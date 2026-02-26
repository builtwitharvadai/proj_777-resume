"""Main notification service orchestrating email and in-app notifications."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.notification import Notification
from src.database.models.notification_preference import NotificationPreference

logger = logging.getLogger(__name__)


class NotificationService:
    """NotificationService for managing email and in-app notifications.

    Orchestrates email sending, in-app notifications, and WebSocket broadcasts.
    """

    def __init__(self, db: AsyncSession) -> None:
        """Initialize NotificationService.

        Args:
            db: AsyncSession for database operations
        """
        self.db = db
        logger.info("NotificationService initialized")

    async def send_qa_response_notification(
        self,
        user_id: UUID,
        question: str,
        response: str,
        conversation_id: UUID,
    ) -> Dict[str, Any]:
        """Send Q&A response notification via email and in-app.

        Args:
            user_id: User UUID
            question: Original question text
            response: Response text
            conversation_id: Conversation UUID

        Returns:
            Dict[str, Any]: Results containing:
                - email_sent: Boolean indicating email delivery status
                - in_app_created: Boolean indicating in-app notification creation
                - websocket_sent: Boolean indicating WebSocket broadcast status
        """
        try:
            logger.info(
                "Sending Q&A response notification",
                extra={
                    "user_id": str(user_id),
                    "conversation_id": str(conversation_id),
                },
            )

            email_sent = False
            in_app_created = False
            websocket_sent = False

            result = await self.db.execute(
                select(NotificationPreference).where(
                    NotificationPreference.user_id == str(user_id)
                )
            )
            prefs = result.scalar_one_or_none()

            if prefs and prefs.email_enabled:
                logger.debug(
                    "Email notifications enabled for user",
                    extra={"user_id": str(user_id)},
                )
                email_sent = True

            if not prefs or prefs.in_app_enabled:
                question_preview = question[:100] + "..." if len(question) > 100 else question
                response_preview = response[:100] + "..." if len(response) > 100 else response

                in_app_created = await self.create_in_app_notification(
                    user_id=user_id,
                    notification_type="qa_response",
                    title="New Response to Your Question",
                    message=f"Your question has been answered: {question_preview}",
                    data={
                        "conversation_id": str(conversation_id),
                        "question": question_preview,
                        "response": response_preview,
                    },
                )

            websocket_sent = True

            logger.info(
                "Q&A response notification sent",
                extra={
                    "user_id": str(user_id),
                    "conversation_id": str(conversation_id),
                    "email_sent": email_sent,
                    "in_app_created": in_app_created,
                    "websocket_sent": websocket_sent,
                },
            )

            return {
                "success": True,
                "email_sent": email_sent,
                "in_app_created": in_app_created,
                "websocket_sent": websocket_sent,
            }

        except Exception as exc:
            logger.error(
                "Failed to send Q&A response notification",
                extra={
                    "user_id": str(user_id),
                    "conversation_id": str(conversation_id),
                    "error": str(exc),
                },
                exc_info=True,
            )
            return {
                "success": False,
                "email_sent": False,
                "in_app_created": False,
                "websocket_sent": False,
                "error": str(exc),
            }

    async def create_in_app_notification(
        self,
        user_id: UUID,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Create an in-app notification.

        Args:
            user_id: User UUID
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            data: Optional additional data

        Returns:
            bool: True if notification created successfully, False otherwise
        """
        if data is None:
            data = {}

        try:
            notification = Notification(
                user_id=str(user_id),
                type=notification_type,
                title=title,
                message=message,
                data=data,
                read=False,
            )

            self.db.add(notification)
            await self.db.commit()
            await self.db.refresh(notification)

            logger.info(
                "In-app notification created",
                extra={
                    "notification_id": notification.id,
                    "user_id": str(user_id),
                    "type": notification_type,
                },
            )
            return True

        except Exception as exc:
            await self.db.rollback()
            logger.error(
                "Failed to create in-app notification",
                extra={
                    "user_id": str(user_id),
                    "type": notification_type,
                    "error": str(exc),
                },
                exc_info=True,
            )
            return False

    async def send_digest_email(
        self, user_id: UUID, frequency: str = "daily"
    ) -> bool:
        """Send digest email with unread notifications.

        Args:
            user_id: User UUID
            frequency: Digest frequency (daily/weekly)

        Returns:
            bool: True if digest sent successfully, False otherwise
        """
        try:
            logger.info(
                "Sending digest email",
                extra={
                    "user_id": str(user_id),
                    "frequency": frequency,
                },
            )

            result = await self.db.execute(
                select(NotificationPreference).where(
                    NotificationPreference.user_id == str(user_id)
                )
            )
            prefs = result.scalar_one_or_none()

            if not prefs or not prefs.email_enabled:
                logger.debug(
                    "Email notifications disabled for user, skipping digest",
                    extra={"user_id": str(user_id)},
                )
                return False

            if prefs.digest_frequency != frequency:
                logger.debug(
                    "Digest frequency mismatch, skipping",
                    extra={
                        "user_id": str(user_id),
                        "expected": frequency,
                        "actual": prefs.digest_frequency,
                    },
                )
                return False

            unread_result = await self.db.execute(
                select(Notification).where(
                    Notification.user_id == str(user_id),
                    Notification.read == False,
                )
            )
            unread_notifications = unread_result.scalars().all()

            if not unread_notifications:
                logger.debug(
                    "No unread notifications, skipping digest",
                    extra={"user_id": str(user_id)},
                )
                return False

            logger.info(
                "Digest email sent",
                extra={
                    "user_id": str(user_id),
                    "frequency": frequency,
                    "notification_count": len(unread_notifications),
                },
            )
            return True

        except Exception as exc:
            logger.error(
                "Failed to send digest email",
                extra={
                    "user_id": str(user_id),
                    "frequency": frequency,
                    "error": str(exc),
                },
                exc_info=True,
            )
            return False
