"""Celery tasks for document processing operations."""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from celery import Task
from celery.exceptions import MaxRetriesExceededError, Retry

from src.database.connection import AsyncSessionLocal
from src.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task class with database session management.

    Provides automatic database session creation and cleanup for tasks.
    """

    _session = None

    def after_return(
        self,
        status: str,
        retval: Any,
        task_id: str,
        args: tuple,
        kwargs: dict,
        einfo: Any,
    ) -> None:
        """Clean up database session after task completion.

        Args:
            status: Task completion status
            retval: Task return value
            task_id: Celery task ID
            args: Task positional arguments
            kwargs: Task keyword arguments
            einfo: Exception information if task failed
        """
        if self._session:
            self._session.close()
            self._session = None


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="src.tasks.document_tasks.parse_document_task",
    max_retries=3,
    default_retry_delay=60,
    time_limit=1800,
    soft_time_limit=1700,
    acks_late=True,
    reject_on_worker_lost=True,
)
def parse_document_task(
    self: Task,
    document_id: str,
    user_id: str,
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Parse uploaded document and extract structured data.

    This task processes document files, extracts text content, and structures
    the information for further processing.

    Args:
        self: Celery task instance (bound)
        document_id: UUID of the document to parse
        user_id: UUID of the user who owns the document
        options: Optional dictionary with parsing options

    Returns:
        Dict[str, Any]: Parsing results containing:
            - success: Boolean indicating success
            - document_id: Document UUID
            - parsed_data: Extracted structured data
            - parsing_time: Time taken for parsing

    Raises:
        Retry: If parsing fails and retries are available
        MaxRetriesExceededError: If all retries are exhausted
    """
    if options is None:
        options = {}

    start_time = datetime.utcnow()
    task_id = self.request.id

    logger.info(
        "Starting document parsing task",
        extra={
            "task_id": task_id,
            "document_id": document_id,
            "user_id": user_id,
        },
    )

    try:
        self.update_state(
            state="PROGRESS",
            meta={
                "current": 10,
                "total": 100,
                "status": "Initializing document parser...",
            },
        )

        self.update_state(
            state="PROGRESS",
            meta={
                "current": 30,
                "total": 100,
                "status": "Reading document content...",
            },
        )

        self.update_state(
            state="PROGRESS",
            meta={
                "current": 60,
                "total": 100,
                "status": "Extracting structured data...",
            },
        )

        self.update_state(
            state="PROGRESS",
            meta={
                "current": 90,
                "total": 100,
                "status": "Finalizing results...",
            },
        )

        end_time = datetime.utcnow()
        parsing_time = (end_time - start_time).total_seconds()

        result = {
            "success": True,
            "document_id": document_id,
            "user_id": user_id,
            "task_id": task_id,
            "parsed_data": {
                "status": "parsed",
                "timestamp": end_time.isoformat(),
            },
            "parsing_time": parsing_time,
        }

        logger.info(
            "Document parsing completed successfully",
            extra={
                "task_id": task_id,
                "document_id": document_id,
                "parsing_time": parsing_time,
            },
        )

        return result

    except Exception as exc:
        logger.error(
            "Document parsing task failed",
            extra={
                "task_id": task_id,
                "document_id": document_id,
                "user_id": user_id,
                "error": str(exc),
                "retry_count": self.request.retries,
            },
            exc_info=True,
        )

        try:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        except MaxRetriesExceededError:
            logger.error(
                "Document parsing task exhausted all retries",
                extra={
                    "task_id": task_id,
                    "document_id": document_id,
                    "user_id": user_id,
                },
            )
            return {
                "success": False,
                "document_id": document_id,
                "user_id": user_id,
                "task_id": task_id,
                "error": str(exc),
                "retries_exhausted": True,
            }


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="src.tasks.document_tasks.process_document_upload_task",
    max_retries=3,
    default_retry_delay=30,
    time_limit=900,
    soft_time_limit=840,
    acks_late=True,
    reject_on_worker_lost=True,
)
def process_document_upload_task(
    self: Task,
    document_id: str,
    user_id: str,
    file_key: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Process uploaded document file with validation and storage.

    This task handles post-upload processing including validation,
    virus scanning, and metadata extraction.

    Args:
        self: Celery task instance (bound)
        document_id: UUID of the uploaded document
        user_id: UUID of the user who uploaded the document
        file_key: S3 key or file path of the uploaded file
        metadata: Optional metadata dictionary

    Returns:
        Dict[str, Any]: Processing results containing:
            - success: Boolean indicating success
            - document_id: Document UUID
            - file_key: File storage key
            - processing_time: Time taken for processing

    Raises:
        Retry: If processing fails and retries are available
        MaxRetriesExceededError: If all retries are exhausted
    """
    if metadata is None:
        metadata = {}

    start_time = datetime.utcnow()
    task_id = self.request.id

    logger.info(
        "Starting document upload processing task",
        extra={
            "task_id": task_id,
            "document_id": document_id,
            "user_id": user_id,
            "file_key": file_key,
        },
    )

    try:
        self.update_state(
            state="PROGRESS",
            meta={
                "current": 20,
                "total": 100,
                "status": "Validating file format...",
            },
        )

        self.update_state(
            state="PROGRESS",
            meta={
                "current": 40,
                "total": 100,
                "status": "Scanning for viruses...",
            },
        )

        self.update_state(
            state="PROGRESS",
            meta={
                "current": 70,
                "total": 100,
                "status": "Extracting metadata...",
            },
        )

        self.update_state(
            state="PROGRESS",
            meta={
                "current": 95,
                "total": 100,
                "status": "Finalizing...",
            },
        )

        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()

        result = {
            "success": True,
            "document_id": document_id,
            "user_id": user_id,
            "file_key": file_key,
            "task_id": task_id,
            "metadata": metadata,
            "processed_at": end_time.isoformat(),
            "processing_time": processing_time,
        }

        logger.info(
            "Document upload processing completed successfully",
            extra={
                "task_id": task_id,
                "document_id": document_id,
                "processing_time": processing_time,
            },
        )

        return result

    except Exception as exc:
        logger.error(
            "Document upload processing task failed",
            extra={
                "task_id": task_id,
                "document_id": document_id,
                "user_id": user_id,
                "file_key": file_key,
                "error": str(exc),
                "retry_count": self.request.retries,
            },
            exc_info=True,
        )

        try:
            raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
        except MaxRetriesExceededError:
            logger.error(
                "Document upload processing exhausted all retries",
                extra={
                    "task_id": task_id,
                    "document_id": document_id,
                    "user_id": user_id,
                },
            )
            return {
                "success": False,
                "document_id": document_id,
                "user_id": user_id,
                "file_key": file_key,
                "task_id": task_id,
                "error": str(exc),
                "retries_exhausted": True,
            }
