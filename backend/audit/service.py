import logging
import json
import uuid
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any

class JsonFormatter(logging.Formatter):
    """Custom formatter to output logs in JSON format."""
    def format(self, record):
        # Create a base log record
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        # If there's extra data, merge it into the log record
        if hasattr(record, 'extra_data'):
            log_record.update(record.extra_data)
        return json.dumps(log_record)

def setup_audit_logger():
    """Sets up a dedicated logger for audit trails."""
    logger = logging.getLogger("audit")
    logger.setLevel(logging.INFO)
    logger.propagate = False # Prevent duplicate logs in the root logger

    # If handlers are already configured, don't add them again
    if logger.hasHandlers():
        return logger

    # Use a file handler to write to a file
    handler = logging.FileHandler("audit_log.jsonl")

    # Use our custom JSON formatter
    formatter = JsonFormatter()
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger

class AuditService:
    """
    A centralized service for logging audit trails of all significant events
    in the MCP and other parts of the system using structured JSON logging.
    """
    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def log_event(
        self,
        event_name: str,
        job_id: UUID,
        user_id: Optional[str] = "default_user",
        session_id: Optional[str] = None,
        status: str = "success",
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Logs a structured event using the configured logger.

        Args:
            event_name (str): The name of the event (e.g., "session_created", "model_trained").
            job_id (UUID): The unique ID of the job this event belongs to.
            user_id (str, optional): The ID of the user who initiated the event.
            session_id (str, optional): The session ID if the event is part of a session.
            status (str, optional): The status of the event (e.g., "success", "failed", "pending").
            details (Dict[str, Any], optional): Any additional structured data about the event.
        """
        log_details = {
            "audit_id": str(uuid.uuid4()),
            "job_id": str(job_id),
            "user_id": user_id,
            "session_id": session_id,
            "event_name": event_name,
            "status": status,
            "details": details or {}
        }

        # Pass the structured data via the 'extra' parameter
        self._logger.info(
            f"Audit Event Recorded: {event_name}",
            extra={'extra_data': log_details}
        )

# Instantiate the logger and the service for dependency injection
audit_logger = setup_audit_logger()
audit_service = AuditService(logger=audit_logger)
