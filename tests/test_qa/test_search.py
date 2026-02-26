"""Unit tests for Q&A search functionality."""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.conversation import Conversation, ConversationCategory
from src.database.models.message import Message, SenderType
from src.database.models.user import User
from src.qa.export import ExportService
from src.qa.search import SearchService


class TestSearchService:
    """Test cases for SearchService class."""

    @pytest.mark.asyncio
    async def test_search_messages_success(self):
        """Test successful message search with ranking."""
        # Create mock database session
        db = AsyncMock(spec=AsyncSession)

        # Create test data
        user_id = str(uuid4())
        conversation_id = str(uuid4())

        # Mock search results
        mock_message = Mock(spec=Message)
        mock_message.id = uuid4()
        mock_message.conversation_id = conversation_id
        mock_message.sender_type = SenderType.AI
        mock_message.content = "This is a test message about resumes"
        mock_message.metadata = {}
        mock_message.created_at = datetime.utcnow()

        # Mock database query execution
        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 1

        mock_search_result = Mock()
        mock_search_result.all.return_value = [(mock_message, 0.75)]

        db.execute.side_effect = [mock_count_result, mock_search_result]

        # Create service and perform search
        search_service = SearchService()

        # Mock highlight_matches to return content as-is
        with patch.object(
            search_service,
            "highlight_matches",
            return_value=mock_message.content,
        ):
            messages, total = await search_service.search_messages(
                db=db,
                user_id=user_id,
                query="resume",
                conversation_id=None,
                limit=10,
                offset=0,
            )

        # Verify results
        assert total == 1
        assert len(messages) == 1
        assert messages[0]["id"] == str(mock_message.id)
        assert messages[0]["content"] == mock_message.content
        assert messages[0]["rank"] == 0.75

    @pytest.mark.asyncio
    async def test_search_messages_with_conversation_filter(self):
        """Test message search filtered by conversation."""
        db = AsyncMock(spec=AsyncSession)

        user_id = str(uuid4())
        conversation_id = uuid4()

        # Mock empty results
        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 0

        mock_search_result = Mock()
        mock_search_result.all.return_value = []

        db.execute.side_effect = [mock_count_result, mock_search_result]

        search_service = SearchService()
        messages, total = await search_service.search_messages(
            db=db,
            user_id=user_id,
            query="test",
            conversation_id=conversation_id,
            limit=10,
            offset=0,
        )

        assert total == 0
        assert len(messages) == 0

    @pytest.mark.asyncio
    async def test_search_messages_pagination(self):
        """Test message search with pagination."""
        db = AsyncMock(spec=AsyncSession)

        user_id = str(uuid4())

        # Mock results for page 2
        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 25

        mock_message1 = Mock(spec=Message)
        mock_message1.id = uuid4()
        mock_message1.conversation_id = str(uuid4())
        mock_message1.sender_type = SenderType.USER
        mock_message1.content = "Page 2 message 1"
        mock_message1.metadata = {}
        mock_message1.created_at = datetime.utcnow()

        mock_message2 = Mock(spec=Message)
        mock_message2.id = uuid4()
        mock_message2.conversation_id = str(uuid4())
        mock_message2.sender_type = SenderType.AI
        mock_message2.content = "Page 2 message 2"
        mock_message2.metadata = {}
        mock_message2.created_at = datetime.utcnow()

        mock_search_result = Mock()
        mock_search_result.all.return_value = [
            (mock_message1, 0.8),
            (mock_message2, 0.7),
        ]

        db.execute.side_effect = [mock_count_result, mock_search_result]

        search_service = SearchService()

        with patch.object(
            search_service,
            "highlight_matches",
            side_effect=lambda db, content, query: content,
        ):
            messages, total = await search_service.search_messages(
                db=db,
                user_id=user_id,
                query="test",
                conversation_id=None,
                limit=10,
                offset=10,
            )

        assert total == 25
        assert len(messages) == 2

    @pytest.mark.asyncio
    async def test_rank_results_success(self):
        """Test ranking of search results."""
        db = AsyncMock(spec=AsyncSession)

        # Create test messages
        message1 = Mock(spec=Message)
        message1.id = uuid4()

        message2 = Mock(spec=Message)
        message2.id = uuid4()

        # Mock rank scores
        mock_rank1 = Mock()
        mock_rank1.scalar.return_value = 0.9

        mock_rank2 = Mock()
        mock_rank2.scalar.return_value = 0.6

        db.execute.side_effect = [mock_rank1, mock_rank2]

        search_service = SearchService()
        ranked = await search_service.rank_results(
            db=db,
            messages=[message1, message2],
            query="test query",
        )

        assert len(ranked) == 2
        assert ranked[0][0] == message1
        assert ranked[0][1] == 0.9
        assert ranked[1][0] == message2
        assert ranked[1][1] == 0.6

    @pytest.mark.asyncio
    async def test_highlight_matches_success(self):
        """Test highlighting of search term matches."""
        db = AsyncMock(spec=AsyncSession)

        content = "This is a test message about resume writing"
        query = "resume"

        # Mock highlighted result
        mock_result = Mock()
        mock_result.scalar.return_value = "This is a test message about <mark>resume</mark> writing"

        db.execute.return_value = mock_result

        search_service = SearchService()
        highlighted = await search_service.highlight_matches(
            db=db,
            content=content,
            query=query,
        )

        assert "<mark>resume</mark>" in highlighted

    @pytest.mark.asyncio
    async def test_highlight_matches_fallback_on_error(self):
        """Test that original content is returned when highlighting fails."""
        db = AsyncMock(spec=AsyncSession)

        content = "Original content"
        query = "test"

        # Mock database error
        db.execute.side_effect = Exception("Database error")

        search_service = SearchService()
        highlighted = await search_service.highlight_matches(
            db=db,
            content=content,
            query=query,
        )

        # Should return original content on error
        assert highlighted == content


