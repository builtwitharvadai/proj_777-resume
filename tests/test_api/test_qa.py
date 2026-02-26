"""Integration tests for Q&A API endpoints."""

from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from src.database.models.conversation import Conversation, ConversationCategory
from src.database.models.message import Message, SenderType
from src.database.models.message_rating import MessageRating
from src.main import create_app
from src.qa.schemas import ConversationResponse, MessageResponse


@pytest.fixture
def app() -> Any:
    """Create test application instance.

    Returns:
        FastAPI application instance
    """
    return create_app()


@pytest.fixture
def client(app: Any) -> TestClient:
    """Create test client.

    Args:
        app: FastAPI application instance

    Returns:
        Test client instance
    """
    return TestClient(app)


@pytest.fixture
def mock_user() -> Dict[str, Any]:
    """Mock authenticated user data.

    Returns:
        Dict with user information
    """
    user_id = uuid4()
    return {
        "id": user_id,
        "email": "test@example.com",
        "email_verified": True,
    }


@pytest.fixture
def mock_conversation(mock_user: Dict[str, Any]) -> Conversation:
    """Create mock conversation instance.

    Args:
        mock_user: Mock user data

    Returns:
        Mock conversation object
    """
    conv = Conversation(
        user_id=str(mock_user["id"]),
        title="Test Conversation",
        category=ConversationCategory.RESUME_HELP,
        tags=["resume", "cv"],
        is_active=True,
    )
    conv.id = uuid4()
    conv.created_at = datetime.utcnow()
    conv.updated_at = datetime.utcnow()
    conv.last_message_at = datetime.utcnow()
    return conv


@pytest.fixture
def mock_message(mock_conversation: Conversation) -> Message:
    """Create mock message instance.

    Args:
        mock_conversation: Mock conversation

    Returns:
        Mock message object
    """
    msg = Message(
        conversation_id=str(mock_conversation.id),
        sender_type=SenderType.AI,
        content="This is a test AI response",
        metadata={},
    )
    msg.id = uuid4()
    msg.created_at = datetime.utcnow()
    return msg


@pytest.fixture
def mock_conversation_response(
    mock_conversation: Conversation, mock_message: Message
) -> ConversationResponse:
    """Create mock conversation response.

    Args:
        mock_conversation: Mock conversation
        mock_message: Mock message

    Returns:
        Mock conversation response
    """
    return ConversationResponse(
        id=mock_conversation.id,
        user_id=mock_conversation.user_id,
        title=mock_conversation.title,
        category=mock_conversation.category.value,
        tags=mock_conversation.tags,
        is_active=mock_conversation.is_active,
        last_message_at=mock_conversation.last_message_at,
        created_at=mock_conversation.created_at,
        updated_at=mock_conversation.updated_at,
        messages=[
            MessageResponse(
                id=mock_message.id,
                conversation_id=UUID(mock_message.conversation_id),
                sender_type=mock_message.sender_type.value,
                content=mock_message.content,
                metadata=mock_message.metadata,
                created_at=mock_message.created_at,
            )
        ],
    )


