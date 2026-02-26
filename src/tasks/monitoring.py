"""Task monitoring utilities and health checks for Celery workers."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from celery import Celery
from celery.app.control import Inspect

from src.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


class TaskMonitor:
    """Monitor Celery tasks, queues, and worker status.

    Provides methods to inspect task status, queue statistics,
    and worker health for monitoring and debugging purposes.
    """

    def __init__(self, app: Optional[Celery] = None) -> None:
        """Initialize task monitor with Celery application.

        Args:
            app: Optional Celery application instance. Defaults to celery_app.
        """
        self.app = app or celery_app
        self.inspector: Inspect = self.app.control.inspect()

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get detailed status of a specific task by ID.

        Args:
            task_id: Celery task ID to query

        Returns:
            Dict[str, Any]: Task status information including:
                - task_id: Task identifier
                - status: Current task state
                - result: Task result if completed
                - error: Error information if failed
                - metadata: Additional task metadata
        """
        try:
            task_result = self.app.AsyncResult(task_id)

            status_info = {
                "task_id": task_id,
                "status": task_result.state,
                "ready": task_result.ready(),
                "successful": task_result.successful() if task_result.ready() else None,
                "failed": task_result.failed() if task_result.ready() else None,
            }

            if task_result.ready():
                if task_result.successful():
                    status_info["result"] = task_result.result
                elif task_result.failed():
                    status_info["error"] = str(task_result.info)
                    status_info["traceback"] = task_result.traceback

            if task_result.state == "PROGRESS":
                status_info["progress"] = task_result.info

            logger.debug(
                "Retrieved task status",
                extra={"task_id": task_id, "status": task_result.state},
            )

            return status_info

        except Exception as exc:
            logger.error(
                "Failed to get task status",
                extra={"task_id": task_id, "error": str(exc)},
                exc_info=True,
            )
            return {
                "task_id": task_id,
                "status": "UNKNOWN",
                "error": f"Failed to retrieve task status: {str(exc)}",
            }

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get statistics for all configured task queues.

        Returns:
            Dict[str, Any]: Queue statistics including:
                - queues: List of queue information
                - total_messages: Total pending messages across all queues
                - timestamp: When statistics were collected
        """
        try:
            active_queues = self.inspector.active_queues()
            reserved_tasks = self.inspector.reserved()

            if active_queues is None:
                logger.warning("No active workers found for queue stats")
                return {
                    "queues": [],
                    "total_messages": 0,
                    "error": "No active workers",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            queue_info = []
            total_messages = 0

            for worker, queues in active_queues.items():
                worker_reserved = (
                    len(reserved_tasks.get(worker, [])) if reserved_tasks else 0
                )

                for queue in queues:
                    queue_data = {
                        "name": queue["name"],
                        "routing_key": queue.get("routing_key"),
                        "worker": worker,
                        "reserved_tasks": worker_reserved,
                    }
                    queue_info.append(queue_data)
                    total_messages += worker_reserved

            stats = {
                "queues": queue_info,
                "total_messages": total_messages,
                "total_workers": len(active_queues),
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.info(
                "Retrieved queue statistics",
                extra={
                    "total_queues": len(queue_info),
                    "total_messages": total_messages,
                },
            )

            return stats

        except Exception as exc:
            logger.error(
                "Failed to get queue statistics",
                extra={"error": str(exc)},
                exc_info=True,
            )
            return {
                "queues": [],
                "total_messages": 0,
                "error": f"Failed to retrieve queue stats: {str(exc)}",
                "timestamp": datetime.utcnow().isoformat(),
            }

    def get_worker_stats(self) -> Dict[str, Any]:
        """Get statistics for all active Celery workers.

        Returns:
            Dict[str, Any]: Worker statistics including:
                - workers: List of worker information
                - total_workers: Number of active workers
                - total_active_tasks: Currently executing tasks
                - timestamp: When statistics were collected
        """
        try:
            stats = self.inspector.stats()
            active = self.inspector.active()
            registered = self.inspector.registered()

            if stats is None:
                logger.warning("No active workers found for worker stats")
                return {
                    "workers": [],
                    "total_workers": 0,
                    "total_active_tasks": 0,
                    "error": "No active workers",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            worker_info = []
            total_active_tasks = 0

            for worker_name, worker_stats in stats.items():
                active_tasks = len(active.get(worker_name, [])) if active else 0
                registered_tasks = (
                    len(registered.get(worker_name, [])) if registered else 0
                )

                worker_data = {
                    "name": worker_name,
                    "pool": worker_stats.get("pool", {}).get("implementation"),
                    "max_concurrency": worker_stats.get("pool", {}).get(
                        "max-concurrency"
                    ),
                    "active_tasks": active_tasks,
                    "registered_tasks": registered_tasks,
                    "total_tasks_completed": worker_stats.get("total", {}),
                }
                worker_info.append(worker_data)
                total_active_tasks += active_tasks

            result = {
                "workers": worker_info,
                "total_workers": len(worker_info),
                "total_active_tasks": total_active_tasks,
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.info(
                "Retrieved worker statistics",
                extra={
                    "total_workers": len(worker_info),
                    "total_active_tasks": total_active_tasks,
                },
            )

            return result

        except Exception as exc:
            logger.error(
                "Failed to get worker statistics",
                extra={"error": str(exc)},
                exc_info=True,
            )
            return {
                "workers": [],
                "total_workers": 0,
                "total_active_tasks": 0,
                "error": f"Failed to retrieve worker stats: {str(exc)}",
                "timestamp": datetime.utcnow().isoformat(),
            }


def check_worker_health() -> Dict[str, Any]:
    """Check health status of Celery workers.

    Returns:
        Dict[str, Any]: Health check results including:
            - healthy: Boolean indicating overall health
            - workers_online: Number of responding workers
            - timestamp: When health check was performed
            - details: Detailed health information
    """
    try:
        inspector = celery_app.control.inspect()
        stats = inspector.stats()
        active = inspector.active()

        if stats is None:
            logger.warning("Health check: No active workers found")
            return {
                "healthy": False,
                "workers_online": 0,
                "error": "No active workers responding",
                "timestamp": datetime.utcnow().isoformat(),
            }

        workers_online = len(stats)
        total_active_tasks = sum(len(tasks) for tasks in active.values()) if active else 0

        result = {
            "healthy": True,
            "workers_online": workers_online,
            "total_active_tasks": total_active_tasks,
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "workers": list(stats.keys()),
            },
        }

        logger.info(
            "Worker health check completed",
            extra={
                "healthy": True,
                "workers_online": workers_online,
            },
        )

        return result

    except Exception as exc:
        logger.error(
            "Worker health check failed",
            extra={"error": str(exc)},
            exc_info=True,
        )
        return {
            "healthy": False,
            "workers_online": 0,
            "error": f"Health check failed: {str(exc)}",
            "timestamp": datetime.utcnow().isoformat(),
        }


def check_broker_connectivity() -> Dict[str, Any]:
    """Check connectivity to Redis broker.

    Returns:
        Dict[str, Any]: Broker connectivity status including:
            - connected: Boolean indicating connection status
            - broker_url: Broker URL (masked)
            - timestamp: When check was performed
    """
    try:
        inspector = celery_app.control.inspect()
        ping_result = inspector.ping()

        if ping_result is None or len(ping_result) == 0:
            logger.warning("Broker connectivity check: No workers responding")
            return {
                "connected": False,
                "error": "No workers responding to ping",
                "timestamp": datetime.utcnow().isoformat(),
            }

        broker_url = celery_app.conf.broker_url
        masked_url = broker_url.split("@")[-1] if "@" in broker_url else broker_url

        result = {
            "connected": True,
            "broker_url": masked_url,
            "workers_responding": len(ping_result),
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(
            "Broker connectivity check successful",
            extra={"workers_responding": len(ping_result)},
        )

        return result

    except Exception as exc:
        logger.error(
            "Broker connectivity check failed",
            extra={"error": str(exc)},
            exc_info=True,
        )
        return {
            "connected": False,
            "error": f"Connectivity check failed: {str(exc)}",
            "timestamp": datetime.utcnow().isoformat(),
        }


def get_task_monitor() -> TaskMonitor:
    """Get TaskMonitor instance for monitoring Celery tasks.

    Returns:
        TaskMonitor: Configured task monitor instance
    """
    return TaskMonitor(celery_app)