class TestExportService:
    """Test cases for ExportService class."""

    @pytest.mark.asyncio
    async def test_export_to_json_success(self):
        """Test successful JSON export of conversation."""
        db = AsyncMock(spec=AsyncSession)

        user_id = str(uuid4())
        conversation_id = uuid4()

        # Create mock conversation with messages
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.id = str(conversation_id)
        mock_conversation.user_id = user_id
        mock_conversation.title = "Test Conversation"
        mock_conversation.category = ConversationCategory.RESUME_HELP
        mock_conversation.tags = ["test", "resume"]
        mock_conversation.is_active = True
        mock_conversation.created_at = datetime.utcnow()
        mock_conversation.updated_at = datetime.utcnow()
        mock_conversation.last_message_at = datetime.utcnow()

        # Create mock messages
        mock_message1 = Mock(spec=Message)
        mock_message1.id = uuid4()
        mock_message1.conversation_id = str(conversation_id)
        mock_message1.sender_type = SenderType.USER
        mock_message1.content = "Hello"
        mock_message1.metadata = {}
        mock_message1.created_at = datetime.utcnow()
        mock_message1.updated_at = datetime.utcnow()

        mock_message2 = Mock(spec=Message)
        mock_message2.id = uuid4()
        mock_message2.conversation_id = str(conversation_id)
        mock_message2.sender_type = SenderType.AI
        mock_message2.content = "Hi there!"
        mock_message2.metadata = {}
        mock_message2.created_at = datetime.utcnow()
        mock_message2.updated_at = datetime.utcnow()

        mock_conversation.messages = [mock_message1, mock_message2]

        # Mock database query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_conversation

        db.execute.return_value = mock_result

        # Create service and export
        export_service = ExportService()
        export_data = await export_service.export_to_json(
            db=db,
            conversation_id=conversation_id,
            user_id=user_id,
        )

        # Verify export data
        assert export_data["id"] == str(conversation_id)
        assert export_data["title"] == "Test Conversation"
        assert export_data["category"] == "resume_help"
        assert len(export_data["messages"]) == 2
        assert export_data["messages"][0]["content"] == "Hello"
        assert export_data["messages"][1]["content"] == "Hi there!"

    @pytest.mark.asyncio
    async def test_export_to_json_not_found(self):
        """Test JSON export with non-existent conversation."""
        db = AsyncMock(spec=AsyncSession)

        user_id = str(uuid4())
        conversation_id = uuid4()

        # Mock no conversation found
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None

        db.execute.return_value = mock_result

        export_service = ExportService()

        with pytest.raises(ValueError, match="not found or unauthorized"):
            await export_service.export_to_json(
                db=db,
                conversation_id=conversation_id,
                user_id=user_id,
            )

    @pytest.mark.asyncio
    async def test_export_to_pdf_success(self):
        """Test successful PDF export of conversation."""
        db = AsyncMock(spec=AsyncSession)

        user_id = str(uuid4())
        conversation_id = uuid4()

        # Create mock conversation
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.id = str(conversation_id)
        mock_conversation.user_id = user_id
        mock_conversation.title = "PDF Test"
        mock_conversation.category = ConversationCategory.CAREER_ADVICE
        mock_conversation.created_at = datetime.utcnow()

        # Create mock message
        mock_message = Mock(spec=Message)
        mock_message.id = uuid4()
        mock_message.conversation_id = str(conversation_id)
        mock_message.sender_type = SenderType.USER
        mock_message.content = "Test content"
        mock_message.created_at = datetime.utcnow()

        mock_conversation.messages = [mock_message]

        # Mock database query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_conversation

        db.execute.return_value = mock_result

        # Create service and export
        export_service = ExportService()
        pdf_bytes = await export_service.export_to_pdf(
            db=db,
            conversation_id=conversation_id,
            user_id=user_id,
        )

        # Verify PDF bytes were generated
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    @pytest.mark.asyncio
    async def test_export_multiple_conversations_json(self):
        """Test bulk export of multiple conversations to JSON."""
        db = AsyncMock(spec=AsyncSession)

        user_id = str(uuid4())
        conv_id1 = uuid4()
        conv_id2 = uuid4()

        # Mock conversations
        mock_conv1 = Mock(spec=Conversation)
        mock_conv1.id = str(conv_id1)
        mock_conv1.user_id = user_id
        mock_conv1.title = "Conversation 1"
        mock_conv1.category = ConversationCategory.RESUME_HELP
        mock_conv1.tags = []
        mock_conv1.is_active = True
        mock_conv1.created_at = datetime.utcnow()
        mock_conv1.updated_at = datetime.utcnow()
        mock_conv1.last_message_at = None
        mock_conv1.messages = []

        mock_conv2 = Mock(spec=Conversation)
        mock_conv2.id = str(conv_id2)
        mock_conv2.user_id = user_id
        mock_conv2.title = "Conversation 2"
        mock_conv2.category = ConversationCategory.CAREER_ADVICE
        mock_conv2.tags = []
        mock_conv2.is_active = True
        mock_conv2.created_at = datetime.utcnow()
        mock_conv2.updated_at = datetime.utcnow()
        mock_conv2.last_message_at = None
        mock_conv2.messages = []

        # Mock database queries for each conversation
        mock_result1 = Mock()
        mock_result1.scalar_one_or_none.return_value = mock_conv1

        mock_result2 = Mock()
        mock_result2.scalar_one_or_none.return_value = mock_conv2

        db.execute.side_effect = [mock_result1, mock_result2]

        # Create service and export
        export_service = ExportService()
        export_bytes = await export_service.export_multiple_conversations(
            db=db,
            conversation_ids=[conv_id1, conv_id2],
            user_id=user_id,
            format="json",
        )

        # Verify export
        assert isinstance(export_bytes, bytes)
        assert len(export_bytes) > 0

        # Parse JSON to verify structure
        import json

        export_data = json.loads(export_bytes.decode("utf-8"))
        assert export_data["export_type"] == "bulk"
        assert export_data["format"] == "json"
        assert export_data["conversation_count"] == 2
        assert len(export_data["conversations"]) == 2

    @pytest.mark.asyncio
    async def test_export_multiple_conversations_pdf_not_implemented(self):
        """Test that bulk PDF export raises NotImplementedError."""
        db = AsyncMock(spec=AsyncSession)

        user_id = str(uuid4())
        conversation_ids = [uuid4(), uuid4()]

        export_service = ExportService()

        with pytest.raises(NotImplementedError, match="Bulk PDF export"):
            await export_service.export_multiple_conversations(
                db=db,
                conversation_ids=conversation_ids,
                user_id=user_id,
                format="pdf",
            )

    @pytest.mark.asyncio
    async def test_export_multiple_conversations_invalid_format(self):
        """Test bulk export with invalid format."""
        db = AsyncMock(spec=AsyncSession)

        user_id = str(uuid4())
        conversation_ids = [uuid4()]

        export_service = ExportService()

        with pytest.raises(ValueError, match="Unsupported export format"):
            await export_service.export_multiple_conversations(
                db=db,
                conversation_ids=conversation_ids,
                user_id=user_id,
                format="xml",
            )


