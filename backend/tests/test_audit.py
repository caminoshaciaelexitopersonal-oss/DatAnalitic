import pytest
import json
import logging
from uuid import uuid4
from backend.audit.service import AuditService, JsonFormatter

class MockLogHandler(logging.Handler):
    """Mock logging handler to check for expected logs."""
    def __init__(self, *args, **kwargs):
        self.reset()
        super().__init__(*args, **kwargs)

    def emit(self, record):
        self.messages.append(self.format(record))

    def reset(self):
        self.messages = []

@pytest.fixture
def mock_logger():
    """Fixture to create a logger with a mock handler."""
    logger = logging.getLogger("test_audit_logger")
    logger.setLevel(logging.INFO)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    mock_handler = MockLogHandler()
    formatter = JsonFormatter()
    mock_handler.setFormatter(formatter)
    logger.addHandler(mock_handler)

    return logger, mock_handler

def test_audit_service_log_event(mock_logger):
    """Tests that AuditService.log_event creates a structured JSON log."""
    logger, handler = mock_logger
    service = AuditService(logger=logger)

    job_id = uuid4()
    user_id = "test_user"
    event_name = "test_event"
    details = {"key": "value"}

    service.log_event(
        event_name=event_name,
        job_id=job_id,
        user_id=user_id,
        details=details
    )

    assert len(handler.messages) == 1
    log_output = json.loads(handler.messages[0])

    assert log_output["level"] == "INFO"
    assert log_output["message"] == f"Audit Event Recorded: {event_name}"

    # Corrected assertion: check for keys at the top level
    assert log_output["job_id"] == str(job_id)
    assert log_output["user_id"] == user_id
    assert log_output["event_name"] == event_name
    assert log_output["details"] == details
    assert "audit_id" in log_output

def test_json_formatter():
    """Tests that the JsonFormatter correctly formats a log record."""
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="A test message",
        args=(),
        exc_info=None
    )

    record.extra_data = {"custom": "data"}

    formatted_log = formatter.format(record)
    log_output = json.loads(formatted_log)

    assert log_output["level"] == "INFO"
    assert log_output["message"] == "A test message"
    assert log_output["custom"] == "data"
    assert "timestamp" in log_output
