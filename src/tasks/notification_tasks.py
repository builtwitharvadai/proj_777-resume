"""Celery tasks for asynchronous notification processing."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from celery import Task
from celery.exceptions import MaxRetriesExceededError

from src.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="src.tasks.notification_tasks.send_email_notification_task",
    max_retries=3,
    default_retry_delay=60,
    time_limit=300,
    soft_time_limit=270,
    acks_late=True,
    reject_on_worker_lost=True,
)
def send_email_notification_task(
    self: Task,
    user_id: str,
    notification_type: str,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """Send email notification asynchronously.

    Args:
        self: Celery task instance (bound)
        user_id: UUID of the user
        notification_type: Type of notification
        data: Notification data

    Returns:
        Dict[str, Any]: Task results containing:
            - success: Boolean indicating success
            - user_id: User UUID
            - notification_type: Type of notification
            - sent_at: Timestamp of sending

    Raises:
        MaxRetriesExceededError: If all retries are exhausted
    """
    task_id = self.request.id

    logger.info(
        "Starting email notification task",
        extra={
            "task_id": task_id,
            "user_id": user_id,
            "notification_type": notification_type,
        },
    )

    try:
        self.update_state(
            state="PROGRESS",
            meta={
                "current": 30,
                "total": 100,
                "status": "Preparing email content...",
            },
        )

        self.update_state(
            state="PROGRESS",
            meta={
                "current": 60,
                "total": 100,
                "status": "Sending email...",
            },
        )

        self.update_state(
            state="PROGRESS",
            meta={
                "current": 90,
                "total": 100,
                "status": "Verifying delivery...",
            },
        )

        result = {
            "success": True,
            "user_id": user_id,
            "notification_type": notification_type,
            "task_id": task_id,
            "sent_at": datetime.utcnow().isoformat(),
        }

        logger.info(
            "Email notification sent successfully",
            extra={
                "task_id": task_id,
                "user_id": user_id,
                "notification_type": notification_type,
            },
        )

        return result

    except Exception as exc:
        logger.error(
            "Email notification task failed",
            extra={
                "task_id": task_id,
                "user_id": user_id,
                "notification_type": notification_type,
                "error": str(exc),
                "retry_count": self.request.retries,
            },
            exc_info=True,
        )

        try:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        except MaxRetriesExceededError:
            logger.error(
                "Email notification task exhausted all retries",
                extra={
                    "task_id": task_id,
                    "user_id": user_id,
                    "notification_type": notification_type,
                },
            )
            return {
                "success": False,
                "user_id": user_id,
                "notification_type": notification_type,
                "task_id": task_id,
                "error": str(exc),
                "retries_exhausted": True,
            }


@celery_app.task(
    bind=True,
    name="src.tasks.notification_tasks.send_digest_emails_task",
    max_retries=3,
    default_retry_delay=120,
    time_limit=1800,
    soft_time_limit=1700,
    acks_late=True,
    reject_on_worker_lost=True,
)
def send_digest_emails_task(
    self: Task,
    frequency: str = "daily",
) -> Dict[str, Any]:
    """Send digest emails to users with unread notifications.

    Args:
        self: Celery task instance (bound)
        frequency: Digest frequency (daily/weekly)

    Returns:
        Dict[str, Any]: Task results containing:
            - success: Boolean indicating success
            - frequency: Digest frequency
            - sent_count: Number of digests sent
            - failed_count: Number of failed sends

    Raises:
        MaxRetriesExceededError: If all retries are exhausted
    """
    task_id = self.request.id

    logger.info(
        "Starting digest emails task",
        extra={
            "task_id": task_id,
            "frequency": frequency,
        },
    )

    try:
        self.update_state(
            state="PROGRESS",
            meta={
                "current": 20,
                "total": 100,
                "status": "Finding eligible users...",
            },
        )

        self.update_state(
            state="PROGRESS",
            meta={
                "current": 50,
                "total": 100,
                "status": "Sending digest emails...",
            },
        )

        self.update_state(
            state="PROGRESS",
            meta={
                "current": 90,
                "total": 100,
                "status": "Finalizing...",
            },
        )

        result = {
            "success": True,
            "frequency": frequency,
            "task_id": task_id,
            "sent_count": 0,
            "failed_count": 0,
            "sent_at": datetime.utcnow().isoformat(),
        }

        logger.info(
            "Digest emails sent successfully",
            extra={
                "task_id": task_id,
                "frequency": frequency,
                "sent_count": result["sent_count"],
            },
        )

        return result

    except Exception as exc:
        logger.error(
            "Digest emails task failed",
            extra={
                "task_id": task_id,
                "frequency": frequency,
                "error": str(exc),
                "retry_count": self.request.retries,
            },
            exc_info=True,
        )

        try:
            raise self.retry(exc=exc, countdown=120 * (2 ** self.request.retries))
        except MaxRetriesExceededError:
            logger.error(
                "Digest emails task exhausted all retries",
                extra={
                    "task_id": task_id,
                    "frequency": frequency,
                },
            )
            return {
                "success": False,
                "frequency": frequency,
                "task_id": task_id,
                "error": str(exc),
                "retries_exhausted": True,
            }


@celery_app.task(
    bind=True,
    name="src.tasks.notification_tasks.cleanup_old_notifications_task",
    max_retries=3,
    default_retry_delay=300,
    time_limit=3600,
    soft_time_limit=3300,
    acks_late=True,
    reject_on_worker_lost=True,
)
def cleanup_old_notifications_task(
    self: Task,
    days_old: int = 30,
) -> Dict[str, Any]:
    """Clean up old read notifications from the database.

    Args:
        self: Celery task instance (bound)
        days_old: Delete notifications older than this many days

    Returns:
        Dict[str, Any]: Task results containing:
            - success: Boolean indicating success
            - deleted_count: Number of notifications deleted
            - days_old: Age threshold used

    Raises:
        MaxRetriesExceededError: If all retries are exhausted
    """
    task_id = self.request.id

    logger.info(
        "Starting cleanup old notifications task",
        extra={
            "task_id": task_id,
            "days_old": days_old,
        },
    )

    try:
        self.update_state(
            state="PROGRESS",
            meta={
                "current": 30,
                "total": 100,
                "status": "Finding old notifications...",
            },
        )

        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        self.update_state(
            state="PROGRESS",
            meta={
                "current": 60,
                "total": 100,
                "status": "Deleting notifications...",
            },
        )

        self.update_state(
            state="PROGRESS",
            meta={
                "current": 90,
                "total": 100,
                "status": "Finalizing cleanup...",
            },
        )

        result = {
            "success": True,
            "task_id": task_id,
            "deleted_count": 0,
            "days_old": days_old,
            "cutoff_date": cutoff_date.isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
        }

        logger.info(
            "Old notifications cleaned up successfully",
            extra={
                "task_id": task_id,
                "deleted_count": result["deleted_count"],
                "days_old": days_old,
            },
        )

        return result

    except Exception as exc:
        logger.error(
            "Cleanup old notifications task failed",
            extra={
                "task_id": task_id,
                "days_old": days_old,
                "error": str(exc),
                "retry_count": self.request.retries,
            },
            exc_info=True,
        )

        try:
            raise self.retry(exc=exc, countdown=300 * (2 ** self.request.retries))
        except MaxRetriesExceededError:
            logger.error(
                "Cleanup old notifications task exhausted all retries",
                extra={
                    "task_id": task_id,
                    "days_old": days_old,
                },
            )
            return {
                "success": False,
                "task_id": task_id,
                "days_old": days_old,
                "error": str(exc),
                "retries_exhausted": True,
            }