class TestSearchPerformance:
    """Performance tests for search functionality."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_search_response_time(self):
        """Test that search completes within acceptable time."""
        import time

        db = AsyncMock(spec=AsyncSession)

        user_id = str(uuid4())

        # Mock quick response
        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 0

        mock_search_result = Mock()
        mock_search_result.all.return_value = []

        db.execute.side_effect = [mock_count_result, mock_search_result]

        search_service = SearchService()

        start_time = time.time()
        await search_service.search_messages(
            db=db,
            user_id=user_id,
            query="performance test",
            conversation_id=None,
            limit=10,
            offset=0,
        )
        elapsed_time = time.time() - start_time

        # Search should complete in under 1 second
        assert elapsed_time < 1.0

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_export_pdf_response_time(self):
        """Test that PDF export completes within acceptable time."""
        import time

        db = AsyncMock(spec=AsyncSession)

        user_id = str(uuid4())
        conversation_id = uuid4()

        # Create minimal mock conversation
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.id = str(conversation_id)
        mock_conversation.user_id = user_id
        mock_conversation.title = "Performance Test"
        mock_conversation.category = ConversationCategory.RESUME_HELP
        mock_conversation.created_at = datetime.utcnow()
        mock_conversation.messages = []

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_conversation

        db.execute.return_value = mock_result

        export_service = ExportService()

        start_time = time.time()
        await export_service.export_to_pdf(
            db=db,
            conversation_id=conversation_id,
            user_id=user_id,
        )
        elapsed_time = time.time() - start_time

        # PDF generation should complete in under 2 seconds
        assert elapsed_time < 2.0
