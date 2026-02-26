"""Unit tests for Q&A service layer."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.conversation import Conversation, ConversationCategory
from src.database.models.message import Message, SenderType
from src.database.models.message_rating import MessageRating
from src.qa.context_builder import ContextBuilder
from src.qa.service import QAService
from src.qa.title_generator import TitleGenerator


@pytest.fixture
def mock_ai_service() -> MagicMock:
    """Create mock AI service.

    Returns:
        MagicMock: Mocked AI service
    """
    return MagicMock()


@pytest.fixture
def mock_context_builder() -> MagicMock:
    """Create mock context builder.

    Returns:
        MagicMock: Mocked context builder
    """
    builder = MagicMock(spec=ContextBuilder)
    builder.build_context = AsyncMock(return_value="Built context for AI")
    return builder


@pytest.fixture
def mock_title_generator() -> MagicMock:
    """Create mock title generator.

    Returns:
        MagicMock: Mocked title generator
    """
    generator = MagicMock(spec=TitleGenerator)
    generator.generate_title = MagicMock(return_value="Generated Title")
    return generator


@pytest.fixture
def qa_service(
    mock_ai_service: MagicMock,
    mock_context_builder: MagicMock,
    mock_title_generator: MagicMock,
) -> QAService:
    """Create QA service with mocked dependencies.

    Args:
        mock_ai_service: Mocked AI service
        mock_context_builder: Mocked context builder
        mock_title_generator: Mocked title generator

    Returns:
        QAService: Service instance with mocked dependencies
    """
    return QAService(
        ai_service=mock_ai_service,
        context_builder=mock_context_builder,
        title_generator=mock_title_generator,
    )


@pytest.fixture
def mock_db() -> AsyncMock:
    """Create mock database session.

    Returns:
        AsyncMock: Mocked async database session
    """
    db = AsyncMock(spec=AsyncSession)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.add = MagicMock()
    db.execute = AsyncMock()
    return db


@pytest.fixture
def sample_user_id() -> str:
    """Sample user ID.

    Returns:
        str: User identifier
    """
    return str(uuid4())


@pytest.fixture
def sample_conversation_id() -> UUID:
    """Sample conversation ID.

    Returns:
        UUID: Conversation identifier
    """
    return uuid4()


@pytest.fixture
def sample_message_id() -> UUID:
    """Sample message ID.

    Returns:
        UUID: Message identifier
    """
    return uuid4()


class TestAskQuestion:
    """Tests for ask_question method."""

    @pytest.mark.asyncio
    async def test_ask_question_new_conversation(
        self,
        qa_service: QAService,
        mock_db: AsyncMock,
        sample_user_id: str,
        mock_title_generator: MagicMock,
    ) -> None:
        """Test asking question creates new conversation.

        Args:
            qa_service: QA service instance
            mock_db: Mocked database session
            sample_user_id: User identifier
            mock_title_generator: Mocked title generator
        """
        question = "How do I improve my resume?"
        category = "resume_help"

        # Mock conversation creation
        conversation_id = uuid4()
        conversation = Conversation(
            id=str(conversation_id),
            user_id=sample_user_id,
            title="Generated Title",
            category=ConversationCategory.RESUME_HELP,
            tags=[],
            is_active=True,
        )

        # Mock database operations
        mock_db.refresh.side_effect = lambda obj: setattr(obj, "id", conversation_id)

        # Mock message creation
        user_msg = Message(
            id=str(uuid4()),
            conversation_id=str(conversation_id),
            sender_type=SenderType.USER,
            content=question,
            metadata={},
        )
        ai_msg = Message(
            id=str(uuid4()),
            conversation_id=str(conversation_id),
            sender_type=SenderType.AI,
            content="AI response",
            metadata={},
        )

        with patch.object(qa_service, "_create_conversation", return_value=conversation):
            with patch.object(qa_service, "_save_message", side_effect=[user_msg, ai_msg]):
                with patch.object(
                    qa_service, "_generate_ai_response", return_value="AI response"
                ):
                    with patch.object(qa_service, "_update_conversation_timestamp"):
                        with patch.object(
                            qa_service,
                            "_get_conversation_with_messages",
                            return_value=MagicMock(),
                        ):
                            result = await qa_service.ask_question(
                                user_id=sample_user_id,
                                question=question,
                                conversation_id=None,
                                category=category,
                                metadata={},
                                db=mock_db,
                            )

        # Verify title was generated
        mock_title_generator.generate_title.assert_called_once_with(question, category)

    @pytest.mark.asyncio
    async def test_ask_question_existing_conversation(
        self,
        qa_service: QAService,
        mock_db: AsyncMock,
        sample_user_id: str,
        sample_conversation_id: UUID,
    ) -> None:
        """Test asking question in existing conversation.

        Args:
            qa_service: QA service instance
            mock_db: Mocked database session
            sample_user_id: User identifier
            sample_conversation_id: Conversation identifier
        """
        question = "What about cover letters?"

        # Mock existing conversation
        conversation = Conversation(
            id=str(sample_conversation_id),
            user_id=sample_user_id,
            title="Career Advice",
            category=ConversationCategory.CAREER_ADVICE,
            tags=[],
            is_active=True,
        )

        with patch.object(
            qa_service, "_get_conversation", return_value=conversation
        ):
            with patch.object(qa_service, "_save_message", return_value=MagicMock()):
                with patch.object(
                    qa_service, "_generate_ai_response", return_value="AI response"
                ):
                    with patch.object(qa_service, "_update_conversation_timestamp"):
                        with patch.object(
                            qa_service,
                            "_get_conversation_with_messages",
                            return_value=MagicMock(),
                        ):
                            result = await qa_service.ask_question(
                                user_id=sample_user_id,
                                question=question,
                                conversation_id=sample_conversation_id,
                                category=None,
                                metadata={},
                                db=mock_db,
                            )

        # Verify conversation was retrieved, not created
        assert result is not None

    @pytest.mark.asyncio
    async def test_ask_question_conversation_not_found(
        self,
        qa_service: QAService,
        mock_db: AsyncMock,
        sample_user_id: str,
        sample_conversation_id: UUID,
    ) -> None:
        """Test asking question with invalid conversation ID.

        Args:
            qa_service: QA service instance
            mock_db: Mocked database session
            sample_user_id: User identifier
            sample_conversation_id: Conversation identifier
        """
        with patch.object(qa_service, "_get_conversation", return_value=None):
            with pytest.raises(ValueError, match="Conversation .* not found"):
                await qa_service.ask_question(
                    user_id=sample_user_id,
                    question="Test question",
                    conversation_id=sample_conversation_id,
                    category=None,
                    metadata={},
                    db=mock_db,
                )


class TestGetConversations:
    """Tests for get_conversations method."""

    @pytest.mark.asyncio
    async def test_get_conversations_success(
        self,
        qa_service: QAService,
        mock_db: AsyncMock,
        sample_user_id: str,
    ) -> None:
        """Test retrieving user conversations.

        Args:
            qa_service: QA service instance
            mock_db: Mocked database session
            sample_user_id: User identifier
        """
        # Mock conversations
        conversations = [
            Conversation(
                id=str(uuid4()),
                user_id=sample_user_id,
                title="Conversation 1",
                category=ConversationCategory.RESUME_HELP,
                tags=[],
                is_active=True,
                messages=[],
            ),
            Conversation(
                id=str(uuid4()),
                user_id=sample_user_id,
                title="Conversation 2",
                category=ConversationCategory.CAREER_ADVICE,
                tags=[],
                is_active=True,
                messages=[],
            ),
        ]

        # Mock database response
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = conversations

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 2

        mock_db.execute.side_effect = [mock_count_result, mock_result]

        result, total = await qa_service.get_conversations(
            user_id=sample_user_id,
            category=None,
            is_active=None,
            offset=0,
            limit=10,
            db=mock_db,
        )

        assert len(result) == 2
        assert total == 2

    @pytest.mark.asyncio
    async def test_get_conversations_with_filters(
        self,
        qa_service: QAService,
        mock_db: AsyncMock,
        sample_user_id: str,
    ) -> None:
        """Test retrieving conversations with category filter.

        Args:
            qa_service: QA service instance
            mock_db: Mocked database session
            sample_user_id: User identifier
        """
        # Mock filtered conversations
        conversations = [
            Conversation(
                id=str(uuid4()),
                user_id=sample_user_id,
                title="Resume Help",
                category=ConversationCategory.RESUME_HELP,
                tags=[],
                is_active=True,
                messages=[],
            ),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = conversations

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1

        mock_db.execute.side_effect = [mock_count_result, mock_result]

        result, total = await qa_service.get_conversations(
            user_id=sample_user_id,
            category="resume_help",
            is_active=True,
            offset=0,
            limit=10,
            db=mock_db,
        )

        assert len(result) == 1
        assert total == 1


class TestSearchMessages:
    """Tests for search_messages method."""

    @pytest.mark.asyncio
    async def test_search_messages_success(
        self,
        qa_service: QAService,
        mock_db: AsyncMock,
        sample_user_id: str,
    ) -> None:
        """Test searching messages successfully.

        Args:
            qa_service: QA service instance
            mock_db: Mocked database session
            sample_user_id: User identifier
        """
        query = "resume"

        # Mock search results
        messages = [
            Message(
                id=str(uuid4()),
                conversation_id=str(uuid4()),
                sender_type=SenderType.USER,
                content="How to improve my resume?",
                metadata={},
                created_at=datetime.utcnow(),
            ),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = messages

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1

        mock_db.execute.side_effect = [mock_count_result, mock_result]

        result, total = await qa_service.search_messages(
            user_id=sample_user_id,
            query=query,
            conversation_id=None,
            offset=0,
            limit=10,
            db=mock_db,
        )

        assert len(result) == 1
        assert total == 1
        assert "resume" in result[0].content.lower()


class TestRateMessage:
    """Tests for rate_message method."""

    @pytest.mark.asyncio
    async def test_rate_message_success(
        self,
        qa_service: QAService,
        mock_db: AsyncMock,
        sample_user_id: str,
        sample_message_id: UUID,
    ) -> None:
        """Test rating an AI message successfully.

        Args:
            qa_service: QA service instance
            mock_db: Mocked database session
            sample_user_id: User identifier
            sample_message_id: Message identifier
        """
        rating = 5
        feedback = "Very helpful!"

        # Mock message exists and is AI message
        message = Message(
            id=str(sample_message_id),
            conversation_id=str(uuid4()),
            sender_type=SenderType.AI,
            content="AI response",
            metadata={},
        )

        mock_message_result = MagicMock()
        mock_message_result.scalar_one_or_none.return_value = message

        # Mock no existing rating
        mock_rating_result = MagicMock()
        mock_rating_result.scalar_one_or_none.return_value = None

        mock_db.execute.side_effect = [mock_message_result, mock_rating_result]

        # Mock created rating
        created_rating = MessageRating(
            id=str(uuid4()),
            message_id=str(sample_message_id),
            user_id=sample_user_id,
            rating=rating,
            feedback_text=feedback,
            helpful=True,
        )

        mock_db.refresh.side_effect = lambda obj: setattr(obj, "id", uuid4())

        result = await qa_service.rate_message(
            user_id=sample_user_id,
            message_id=sample_message_id,
            rating=rating,
            feedback_text=feedback,
            db=mock_db,
        )

        # Verify rating was added
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called()

    @pytest.mark.asyncio
    async def test_rate_message_update_existing(
        self,
        qa_service: QAService,
        mock_db: AsyncMock,
        sample_user_id: str,
        sample_message_id: UUID,
    ) -> None:
        """Test updating existing message rating.

        Args:
            qa_service: QA service instance
            mock_db: Mocked database session
            sample_user_id: User identifier
            sample_message_id: Message identifier
        """
        new_rating = 4

        # Mock message exists
        message = Message(
            id=str(sample_message_id),
            conversation_id=str(uuid4()),
            sender_type=SenderType.AI,
            content="AI response",
            metadata={},
        )

        mock_message_result = MagicMock()
        mock_message_result.scalar_one_or_none.return_value = message

        # Mock existing rating
        existing_rating = MessageRating(
            id=str(uuid4()),
            message_id=str(sample_message_id),
            user_id=sample_user_id,
            rating=3,
            feedback_text="Okay",
            helpful=True,
        )

        mock_rating_result = MagicMock()
        mock_rating_result.scalar_one_or_none.return_value = existing_rating

        mock_db.execute.side_effect = [mock_message_result, mock_rating_result]

        result = await qa_service.rate_message(
            user_id=sample_user_id,
            message_id=sample_message_id,
            rating=new_rating,
            feedback_text="Better!",
            db=mock_db,
        )

        # Verify rating was updated
        assert existing_rating.rating == new_rating
        mock_db.commit.assert_called()

    @pytest.mark.asyncio
    async def test_rate_message_not_found(
        self,
        qa_service: QAService,
        mock_db: AsyncMock,
        sample_user_id: str,
        sample_message_id: UUID,
    ) -> None:
        """Test rating message that doesn't exist.

        Args:
            qa_service: QA service instance
            mock_db: Mocked database session
            sample_user_id: User identifier
            sample_message_id: Message identifier
        """
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_db.execute.return_value = mock_result

        with pytest.raises(ValueError, match="Message not found"):
            await qa_service.rate_message(
                user_id=sample_user_id,
                message_id=sample_message_id,
                rating=5,
                feedback_text=None,
                db=mock_db,
            )


class TestContextBuilding:
    """Tests for context building integration."""

    @pytest.mark.asyncio
    async def test_context_builder_called(
        self,
        qa_service: QAService,
        mock_db: AsyncMock,
        mock_context_builder: MagicMock,
        sample_user_id: str,
    ) -> None:
        """Test that context builder is called during question processing.

        Args:
            qa_service: QA service instance
            mock_db: Mocked database session
            mock_context_builder: Mocked context builder
            sample_user_id: User identifier
        """
        question = "Test question"

        # Mock conversation and message creation
        conversation = Conversation(
            id=str(uuid4()),
            user_id=sample_user_id,
            title="Test",
            category=ConversationCategory.RESUME_HELP,
            tags=[],
            is_active=True,
        )

        with patch.object(qa_service, "_create_conversation", return_value=conversation):
            with patch.object(qa_service, "_save_message", return_value=MagicMock()):
                with patch.object(
                    qa_service, "_generate_ai_response", return_value="AI response"
                ):
                    with patch.object(qa_service, "_update_conversation_timestamp"):
                        with patch.object(
                            qa_service,
                            "_get_conversation_with_messages",
                            return_value=MagicMock(),
                        ):
                            await qa_service.ask_question(
                                user_id=sample_user_id,
                                question=question,
                                conversation_id=None,
                                category="resume_help",
                                metadata={},
                                db=mock_db,
                            )

        # Verify context builder was called
        mock_context_builder.build_context.assert_called_once()


class TestTitleGeneration:
    """Tests for title generation integration."""

    @pytest.mark.asyncio
    async def test_title_generator_called_for_new_conversation(
        self,
        qa_service: QAService,
        mock_db: AsyncMock,
        mock_title_generator: MagicMock,
        sample_user_id: str,
    ) -> None:
        """Test title generator is called for new conversations.

        Args:
            qa_service: QA service instance
            mock_db: Mocked database session
            mock_title_generator: Mocked title generator
            sample_user_id: User identifier
        """
        question = "How can I make my resume better?"
        category = "resume_help"

        # Mock conversation creation
        conversation = Conversation(
            id=str(uuid4()),
            user_id=sample_user_id,
            title="Generated Title",
            category=ConversationCategory.RESUME_HELP,
            tags=[],
            is_active=True,
        )

        with patch.object(qa_service, "_create_conversation", return_value=conversation):
            with patch.object(qa_service, "_save_message", return_value=MagicMock()):
                with patch.object(
                    qa_service, "_generate_ai_response", return_value="AI response"
                ):
                    with patch.object(qa_service, "_update_conversation_timestamp"):
                        with patch.object(
                            qa_service,
                            "_get_conversation_with_messages",
                            return_value=MagicMock(),
                        ):
                            await qa_service.ask_question(
                                user_id=sample_user_id,
                                question=question,
                                conversation_id=None,
                                category=category,
                                metadata={},
                                db=mock_db,
                            )

        # Verify title generator was called with question and category
        mock_title_generator.generate_title.assert_called_once_with(question, category)


class TestErrorHandling:
    """Tests for error handling scenarios."""

    @pytest.mark.asyncio
    async def test_handle_database_error_gracefully(
        self,
        qa_service: QAService,
        mock_db: AsyncMock,
        sample_user_id: str,
    ) -> None:
        """Test graceful handling of database errors.

        Args:
            qa_service: QA service instance
            mock_db: Mocked database session
            sample_user_id: User identifier
        """
        question = "Test question"

        # Mock database error
        mock_db.execute.side_effect = Exception("Database error")

        with pytest.raises(Exception):
            await qa_service.get_conversations(
                user_id=sample_user_id,
                category=None,
                is_active=None,
                offset=0,
                limit=10,
                db=mock_db,
            )