class TestAskQuestionEndpoint:
    """Tests for ask question endpoint."""

    @patch("src.api.qa.get_current_verified_user")
    @patch("src.api.qa.get_qa_service")
    @patch("src.api.qa.limiter.limit")
    def test_ask_question_success(
        self,
        mock_limiter: Any,
        mock_get_service: Any,
        mock_get_user: Any,
        client: TestClient,
        mock_user: Dict[str, Any],
        mock_conversation_response: ConversationResponse,
    ) -> None:
        """Test successful question submission.

        Args:
            mock_limiter: Mock rate limiter
            mock_get_service: Mock Q&A service
            mock_get_user: Mock user dependency
            client: Test client
            mock_user: Mock user data
            mock_conversation_response: Mock conversation response
        """
        # Setup mocks
        mock_limiter.return_value = lambda f: f
        mock_user_obj = MagicMock()
        mock_user_obj.id = mock_user["id"]
        mock_user_obj.email = mock_user["email"]
        mock_user_obj.email_verified = mock_user["email_verified"]
        mock_get_user.return_value = mock_user_obj

        mock_service = MagicMock()
        mock_service.ask_question = AsyncMock(return_value=mock_conversation_response)
        mock_get_service.return_value = mock_service

        # Make request
        response = client.post(
            "/api/qa/ask",
            json={
                "question": "How do I improve my resume?",
                "category": "resume_help",
                "metadata": {},
            },
        )

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "title" in data
        assert "messages" in data
        assert len(data["messages"]) > 0

    @patch("src.api.qa.get_current_verified_user")
    @patch("src.api.qa.get_qa_service")
    @patch("src.api.qa.limiter.limit")
    def test_ask_question_continue_conversation(
        self,
        mock_limiter: Any,
        mock_get_service: Any,
        mock_get_user: Any,
        client: TestClient,
        mock_user: Dict[str, Any],
        mock_conversation_response: ConversationResponse,
    ) -> None:
        """Test continuing existing conversation.

        Args:
            mock_limiter: Mock rate limiter
            mock_get_service: Mock Q&A service
            mock_get_user: Mock user dependency
            client: Test client
            mock_user: Mock user data
            mock_conversation_response: Mock conversation response
        """
        # Setup mocks
        mock_limiter.return_value = lambda f: f
        mock_user_obj = MagicMock()
        mock_user_obj.id = mock_user["id"]
        mock_user_obj.email = mock_user["email"]
        mock_user_obj.email_verified = mock_user["email_verified"]
        mock_get_user.return_value = mock_user_obj

        mock_service = MagicMock()
        mock_service.ask_question = AsyncMock(return_value=mock_conversation_response)
        mock_get_service.return_value = mock_service

        conversation_id = str(uuid4())

        # Make request
        response = client.post(
            "/api/qa/ask",
            json={
                "question": "Can you elaborate on that?",
                "conversation_id": conversation_id,
            },
        )

        # Assertions
        assert response.status_code == status.HTTP_200_OK

    @patch("src.api.qa.get_current_verified_user")
    @patch("src.api.qa.get_qa_service")
    @patch("src.api.qa.limiter.limit")
    def test_ask_question_conversation_not_found(
        self,
        mock_limiter: Any,
        mock_get_service: Any,
        mock_get_user: Any,
        client: TestClient,
        mock_user: Dict[str, Any],
    ) -> None:
        """Test error when conversation not found.

        Args:
            mock_limiter: Mock rate limiter
            mock_get_service: Mock Q&A service
            mock_get_user: Mock user dependency
            client: Test client
            mock_user: Mock user data
        """
        # Setup mocks
        mock_limiter.return_value = lambda f: f
        mock_user_obj = MagicMock()
        mock_user_obj.id = mock_user["id"]
        mock_user_obj.email = mock_user["email"]
        mock_user_obj.email_verified = mock_user["email_verified"]
        mock_get_user.return_value = mock_user_obj

        mock_service = MagicMock()
        mock_service.ask_question = AsyncMock(
            side_effect=ValueError("Conversation not found")
        )
        mock_get_service.return_value = mock_service

        # Make request
        response = client.post(
            "/api/qa/ask",
            json={
                "question": "Test question",
                "conversation_id": str(uuid4()),
            },
        )

        # Assertions
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_ask_question_without_authentication(
        self,
        client: TestClient,
    ) -> None:
        """Test error when not authenticated.

        Args:
            client: Test client
        """
        response = client.post(
            "/api/qa/ask",
            json={
                "question": "Test question",
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("src.api.qa.get_current_verified_user")
    @patch("src.api.qa.limiter.limit")
    def test_ask_question_empty_question(
        self,
        mock_limiter: Any,
        mock_get_user: Any,
        client: TestClient,
        mock_user: Dict[str, Any],
    ) -> None:
        """Test validation error for empty question.

        Args:
            mock_limiter: Mock rate limiter
            mock_get_user: Mock user dependency
            client: Test client
            mock_user: Mock user data
        """
        mock_limiter.return_value = lambda f: f
        mock_user_obj = MagicMock()
        mock_user_obj.id = mock_user["id"]
        mock_user_obj.email = mock_user["email"]
        mock_user_obj.email_verified = mock_user["email_verified"]
        mock_get_user.return_value = mock_user_obj

        response = client.post(
            "/api/qa/ask",
            json={
                "question": "   ",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetConversationsEndpoint:
    """Tests for get conversations endpoint."""

    @patch("src.api.qa.get_current_verified_user")
    @patch("src.api.qa.get_qa_service")
    def test_get_conversations_success(
        self,
        mock_get_service: Any,
        mock_get_user: Any,
        client: TestClient,
        mock_user: Dict[str, Any],
        mock_conversation_response: ConversationResponse,
    ) -> None:
        """Test successful conversations retrieval.

        Args:
            mock_get_service: Mock Q&A service
            mock_get_user: Mock user dependency
            client: Test client
            mock_user: Mock user data
            mock_conversation_response: Mock conversation response
        """
        mock_user_obj = MagicMock()
        mock_user_obj.id = mock_user["id"]
        mock_user_obj.email = mock_user["email"]
        mock_user_obj.email_verified = mock_user["email_verified"]
        mock_get_user.return_value = mock_user_obj

        mock_service = MagicMock()
        mock_service.get_conversations = AsyncMock(
            return_value=([mock_conversation_response], 1)
        )
        mock_get_service.return_value = mock_service

        response = client.get("/api/qa/conversations")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "conversations" in data
        assert "total" in data
        assert "offset" in data
        assert "limit" in data
        assert data["total"] == 1
        assert len(data["conversations"]) == 1

    @patch("src.api.qa.get_current_verified_user")
    @patch("src.api.qa.get_qa_service")
    def test_get_conversations_with_filters(
        self,
        mock_get_service: Any,
        mock_get_user: Any,
        client: TestClient,
        mock_user: Dict[str, Any],
        mock_conversation_response: ConversationResponse,
    ) -> None:
        """Test conversations retrieval with filters.

        Args:
            mock_get_service: Mock Q&A service
            mock_get_user: Mock user dependency
            client: Test client
            mock_user: Mock user data
            mock_conversation_response: Mock conversation response
        """
        mock_user_obj = MagicMock()
        mock_user_obj.id = mock_user["id"]
        mock_user_obj.email = mock_user["email"]
        mock_user_obj.email_verified = mock_user["email_verified"]
        mock_get_user.return_value = mock_user_obj

        mock_service = MagicMock()
        mock_service.get_conversations = AsyncMock(
            return_value=([mock_conversation_response], 1)
        )
        mock_get_service.return_value = mock_service

        response = client.get(
            "/api/qa/conversations",
            params={
                "category": "resume_help",
                "is_active": True,
                "offset": 0,
                "limit": 10,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1

    @patch("src.api.qa.get_current_verified_user")
    @patch("src.api.qa.get_qa_service")
    def test_get_conversations_pagination(
        self,
        mock_get_service: Any,
        mock_get_user: Any,
        client: TestClient,
        mock_user: Dict[str, Any],
    ) -> None:
        """Test conversations pagination.

        Args:
            mock_get_service: Mock Q&A service
            mock_get_user: Mock user dependency
            client: Test client
            mock_user: Mock user data
        """
        mock_user_obj = MagicMock()
        mock_user_obj.id = mock_user["id"]
        mock_user_obj.email = mock_user["email"]
        mock_user_obj.email_verified = mock_user["email_verified"]
        mock_get_user.return_value = mock_user_obj

        mock_service = MagicMock()
        mock_service.get_conversations = AsyncMock(return_value=([], 0))
        mock_get_service.return_value = mock_service

        response = client.get(
            "/api/qa/conversations",
            params={"offset": 10, "limit": 20},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["offset"] == 10
        assert data["limit"] == 20

    def test_get_conversations_without_authentication(
        self,
        client: TestClient,
    ) -> None:
        """Test error when not authenticated.

        Args:
            client: Test client
        """
        response = client.get("/api/qa/conversations")

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestSearchMessagesEndpoint:
    """Tests for search messages endpoint."""

    @patch("src.api.qa.get_current_verified_user")
    @patch("src.api.qa.get_qa_service")
    def test_search_messages_success(
        self,
        mock_get_service: Any,
        mock_get_user: Any,
        client: TestClient,
        mock_user: Dict[str, Any],
        mock_message: Message,
    ) -> None:
        """Test successful message search.

        Args:
            mock_get_service: Mock Q&A service
            mock_get_user: Mock user dependency
            client: Test client
            mock_user: Mock user data
            mock_message: Mock message
        """
        mock_user_obj = MagicMock()
        mock_user_obj.id = mock_user["id"]
        mock_user_obj.email = mock_user["email"]
        mock_user_obj.email_verified = mock_user["email_verified"]
        mock_get_user.return_value = mock_user_obj

        mock_message_response = MessageResponse(
            id=mock_message.id,
            conversation_id=UUID(mock_message.conversation_id),
            sender_type=mock_message.sender_type.value,
            content=mock_message.content,
            metadata=mock_message.metadata,
            created_at=mock_message.created_at,
        )

        mock_service = MagicMock()
        mock_service.search_messages = AsyncMock(
            return_value=([mock_message_response], 1)
        )
        mock_get_service.return_value = mock_service

        response = client.post(
            "/api/qa/search",
            json={
                "query": "resume",
                "limit": 10,
                "offset": 0,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "messages" in data
        assert "total" in data
        assert data["total"] == 1
        assert len(data["messages"]) == 1

    @patch("src.api.qa.get_current_verified_user")
    @patch("src.api.qa.get_qa_service")
    def test_search_messages_with_conversation_filter(
        self,
        mock_get_service: Any,
        mock_get_user: Any,
        client: TestClient,
        mock_user: Dict[str, Any],
    ) -> None:
        """Test message search with conversation filter.

        Args:
            mock_get_service: Mock Q&A service
            mock_get_user: Mock user dependency
            client: Test client
            mock_user: Mock user data
        """
        mock_user_obj = MagicMock()
        mock_user_obj.id = mock_user["id"]
        mock_user_obj.email = mock_user["email"]
        mock_user_obj.email_verified = mock_user["email_verified"]
        mock_get_user.return_value = mock_user_obj

        mock_service = MagicMock()
        mock_service.search_messages = AsyncMock(return_value=([], 0))
        mock_get_service.return_value = mock_service

        conversation_id = str(uuid4())

        response = client.post(
            "/api/qa/search",
            json={
                "query": "test",
                "conversation_id": conversation_id,
            },
        )

        assert response.status_code == status.HTTP_200_OK

    def test_search_messages_empty_query(
        self,
        client: TestClient,
    ) -> None:
        """Test validation error for empty query.

        Args:
            client: Test client
        """
        response = client.post(
            "/api/qa/search",
            json={
                "query": "   ",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_search_messages_without_authentication(
        self,
        client: TestClient,
    ) -> None:
        """Test error when not authenticated.

        Args:
            client: Test client
        """
        response = client.post(
            "/api/qa/search",
            json={
                "query": "test",
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestRateMessageEndpoint:
    """Tests for rate message endpoint."""

    @patch("src.api.qa.get_current_verified_user")
    @patch("src.api.qa.get_qa_service")
    def test_rate_message_success(
        self,
        mock_get_service: Any,
        mock_get_user: Any,
        client: TestClient,
        mock_user: Dict[str, Any],
        mock_message: Message,
    ) -> None:
        """Test successful message rating.

        Args:
            mock_get_service: Mock Q&A service
            mock_get_user: Mock user dependency
            client: Test client
            mock_user: Mock user data
            mock_message: Mock message
        """
        mock_user_obj = MagicMock()
        mock_user_obj.id = mock_user["id"]
        mock_user_obj.email = mock_user["email"]
        mock_user_obj.email_verified = mock_user["email_verified"]
        mock_get_user.return_value = mock_user_obj

        mock_rating = MessageRating(
            message_id=str(mock_message.id),
            user_id=str(mock_user["id"]),
            rating=5,
            feedback_text="Great response!",
            is_helpful=True,
        )
        mock_rating.id = uuid4()

        mock_service = MagicMock()
        mock_service.rate_message = AsyncMock(return_value=mock_rating)
        mock_get_service.return_value = mock_service

        response = client.post(
            f"/api/qa/rate/{mock_message.id}",
            json={
                "rating": 5,
                "feedback_text": "Great response!",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "rating_id" in data
        assert data["rating"] == 5
        assert data["is_helpful"] is True

    @patch("src.api.qa.get_current_verified_user")
    @patch("src.api.qa.get_qa_service")
    def test_rate_message_update_existing(
        self,
        mock_get_service: Any,
        mock_get_user: Any,
        client: TestClient,
        mock_user: Dict[str, Any],
        mock_message: Message,
    ) -> None:
        """Test updating existing message rating.

        Args:
            mock_get_service: Mock Q&A service
            mock_get_user: Mock user dependency
            client: Test client
            mock_user: Mock user data
            mock_message: Mock message
        """
        mock_user_obj = MagicMock()
        mock_user_obj.id = mock_user["id"]
        mock_user_obj.email = mock_user["email"]
        mock_user_obj.email_verified = mock_user["email_verified"]
        mock_get_user.return_value = mock_user_obj

        mock_rating = MessageRating(
            message_id=str(mock_message.id),
            user_id=str(mock_user["id"]),
            rating=3,
            feedback_text="Updated rating",
            is_helpful=True,
        )
        mock_rating.id = uuid4()

        mock_service = MagicMock()
        mock_service.rate_message = AsyncMock(return_value=mock_rating)
        mock_get_service.return_value = mock_service

        response = client.post(
            f"/api/qa/rate/{mock_message.id}",
            json={
                "rating": 3,
                "feedback_text": "Updated rating",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["rating"] == 3

    @patch("src.api.qa.get_current_verified_user")
    @patch("src.api.qa.get_qa_service")
    def test_rate_message_not_found(
        self,
        mock_get_service: Any,
        mock_get_user: Any,
        client: TestClient,
        mock_user: Dict[str, Any],
    ) -> None:
        """Test error when message not found.

        Args:
            mock_get_service: Mock Q&A service
            mock_get_user: Mock user dependency
            client: Test client
            mock_user: Mock user data
        """
        mock_user_obj = MagicMock()
        mock_user_obj.id = mock_user["id"]
        mock_user_obj.email = mock_user["email"]
        mock_user_obj.email_verified = mock_user["email_verified"]
        mock_get_user.return_value = mock_user_obj

        mock_service = MagicMock()
        mock_service.rate_message = AsyncMock(
            side_effect=ValueError("Message not found or not an AI message")
        )
        mock_get_service.return_value = mock_service

        message_id = str(uuid4())

        response = client.post(
            f"/api/qa/rate/{message_id}",
            json={
                "rating": 5,
            },
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_rate_message_invalid_rating(
        self,
        client: TestClient,
    ) -> None:
        """Test validation error for invalid rating.

        Args:
            client: Test client
        """
        message_id = str(uuid4())

        response = client.post(
            f"/api/qa/rate/{message_id}",
            json={
                "rating": 10,
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_rate_message_without_authentication(
        self,
        client: TestClient,
    ) -> None:
        """Test error when not authenticated.

        Args:
            client: Test client
        """
        message_id = str(uuid4())

        response = client.post(
            f"/api/qa/rate/{message_id}",
            json={
                "rating": 5,
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestWebSocketIntegration:
    """Tests for WebSocket integration with Q&A endpoints."""

    @patch("src.api.qa.ws_manager")
    @patch("src.api.qa.get_current_verified_user")
    @patch("src.api.qa.get_qa_service")
    @patch("src.api.qa.limiter.limit")
    def test_websocket_notification_on_response(
        self,
        mock_limiter: Any,
        mock_get_service: Any,
        mock_get_user: Any,
        mock_ws_manager: Any,
        client: TestClient,
        mock_user: Dict[str, Any],
        mock_conversation_response: ConversationResponse,
    ) -> None:
        """Test WebSocket notification sent on AI response.

        Args:
            mock_limiter: Mock rate limiter
            mock_get_service: Mock Q&A service
            mock_get_user: Mock user dependency
            mock_ws_manager: Mock WebSocket manager
            client: Test client
            mock_user: Mock user data
            mock_conversation_response: Mock conversation response
        """
        mock_limiter.return_value = lambda f: f
        mock_user_obj = MagicMock()
        mock_user_obj.id = mock_user["id"]
        mock_user_obj.email = mock_user["email"]
        mock_user_obj.email_verified = mock_user["email_verified"]
        mock_get_user.return_value = mock_user_obj

        mock_service = MagicMock()
        mock_service.ask_question = AsyncMock(return_value=mock_conversation_response)
        mock_get_service.return_value = mock_service

        mock_ws_manager.send_to_user = AsyncMock()

        response = client.post(
            "/api/qa/ask",
            json={
                "question": "Test question",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        mock_ws_manager.send_to_user.assert_called_once()

    @patch("src.api.qa.ws_manager")
    @patch("src.api.qa.get_current_verified_user")
    @patch("src.api.qa.get_qa_service")
    @patch("src.api.qa.limiter.limit")
    def test_websocket_notification_failure_handled(
        self,
        mock_limiter: Any,
        mock_get_service: Any,
        mock_get_user: Any,
        mock_ws_manager: Any,
        client: TestClient,
        mock_user: Dict[str, Any],
        mock_conversation_response: ConversationResponse,
    ) -> None:
        """Test WebSocket notification failure doesn't break request.

        Args:
            mock_limiter: Mock rate limiter
            mock_get_service: Mock Q&A service
            mock_get_user: Mock user dependency
            mock_ws_manager: Mock WebSocket manager
            client: Test client
            mock_user: Mock user data
            mock_conversation_response: Mock conversation response
        """
        mock_limiter.return_value = lambda f: f
        mock_user_obj = MagicMock()
        mock_user_obj.id = mock_user["id"]
        mock_user_obj.email = mock_user["email"]
        mock_user_obj.email_verified = mock_user["email_verified"]
        mock_get_user.return_value = mock_user_obj

        mock_service = MagicMock()
        mock_service.ask_question = AsyncMock(return_value=mock_conversation_response)
        mock_get_service.return_value = mock_service

        mock_ws_manager.send_to_user = AsyncMock(side_effect=Exception("WS error"))

        response = client.post(
            "/api/qa/ask",
            json={
                "question": "Test question",
            },
        )

        assert response.status_code == status.HTTP_200_OK
