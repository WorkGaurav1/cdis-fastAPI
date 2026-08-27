# Verifies utils/logging.py's redaction processor and request-logging
# middleware, mirroring src/lib/logger.ts's redactConfig and pino-http's
# default request-logging fields.

import structlog

from utils.logging import _redact_sensitive_data


def test_redacts_top_level_sensitive_keys():
    event = {
        "event": "login attempt",
        "password": "hunter2",
        "email": "user@example.com",
    }
    redacted = _redact_sensitive_data(None, "info", event)
    assert redacted["password"] == "[REDACTED]"
    assert redacted["email"] == "user@example.com"  # not sensitive, untouched


def test_redacts_nested_sensitive_keys_at_any_depth():
    event = {
        "event": "user created",
        "user": {
            "email": "user@example.com",
            "hashed_password": "$2b$12$...",
            "tokens": {"access_token": "abc.def.ghi", "refresh_token": "rawvalue"},
        },
    }
    redacted = _redact_sensitive_data(None, "info", event)
    assert redacted["user"]["hashed_password"] == "[REDACTED]"
    assert redacted["user"]["tokens"]["access_token"] == "[REDACTED]"
    assert redacted["user"]["tokens"]["refresh_token"] == "[REDACTED]"
    assert redacted["user"]["email"] == "user@example.com"


def test_redacts_sensitive_keys_inside_lists():
    event = {"event": "batch", "items": [{"token": "abc"}, {"ok": "fine"}]}
    redacted = _redact_sensitive_data(None, "info", event)
    assert redacted["items"][0]["token"] == "[REDACTED]"
    assert redacted["items"][1]["ok"] == "fine"


def test_redaction_key_matching_is_case_insensitive():
    event = {"AccessToken": "abc", "Authorization": "Bearer xyz"}
    redacted = _redact_sensitive_data(None, "info", event)
    assert redacted["AccessToken"] == "[REDACTED]"
    assert redacted["Authorization"] == "[REDACTED]"


def test_request_completed_log_includes_method_path_status_and_request_id(client):
    # capture_logs() replaces the whole configured processor chain for
    # its duration -- merge_contextvars must be passed explicitly or
    # request_id (bound via contextvars in log_requests) won't show up.
    with structlog.testing.capture_logs(
        processors=[structlog.contextvars.merge_contextvars]
    ) as captured:
        response = client.get("/health")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers

    request_logs = [c for c in captured if c.get("event") == "request_completed"]
    assert len(request_logs) == 1
    entry = request_logs[0]
    assert entry["method"] == "GET"
    assert entry["path"] == "/health"
    assert entry["status_code"] == 200
    assert "duration_ms" in entry
    assert "request_id" in entry
