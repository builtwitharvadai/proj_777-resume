"""Q&A API endpoints for questions, conversations, and search."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.qa_rate_limit import (
    QA_RATE_LIMIT,
    limiter,
    rate_limit_exceeded_handler,
)
from src.auth.dependencies import get_current_verified_user
from src.database.connection import get_db
from src.database.models.user import User
from src.qa.schemas import (
    ConversationListResponse,
    ConversationResponse,
    MessageRatingRequest,
    MessageResponse,
    QuestionRequest,
    SearchRequest,
)
from src.qa.service import QAService
from src.websocket.manager import WebSocketManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/qa")

# WebSocket manager instance - will be initialized at application startup
ws_manager: Optional[WebSocketManager] = None


def get_qa_service() -> QAService:
    """Dependency for Q&A service.

    Returns:
        QAService: Q&A service instance
    """
    return QAService()


@router.post(
    "/ask",
    response_model=ConversationResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a question",
    description="Submit a question and receive an AI-generated response. "
    "Can continue an existing conversation or start a new one.",
)
@limiter.limit(QA_RATE_LIMIT)
async def ask_question(
    request: Request,
    question_request: QuestionRequest,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db),
    qa_service: QAService = Depends(get_qa_service),
) -> ConversationResponse:
    """Ask a question and receive an AI response.

    Processes user question, generates AI response, and sends real-time
    notifications via WebSocket if available.

    Args:
        request: FastAPI request (required for rate limiting)
        question_request: Question request data
        current_user: Authenticated and verified user
        db: Database session
        qa_service: Q&A service instance

    Returns:
        ConversationResponse: Conversation with user question and AI response

    Raises:
        HTTPException: If conversation not found or other errors occur
    """
    logger.info(
        "Processing question request",
        extra={
            "user_id": str(current_user.id),
            "conversation_id": str(question_request.conversation_id)
            if question_request.conversation_id
            else None,
            "category": question_request.category,
        },
    )

    # Store user_id in request state for rate limiting
    request.state.user_id = str(current_user.id)

    try:
        # Process question and get response
        conversation = await qa_service.ask_question(
            user_id=str(current_user.id),
            question=question_request.question,
            conversation_id=question_request.conversation_id,
            category=question_request.category,
            metadata=question_request.metadata,
            db=db,
        )

        logger.info(
            "Question processed successfully",
            extra={
                "user_id": str(current_user.id),
                "conversation_id": str(conversation.id),
                "message_count": len(conversation.messages),
            },
        )

        # Send real-time notification via WebSocket if manager is available
        if ws_manager:
            try:
                ai_message = conversation.messages[-1] if conversation.messages else None
                if ai_message:
                    await ws_manager.send_to_user(
                        user_id=current_user.id,
                        message={
                            "type": "qa_response",
                            "conversation_id": str(conversation.id),
                            "message": {
                                "id": str(ai_message.id),
                                "content": ai_message.content,
                                "created_at": ai_message.created_at.isoformat(),
                            },
                        },
                    )
                    logger.debug(
                        "WebSocket notification sent",
                        extra={
                            "user_id": str(current_user.id),
                            "conversation_id": str(conversation.id),
                        },
                    )
            except Exception as exc:
                logger.warning(
                    "Failed to send WebSocket notification",
                    extra={
                        "user_id": str(current_user.id),
                        "error": str(exc),
                    },
                )

        return conversation

    except ValueError as exc:
        logger.warning(
            "Invalid request",
            extra={
                "user_id": str(current_user.id),
                "error": str(exc),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.error(
            "Failed to process question",
            extra={
                "user_id": str(current_user.id),
                "error": str(exc),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process question",
        ) from exc


@router.get(
    "/conversations",
    response_model=ConversationListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get conversations",
    description="Retrieve user's conversations with optional filtering and pagination.",
)
async def get_conversations(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    offset: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db),
    qa_service: QAService = Depends(get_qa_service),
) -> ConversationListResponse:
    """Retrieve user's conversations.

    Supports filtering by category and active status, with pagination.

    Args:
        category: Optional category filter
        is_active: Optional active status filter
        offset: Pagination offset (default: 0)
        limit: Pagination limit (default: 20, max: 100)
        current_user: Authenticated and verified user
        db: Database session
        qa_service: Q&A service instance

    Returns:
        ConversationListResponse: List of conversations with pagination metadata

    Raises:
        HTTPException: If retrieval fails
    """
    # Validate limit
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 1

    logger.info(
        "Retrieving conversations",
        extra={
            "user_id": str(current_user.id),
            "category": category,
            "is_active": is_active,
            "offset": offset,
            "limit": limit,
        },
    )

    try:
        conversations, total = await qa_service.get_conversations(
            user_id=str(current_user.id),
            category=category,
            is_active=is_active,
            offset=offset,
            limit=limit,
            db=db,
        )

        logger.info(
            "Conversations retrieved",
            extra={
                "user_id": str(current_user.id),
                "count": len(conversations),
                "total": total,
            },
        )

        return ConversationListResponse(
            conversations=conversations,
            total=total,
            offset=offset,
            limit=limit,
        )

    except Exception as exc:
        logger.error(
            "Failed to retrieve conversations",
            extra={
                "user_id": str(current_user.id),
                "error": str(exc),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations",
        ) from exc


@router.post(
    "/search",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Search messages",
    description="Search user's messages using full-text search with optional conversation filter.",
)
async def search_messages(
    search_request: SearchRequest,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db),
    qa_service: QAService = Depends(get_qa_service),
) -> dict:
    """Search user's messages.

    Performs full-text search across messages with pagination support.

    Args:
        search_request: Search request data
        current_user: Authenticated and verified user
        db: Database session
        qa_service: Q&A service instance

    Returns:
        dict: Search results with messages and pagination metadata

    Raises:
        HTTPException: If search fails
    """
    logger.info(
        "Searching messages",
        extra={
            "user_id": str(current_user.id),
            "query": search_request.query,
            "conversation_id": str(search_request.conversation_id)
            if search_request.conversation_id
            else None,
        },
    )

    try:
        messages, total = await qa_service.search_messages(
            user_id=str(current_user.id),
            query=search_request.query,
            conversation_id=search_request.conversation_id,
            offset=search_request.offset,
            limit=search_request.limit,
            db=db,
        )

        logger.info(
            "Messages searched",
            extra={
                "user_id": str(current_user.id),
                "count": len(messages),
                "total": total,
            },
        )

        return {
            "messages": messages,
            "total": total,
            "offset": search_request.offset,
            "limit": search_request.limit,
        }

    except Exception as exc:
        logger.error(
            "Failed to search messages",
            extra={
                "user_id": str(current_user.id),
                "error": str(exc),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search messages",
        ) from exc


@router.post(
    "/rate/{message_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Rate a message",
    description="Rate an AI-generated message with optional feedback.",
)
async def rate_message(
    message_id: UUID,
    rating_request: MessageRatingRequest,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db),
    qa_service: QAService = Depends(get_qa_service),
) -> dict:
    """Rate an AI-generated message.

    Allows users to provide feedback on AI responses with a rating (1-5)
    and optional text feedback.

    Args:
        message_id: UUID of the message to rate
        rating_request: Rating data
        current_user: Authenticated and verified user
        db: Database session
        qa_service: Q&A service instance

    Returns:
        dict: Success message with rating details

    Raises:
        HTTPException: If message not found or rating fails
    """
    logger.info(
        "Rating message",
        extra={
            "user_id": str(current_user.id),
            "message_id": str(message_id),
            "rating": rating_request.rating,
        },
    )

    try:
        message_rating = await qa_service.rate_message(
            user_id=str(current_user.id),
            message_id=message_id,
            rating=rating_request.rating,
            feedback_text=rating_request.feedback_text,
            db=db,
        )

        logger.info(
            "Message rated successfully",
            extra={
                "user_id": str(current_user.id),
                "message_id": str(message_id),
                "rating_id": str(message_rating.id),
            },
        )

        return {
            "message": "Rating submitted successfully",
            "rating_id": str(message_rating.id),
            "rating": message_rating.rating,
            "is_helpful": message_rating.is_helpful,
        }

    except ValueError as exc:
        logger.warning(
            "Invalid rating request",
            extra={
                "user_id": str(current_user.id),
                "message_id": str(message_id),
                "error": str(exc),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.error(
            "Failed to rate message",
            extra={
                "user_id": str(current_user.id),
                "message_id": str(message_id),
                "error": str(exc),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to rate message",
        ) from exc


def set_websocket_manager(manager: WebSocketManager) -> None:
    """Set the WebSocket manager instance.

    Called during application startup to inject the manager.

    Args:
        manager: WebSocket manager instance
    """
    global ws_manager
    ws_manager = manager
    logger.info("WebSocket manager set for Q&A API")
