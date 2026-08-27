# Structured application logging -- mirrors src/lib/logger.ts's pino
# config: JSON output in production/staging, a readable colorized
# console in development, effectively silent during the test suite
# (deliberately-exercised error paths -- 401s, 403s, locked accounts --
# are noise there, not signal). A redaction processor censors
# credentials/tokens/cookies wherever they appear in a logged payload,
# matching lib/logger.ts's redactConfig, and applies to every log call
# in the app -- both structlog-native calls and plain stdlib
# `logging.getLogger(...)` calls (e.g. utils/error_handlers.py) --
# since both are routed through the same processor chain below.

import logging
import sys
import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from fastapi import Request, Response

from config.config import settings

# Mirrors src/lib/logger.ts's redactConfig.paths -- the bare key names
# it lists (password, passwordHash, accessToken, refreshToken, token),
# plus this app's own field-naming (hashed_password, csrf_token,
# secret_key) and the request/response header names Node also redacts
# (authorization, cookie, set-cookie). Matched case-insensitively so it
# catches a field regardless of which casing convention logged it.
_REDACT_KEYS = frozenset(
    {
        "password",
        "passwordhash",
        "hashed_password",
        "accesstoken",
        "access_token",
        "refreshtoken",
        "refresh_token",
        "token",
        "token_hash",
        "csrf_token",
        "secret_key",
        "authorization",
        "cookie",
        "set-cookie",
    }
)


def _scrub(value):
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if str(key).lower() in _REDACT_KEYS else _scrub(val)
            for key, val in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_scrub(item) for item in value]
    return value


def _redact_sensitive_data(logger, method_name, event_dict):
    """
    structlog processor: recursively censors any key matching
    _REDACT_KEYS, anywhere in the logged event -- not just top-level,
    since a whole request body or user object can end up logged as one
    nested value.
    """
    return _scrub(event_dict)


def _log_level() -> int:
    if settings.ENVIRONMENT == "test":
        return logging.CRITICAL + 1  # effectively silent, mirrors pino's "silent"
    if settings.ENVIRONMENT == "development":
        return logging.DEBUG
    return logging.INFO


def configure_logging() -> None:
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.format_exc_info,
        _redact_sensitive_data,
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    renderer = (
        structlog.dev.ConsoleRenderer()
        if settings.ENVIRONMENT == "development"
        else structlog.processors.JSONRenderer()
    )

    # foreign_pre_chain applies shared_processors (redaction included) to
    # plain stdlib `logging.getLogger(...)` calls too -- not just
    # structlog-native ones -- so uvicorn's own loggers and
    # utils/error_handlers.py's logger get the same treatment.
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(_log_level())


request_logger = structlog.get_logger("app.request")


async def log_requests(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """
    FastAPI HTTP middleware logging one line per request: method, path,
    status, duration, and a request id -- mirrors pino-http's default
    fields (src/app.ts's `pinoHttp({ logger })`). The request id is bound
    into structlog's contextvars for the duration of the request, so any
    other log call made while handling it (e.g. error_handlers.py's
    warnings) automatically carries the same id without having to thread
    it through every function call by hand.
    """
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)

    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)

    request_logger.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
    )
    response.headers["X-Request-ID"] = request_id
    return response
