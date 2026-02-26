"""Task result model for tracking background job status and results."""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from src.database.base import BaseModel

logger = logging.getLogger(__name__)


class TaskResult(BaseModel):
    """Model for storing Celery task results and tracking job progress.

    Attributes:
        task_id: Unique Celery task ID (UUID format)
        user_id: Foreign key to user who initiated the task
        task_type: Type of task (e.g., 'parse_document', 'process_upload')
        status: Task status (pending, running, success, failed)
        progress_percentage: Task completion progress (0-100)
        result_data: JSON data containing task results
        error_message: Error message if task failed
        started_at: Timestamp when task execution started
        completed_at: Timestamp when task execution completed
    """

    __tablename__ = "task_results"

    task_id = Column(
        String(36),
        unique=True,
        nullable=False,
        index=True,
        comment="Celery task UUID",
    )

    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who initiated the task",
    )

    task_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Type of background task",
    )

    status = Column(
        String(20),
        nullable=False,
        default="pending",
        index=True,
        comment="Task status: pending, running, success, failed",
    )

    progress_percentage = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Task completion percentage (0-100)",
    )

    result_data = Column(
        JSON,
        nullable=True,
        comment="JSON data containing task results",
    )

    error_message = Column(
        Text,
        nullable=True,
        comment="Error message if task failed",
    )

    started_at = Column(
        DateTime,
        nullable=True,
        index=True,
        comment="Timestamp when task started executing",
    )

    completed_at = Column(
        DateTime,
        nullable=True,
        index=True,
        comment="Timestamp when task completed",
    )

    user = relationship("User", backref="task_results")

    def __repr__(self) -> str:
        """String representation of task result.

        Returns:
            str: String representation showing task ID and status
        """
        return f"<TaskResult(task_id={self.task_id}, status={self.status})>"

    def to_dict(self, exclude: Optional[set] = None) -> Dict[str, Any]:
        """Convert task result to dictionary with enhanced serialization.

        Args:
            exclude: Optional set of fields to exclude from output

        Returns:
            Dict[str, Any]: Dictionary representation of task result
        """
        if exclude is None:
            exclude = set()

        result = super().to_dict(exclude=exclude)

        if "started_at" in result and result["started_at"]:
            if isinstance(self.started_at, datetime):
                result["started_at"] = self.started_at.isoformat()

        if "completed_at" in result and result["completed_at"]:
            if isinstance(self.completed_at, datetime):
                result["completed_at"] = self.completed_at.isoformat()

        return result

    def mark_started(self) -> None:
        """Mark task as started and set started_at timestamp."""
        self.status = "running"
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        logger.info(
            "Task marked as started",
            extra={
                "task_id": self.task_id,
                "task_type": self.task_type,
                "user_id": self.user_id,
            },
        )

    def mark_completed(
        self, result_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Mark task as successfully completed.

        Args:
            result_data: Optional dictionary containing task results
        """
        self.status = "success"
        self.progress_percentage = 100
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        if result_data:
            self.result_data = result_data

        logger.info(
            "Task completed successfully",
            extra={
                "task_id": self.task_id,
                "task_type": self.task_type,
                "user_id": self.user_id,
            },
        )

    def mark_failed(self, error_message: str) -> None:
        """Mark task as failed with error message.

        Args:
            error_message: Error message describing the failure
        """
        self.status = "failed"
        self.error_message = error_message
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        logger.error(
            "Task failed",
            extra={
                "task_id": self.task_id,
                "task_type": self.task_type,
                "user_id": self.user_id,
                "error_message": error_message,
            },
        )

    def update_progress(self, percentage: int) -> None:
        """Update task progress percentage.

        Args:
            percentage: Progress percentage (0-100)

        Raises:
            ValueError: If percentage is not between 0 and 100
        """
        if not 0 <= percentage <= 100:
            raise ValueError("Progress percentage must be between 0 and 100")

        self.progress_percentage = percentage
        self.updated_at = datetime.utcnow()

        logger.debug(
            "Task progress updated",
            extra={
                "task_id": self.task_id,
                "task_type": self.task_type,
                "progress": percentage,
            },
        )
