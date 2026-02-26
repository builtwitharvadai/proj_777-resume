"""Context builder for AI responses using user documents and conversation history."""

import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.message import Message
from src.database.models.parsed_document import ParsedDocument

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Build context for AI responses from documents and conversation history.

    Combines user document content, conversation history, and current question
    into a comprehensive context for AI prompt generation. Includes relevance
    filtering and token management to stay within model limits.

    Attributes:
        max_context_tokens: Maximum tokens to use for context
        max_history_messages: Maximum number of conversation messages to include
        max_document_length: Maximum length of document content to include
    """

    def __init__(
        self,
        max_context_tokens: int = 4000,
        max_history_messages: int = 10,
        max_document_length: int = 5000,
    ) -> None:
        """Initialize ContextBuilder.

        Args:
            max_context_tokens: Maximum tokens for total context
            max_history_messages: Maximum conversation messages to include
            max_document_length: Maximum document content length in characters
        """
        self.max_context_tokens = max_context_tokens
        self.max_history_messages = max_history_messages
        self.max_document_length = max_document_length

        logger.info(
            f"ContextBuilder initialized with max_tokens: {max_context_tokens}, "
            f"max_history: {max_history_messages}, "
            f"max_doc_length: {max_document_length}"
        )

    async def build_context(
        self,
        user_id: str,
        question: str,
        conversation_id: Optional[str],
        db: AsyncSession,
    ) -> str:
        """Build comprehensive context for AI response generation.

        Combines user documents, conversation history, and current question
        into a single context string, applying relevance filtering and
        token management.

        Args:
            user_id: User identifier
            question: Current user question
            conversation_id: Optional conversation ID for history
            db: Database session

        Returns:
            str: Complete context string for AI prompt
        """
        logger.info(
            f"Building context for user {user_id}, "
            f"conversation: {conversation_id}, "
            f"question length: {len(question)}"
        )

        context_parts = []

        # Add document context
        document_context = await self._get_document_context(user_id, question, db)
        if document_context:
            context_parts.append(document_context)
            logger.debug(
                f"Added document context: {len(document_context)} characters"
            )

        # Add conversation history
        if conversation_id:
            history_context = await self._get_conversation_history(
                conversation_id, db
            )
            if history_context:
                context_parts.append(history_context)
                logger.debug(
                    f"Added conversation history: {len(history_context)} characters"
                )

        # Add current question
        question_context = f"\n\nCurrent Question:\n{question}"
        context_parts.append(question_context)

        # Combine all parts
        full_context = "\n\n---\n\n".join(context_parts)

        # Apply token management
        managed_context = self._manage_token_limit(full_context)

        logger.info(
            f"Context built successfully: {len(managed_context)} characters, "
            f"estimated {self._estimate_tokens(managed_context)} tokens"
        )

        return managed_context

    async def _get_document_context(
        self,
        user_id: str,
        question: str,
        db: AsyncSession,
    ) -> str:
        """Extract relevant document content for context.

        Retrieves user's parsed documents and extracts relevant sections
        based on the question topic.

        Args:
            user_id: User identifier
            question: User's question for relevance filtering
            db: Database session

        Returns:
            str: Formatted document context
        """
        logger.debug(f"Retrieving document context for user {user_id}")

        # Query user's parsed documents
        query = (
            select(ParsedDocument)
            .join(ParsedDocument.document)
            .where(ParsedDocument.document.has(user_id=user_id))
            .where(ParsedDocument.parsing_status == "completed")
            .order_by(ParsedDocument.parsed_at.desc())
            .limit(5)
        )

        result = await db.execute(query)
        parsed_docs = result.scalars().all()

        if not parsed_docs:
            logger.debug("No parsed documents found for user")
            return ""

        # Build document context
        doc_parts = ["User Documents Context:"]

        for doc in parsed_docs:
            # Extract relevant sections
            doc_content = []

            # Add raw text (truncated)
            if doc.raw_text:
                truncated_text = doc.raw_text[: self.max_document_length]
                doc_content.append(f"Content: {truncated_text}")

            # Add structured data if relevant
            if doc.work_experience and self._is_relevant_to_question(
                "work experience", question
            ):
                doc_content.append(f"Work Experience: {doc.work_experience}")

            if doc.education and self._is_relevant_to_question("education", question):
                doc_content.append(f"Education: {doc.education}")

            if doc.skills and self._is_relevant_to_question("skills", question):
                doc_content.append(f"Skills: {doc.skills}")

            if doc.contact_info:
                doc_content.append(f"Contact Info: {doc.contact_info}")

            if doc_content:
                doc_parts.append("\n".join(doc_content))

        if len(doc_parts) > 1:
            return "\n\n".join(doc_parts)

        return ""

    async def _get_conversation_history(
        self,
        conversation_id: str,
        db: AsyncSession,
    ) -> str:
        """Retrieve recent conversation history for context.

        Args:
            conversation_id: Conversation identifier
            db: Database session

        Returns:
            str: Formatted conversation history
        """
        logger.debug(f"Retrieving conversation history for {conversation_id}")

        # Query recent messages in conversation
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(self.max_history_messages)
        )

        result = await db.execute(query)
        messages = list(reversed(result.scalars().all()))

        if not messages:
            logger.debug("No messages found in conversation")
            return ""

        # Format conversation history
        history_parts = ["Conversation History:"]

        for msg in messages:
            sender = "User" if msg.sender_type == "user" else "Assistant"
            history_parts.append(f"{sender}: {msg.content}")

        return "\n".join(history_parts)

    def _is_relevant_to_question(self, topic: str, question: str) -> bool:
        """Check if a topic is relevant to the question.

        Simple keyword matching for relevance filtering. In production,
        could be enhanced with semantic similarity.

        Args:
            topic: Topic to check (e.g., "work experience", "education")
            question: User's question

        Returns:
            bool: True if topic is relevant
        """
        question_lower = question.lower()
        topic_lower = topic.lower()

        # Simple keyword matching
        keywords = topic_lower.split()
        return any(keyword in question_lower for keyword in keywords)

    def _manage_token_limit(self, context: str) -> str:
        """Ensure context stays within token limits.

        Truncates context if it exceeds the maximum token limit,
        preserving the most recent and relevant information.

        Args:
            context: Full context string

        Returns:
            str: Token-managed context
        """
        estimated_tokens = self._estimate_tokens(context)

        if estimated_tokens <= self.max_context_tokens:
            return context

        logger.warning(
            f"Context exceeds token limit ({estimated_tokens} > "
            f"{self.max_context_tokens}), truncating"
        )

        # Calculate target character count
        # Rough estimate: 1 token ≈ 4 characters
        target_chars = self.max_context_tokens * 4

        # Truncate from the middle (keep beginning and end)
        if len(context) > target_chars:
            # Keep first 60% and last 40% of target
            start_chars = int(target_chars * 0.6)
            end_chars = int(target_chars * 0.4)

            truncated = (
                context[:start_chars]
                + f"\n\n[... content truncated for brevity ...]\n\n"
                + context[-end_chars:]
            )

            logger.info(
                f"Context truncated from {len(context)} to {len(truncated)} characters"
            )
            return truncated

        return context

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text.

        Uses simple heuristic: 1 token ≈ 4 characters.

        Args:
            text: Text to estimate tokens for

        Returns:
            int: Estimated token count
        """
        return len(text) // 4
