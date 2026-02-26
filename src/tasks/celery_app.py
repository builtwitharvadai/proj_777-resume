"""Celery application configuration with Redis broker setup."""

import logging
from typing import Any, Dict

from celery import Celery
from celery.signals import after_setup_logger, task_failure, task_success
from kombu import Exchange, Queue

from src.core.config import settings

logger = logging.getLogger(__name__)

# Celery application instance
celery_app = Celery("resume_tasks")

# Redis broker and result backend configuration
celery_app.conf.broker_url = settings.CELERY_BROKER_URL
celery_app.conf.result_backend = settings.CELERY_RESULT_BACKEND

# Task serialization settings
celery_app.conf.task_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.result_serializer = "json"
celery_app.conf.timezone = "UTC"
celery_app.conf.enable_utc = True

# Task execution settings
celery_app.conf.task_track_started = True
celery_app.conf.task_time_limit = 3600
celery_app.conf.task_soft_time_limit = 3300
celery_app.conf.task_acks_late = True
celery_app.conf.worker_prefetch_multiplier = 1

# Retry configuration
celery_app.conf.task_default_retry_delay = 60
celery_app.conf.task_max_retries = 3

# Result backend settings
celery_app.conf.result_expires = 86400
celery_app.conf.result_persistent = True

# Worker configuration
celery_app.conf.worker_max_tasks_per_child = 1000
celery_app.conf.worker_disable_rate_limits = False
celery_app.conf.worker_log_format = (
    "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"
)
celery_app.conf.worker_task_log_format = (
    "[%(asctime)s: %(levelname)s/%(processName)s] "
    "[%(task_name)s(%(task_id)s)] %(message)s"
)

# Task routing configuration
celery_app.conf.task_default_queue = "default"
celery_app.conf.task_default_exchange = "tasks"
celery_app.conf.task_default_exchange_type = "direct"
celery_app.conf.task_default_routing_key = "default"

# Define queues with proper configuration
celery_app.conf.task_queues = (
    Queue(
        "default",
        Exchange("tasks", type="direct"),
        routing_key="default",
        queue_arguments={"x-max-priority": 10},
    ),
    Queue(
        "document_processing",
        Exchange("tasks", type="direct"),
        routing_key="document_processing",
        queue_arguments={"x-max-priority": 10},
    ),
    Queue(
        "high_priority",
        Exchange("tasks", type="direct"),
        routing_key="high_priority",
        queue_arguments={"x-max-priority": 10},
    ),
)

# Task routes for different task types
celery_app.conf.task_routes = {
    "src.tasks.document_tasks.parse_document_task": {
        "queue": "document_processing",
        "routing_key": "document_processing",
    },
    "src.tasks.document_tasks.process_document_upload_task": {
        "queue": "document_processing",
        "routing_key": "document_processing",
    },
}

# Broker connection settings
celery_app.conf.broker_connection_retry = True
celery_app.conf.broker_connection_retry_on_startup = True
celery_app.conf.broker_connection_max_retries = 10
celery_app.conf.broker_pool_limit = 10

# Result backend connection settings
celery_app.conf.redis_backend_health_check_interval = 30
celery_app.conf.redis_socket_timeout = 5
celery_app.conf.redis_socket_connect_timeout = 5
celery_app.conf.redis_retry_on_timeout = True
celery_app.conf.redis_max_connections = 50

# Error handling configuration
celery_app.conf.task_reject_on_worker_lost = True
celery_app.conf.task_ignore_result = False


@after_setup_logger.connect
def setup_task_logger(logger: Any, *args: Any, **kwargs: Any) -> None:
    """Configure Celery task logger with structured logging.

    Args:
        logger: Celery logger instance
        *args: Additional arguments
        **kwargs: Additional keyword arguments
    """
    formatter = logging.Formatter(
        "[%(asctime)s: %(levelname)s/%(processName)s] "
        "[%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    for handler in logger.handlers:
        handler.setFormatter(formatter)


@task_success.connect
def task_success_handler(sender: Any = None, **kwargs: Any) -> None:
    """Handle successful task completion.

    Args:
        sender: Task instance
        **kwargs: Additional keyword arguments including result
    """
    task_id = kwargs.get("result")
    logger.info(
        "Task completed successfully",
        extra={
            "task_id": sender.request.id if sender else None,
            "task_name": sender.name if sender else None,
        },
    )


@task_failure.connect
def task_failure_handler(
    sender: Any = None,
    task_id: str = None,
    exception: Exception = None,
    **kwargs: Any,
) -> None:
    """Handle task failure with logging and error tracking.

    Args:
        sender: Task instance
        task_id: Celery task ID
        exception: Exception that caused the failure
        **kwargs: Additional keyword arguments
    """
    logger.error(
        "Task failed",
        extra={
            "task_id": task_id,
            "task_name": sender.name if sender else None,
            "exception": str(exception),
            "exception_type": type(exception).__name__,
        },
        exc_info=True,
    )


def get_celery_app() -> Celery:
    """Get configured Celery application instance.

    Returns:
        Celery: Configured Celery application
    """
    return celery_app
