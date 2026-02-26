"""Main Q&A service orchestrating conversations, AI responses, and persistence."""

import logging
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.ai.service import AIService
from src.database.models.conversation import Conversation, ConversationCategory
from src.database.models.message import Message, SenderType
from src.database.models.message_rating import MessageRating
from src.qa.context_builder import ContextBuilder
from src.qa.schemas import ConversationResponse, MessageResponse
from src.qa.title_generator import TitleGenerator

logger = logging.getLogger(__name__)


class QAService:
    """Q&A service orchestrating conversation management and AI responses.

    Handles conversation creation, message persistence, AI response generation,
    context building, and automatic title generation for conversations.

    Attributes:
        ai_service: AI service for generating responses
        context_builder: Context builder for AI prompts
        title_generator: Title generator for conversations
    """

    def __init__(
        self,
        ai_service: Optional[AIService] = None,
        context_builder: Optional[ContextBuilder] = None,
        title_generator: Optional[TitleGenerator] = None,
    ) -> None:
        """Initialize QAService.

        Args:
            ai_service: Optional AI service instance
            context_builder: Optional context builder instance
            title_generator: Optional title generator instance
        """
        self.ai_service = ai_service or AIService()
        self.context_builder = context_builder or ContextBuilder()
        self.title_generator = title_generator or TitleGenerator()

        logger.info("QAService initialized with AI, context builder, and title generator")

    async def ask_question(
        self,
        user_id: str,
        question: str,
        conversation_id: Optional[UUID],
        category: Optional[str],
        metadata: Optional[dict],
        db: AsyncSession,
    ) -> ConversationResponse:
        """Process user question and generate AI response.

        Orchestrates conversation creation/continuation, context building,
        AI response generation, and message persistence.

        Args:
            user_id: User identifier
            question: User's question text
            conversation_id: Optional conversation ID to continue
            category: Optional conversation category
            metadata: Optional question metadata
            db: Database session

        Returns:
            ConversationResponse: Conversation with messages including AI response

        Raises:
            ValueError: If conversation not found or user mismatch
        """
        logger.info(
            f"Processing question for user {user_id}, "
            f"conversation: {conversation_id}, category: {category}"
        )

        # Get or create conversation
        if conversation_id:
            conversation = await self._get_conversation(
                conversation_id, user_id, db
            )
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")
        else:
            # Generate title from question
            title = self.title_generator.generate_title(question, category)
            conversation = await self._create_conversation(
                user_id, title, category or "resume_help", db
            )

        # Save user message
        user_message = await self._save_message(
            conversation_id=str(conversation.id),
            sender_type=SenderType.USER,
            content=question,
            metadata=metadata or {},
            db=db,
        )

        logger.debug(f"User message saved: {user_message.id}")

        # Build context for AI
        context = await self.context_builder.build_context(
            user_id=user_id,
            question=question,
            conversation_id=str(conversation.id),
            db=db,
        )

        # Generate AI response
        ai_response = await self._generate_ai_response(
            context=context,
            user_id=user_id,
            db=db,
        )

        # Save AI message
        ai_message = await self._save_message(
            conversation_id=str(conversation.id),
            sender_type=SenderType.AI,
            content=ai_response,
            metadata={},
            db=db,
        )

        logger.debug(f"AI message saved: {ai_message.id}")

        # Update conversation last_message_at
        await self._update_conversation_timestamp(conversation.id, db)

        # Return conversation with messages
        return await self._get_conversation_with_messages(
            conversation.id, db
        )

    async def get_conversations(
        self,
        user_id: str,
        category: Optional[str],
        is_active: Optional[bool],
        offset: int,
        limit: int,
        db: AsyncSession,
    ) -> Tuple[List[ConversationResponse], int]:
        """Retrieve user's conversations with filtering and pagination.

        Args:
            user_id: User identifier
            category: Optional category filter
            is_active: Optional active status filter
            offset: Pagination offset
            limit: Pagination limit
            db: Database session

        Returns:
            Tuple[List[ConversationResponse], int]: Conversations and total count
        """
        logger.info(
            f"Retrieving conversations for user {user_id}, "
            f"category: {category}, offset: {offset}, limit: {limit}"
        )

        # Build query
        query = select(Conversation).where(Conversation.user_id == user_id)

        if category:
            query = query.where(Conversation.category == category)

        if is_active is not None:
            query = query.where(Conversation.is_active == is_active)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = (
            query.order_by(Conversation.last_message_at.desc().nullslast())
            .offset(offset)
            .limit(limit)
            .options(selectinload(Conversation.messages))
        )

        result = await db.execute(query)
        conversations = result.scalars().all()

        logger.info(f"Retrieved {len(conversations)} conversations (total: {total})")

        # Convert to response schemas
        conversation_responses = [
            await self._conversation_to_response(conv)
            for conv in conversations
        ]

        return conversation_responses, total

    async def search_messages(
        self,
        user_id: str,
        query: str,
        conversation_id: Optional[UUID],
        offset: int,
        limit: int,
        db: AsyncSession,
    ) -> Tuple[List[MessageResponse], int]:
        """Search messages using full-text search.

        Args:
            user_id: User identifier
            query: Search query text
            conversation_id: Optional conversation ID to limit search
            offset: Pagination offset
            limit: Pagination limit
            db: Database session

        Returns:
            Tuple[List[MessageResponse], int]: Messages and total count
        """
        logger.info(
            f"Searching messages for user {user_id}, "
            f"query: {query}, conversation: {conversation_id}"
        )

        # Build base query with user filter
        base_query = (
            select(Message)
            .join(Conversation)
            .where(Conversation.user_id == user_id)
        )

        # Add conversation filter if specified
        if conversation_id:
            base_query = base_query.where(Message.conversation_id == str(conversation_id))

        # Add text search filter (simple LIKE for compatibility)
        # In production with PostgreSQL, use ts_query for full-text search
        search_filter = Message.content.ilike(f"%{query}%")
        search_query = base_query.where(search_filter)

        # Get total count
        count_query = select(func.count()).select_from(search_query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        search_query = (
            search_query.order_by(Message.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await db.execute(search_query)
        messages = result.scalars().all()

        logger.info(f"Found {len(messages)} messages (total: {total})")

        # Convert to response schemas
        message_responses = [
            MessageResponse(
                id=msg.id,
                conversation_id=UUID(msg.conversation_id),
                sender_type=msg.sender_type.value,
                content=msg.content,
                metadata=msg.metadata,
                created_at=msg.created_at,
            )
            for msg in messages
        ]

        return message_responses, total

    async def rate_message(
        self,
        user_id: str,
        message_id: UUID,
        rating: int,
        feedback_text: Optional[str],
        db: AsyncSession,
    ) -> MessageRating:
        """Rate an AI message.

        Args:
            user_id: User identifier
            message_id: Message UUID to rate
            rating: Rating value (1-5)
            feedback_text: Optional feedback text
            db: Database session

        Returns:
            MessageRating: Created or updated rating

        Raises:
            ValueError: If message not found or not an AI message
        """
        logger.info(
            f"Rating message {message_id} by user {user_id}, "
            f"rating: {rating}"
        )

        # Verify message exists and is an AI message
        query = (
            select(Message)
            .join(Conversation)
            .where(
                and_(
                    Message.id == str(message_id),
                    Conversation.user_id == user_id,
                    Message.sender_type == SenderType.AI,
                )
            )
        )

        result = await db.execute(query)
        message = result.scalar_one_or_none()

        if not message:
            raise ValueError("Message not found or not an AI message")

        # Check if rating already exists
        existing_query = select(MessageRating).where(
            and_(
                MessageRating.message_id == str(message_id),
                MessageRating.user_id == user_id,
            )
        )

        existing_result = await db.execute(existing_query)
        existing_rating = existing_result.scalar_one_or_none()

        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating
            existing_rating.feedback_text = feedback_text
            existing_rating.is_helpful = rating >= 3
            await db.commit()
            await db.refresh(existing_rating)
            logger.info(f"Updated rating {existing_rating.id}")
            return existing_rating
        else:
            # Create new rating
            new_rating = MessageRating(
                message_id=str(message_id),
                user_id=user_id,
                rating=rating,
                feedback_text=feedback_text,
                is_helpful=rating >= 3,
            )
            db.add(new_rating)
            await db.commit()
            await db.refresh(new_rating)
            logger.info(f"Created rating {new_rating.id}")
            return new_rating

    async def _get_conversation(
        self,
        conversation_id: UUID,
        user_id: str,
        db: AsyncSession,
    ) -> Optional[Conversation]:
        """Get conversation by ID and verify user ownership.

        Args:
            conversation_id: Conversation UUID
            user_id: User identifier
            db: Database session

        Returns:
            Optional[Conversation]: Conversation if found and owned by user
        """
        query = select(Conversation).where(
            and_(
                Conversation.id == str(conversation_id),
                Conversation.user_id == user_id,
            )
        )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def _create_conversation(
        self,
        user_id: str,
        title: str,
        category: str,
        db: AsyncSession,
    ) -> Conversation:
        """Create new conversation.

        Args:
            user_id: User identifier
            title: Conversation title
            category: Conversation category
            db: Database session

        Returns:
            Conversation: Created conversation
        """
        logger.info(
            f"Creating conversation for user {user_id}, "
            f"title: {title}, category: {category}"
        )

        conversation = Conversation(
            user_id=user_id,
            title=title,
            category=ConversationCategory(category),
            tags=[],
            is_active=True,
        )

        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

        logger.info(f"Created conversation: {conversation.id}")
        return conversation

    async def _save_message(
        self,
        conversation_id: str,
        sender_type: SenderType,
        content: str,
        metadata: dict,
        db: AsyncSession,
    ) -> Message:
        """Save message to database.

        Args:
            conversation_id: Conversation UUID
            sender_type: Message sender type
            content: Message content
            metadata: Message metadata
            db: Database session

        Returns:
            Message: Created message
        """
        message = Message(
            conversation_id=conversation_id,
            sender_type=sender_type,
            content=content,
            metadata=metadata,
        )

        db.add(message)
        await db.commit()
        await db.refresh(message)

        return message

    async def _generate_ai_response(
        self,
        context: str,
        user_id: str,
        db: AsyncSession,
    ) -> str:
        """Generate AI response using context.

        Args:
            context: Built context for AI prompt
            user_id: User identifier
            db: Database session

        Returns:
            str: Generated AI response

        Raises:
            AIException: If AI generation fails
        """
        logger.info(f"Generating AI response for user {user_id}")

        # Build prompt with context
        prompt = f"""You are a helpful career advisor and resume expert.
Use the following context to provide accurate, personalized advice to the user's question.

{context}

Provide a helpful, accurate, and professional response."""

        # Call AI service (mock for now - in production use actual AI)
        # For now, return a simple response based on context
        response = (
            f"Based on your information and question, here's my advice:\n\n"
            f"[AI-generated response would appear here based on the context]\n\n"
            f"Context length: {len(context)} characters"
        )

        logger.info(f"AI response generated: {len(response)} characters")
        return response

    async def _update_conversation_timestamp(
        self,
        conversation_id: UUID,
        db: AsyncSession,
    ) -> None:
        """Update conversation's last_message_at timestamp.

        Args:
            conversation_id: Conversation UUID
            db: Database session
        """
        query = select(Conversation).where(Conversation.id == str(conversation_id))
        result = await db.execute(query)
        conversation = result.scalar_one_or_none()

        if conversation:
            conversation.last_message_at = datetime.utcnow()
            await db.commit()

    async def _get_conversation_with_messages(
        self,
        conversation_id: UUID,
        db: AsyncSession,
    ) -> ConversationResponse:
        """Get conversation with all messages.

        Args:
            conversation_id: Conversation UUID
            db: Database session

        Returns:
            ConversationResponse: Conversation with messages
        """
        query = (
            select(Conversation)
            .where(Conversation.id == str(conversation_id))
            .options(selectinload(Conversation.messages))
        )

        result = await db.execute(query)
        conversation = result.scalar_one()

        return await self._conversation_to_response(conversation)

    async def _conversation_to_response(
        self,
        conversation: Conversation,
    ) -> ConversationResponse:
        """Convert conversation to response schema.

        Args:
            conversation: Conversation model

        Returns:
            ConversationResponse: Response schema
        """
        messages = [
            MessageResponse(
                id=msg.id,
                conversation_id=UUID(msg.conversation_id),
                sender_type=msg.sender_type.value,
                content=msg.content,
                metadata=msg.metadata,
                created_at=msg.created_at,
            )
            for msg in sorted(conversation.messages, key=lambda m: m.created_at)
        ]

        return ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            category=conversation.category.value,
            tags=conversation.tags or [],
            is_active=conversation.is_active,
            last_message_at=conversation.last_message_at,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=messages,
        )
