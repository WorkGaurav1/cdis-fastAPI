# Central error-handling registration.
#
# Mirrors back-end/src/middlewares/errorHandler.ts: every error path in the
# app — explicit `raise HTTPException(...)`, FastAPI's own automatic 404s
# and request-validation failures, and genuinely unexpected exceptions —
# must resolve to the same `{success:false,error:{code,message}}` envelope
# the frontend's `interceptors.ts` (`toApiError`) expects. Unhandled
# exceptions are logged in full server-side but only ever show the client a
# generic message, per OWASP guidance against leaking stack traces or
# internal details in error responses.

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from utils.apiResponse import send_error

logger = logging.getLogger("app.errors")

# Maps common HTTP status codes to the stable error "code" string used
# across the app/frontend contract. Falls back to a generic HTTP_<status>
# code for anything not explicitly listed here.
_STATUS_CODE_NAMES = {
    400: "VALIDATION_ERROR",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMIT_EXCEEDED",
}


def _code_for_status(status_code: int) -> str:
    return _STATUS_CODE_NAMES.get(status_code, f"HTTP_{status_code}")


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    # Covers every `raise HTTPException(...)` we raise ourselves, plus
    # FastAPI/Starlette's own automatic 404 for unmatched routes and 405
    # for unsupported methods — all of those are Starlette HTTPExceptions
    # too, so a single handler on the base class catches them all.
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    logger.warning(
        "HTTP %s on %s %s: %s",
        exc.status_code,
        request.method,
        request.url.path,
        message,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=send_error(_code_for_status(exc.status_code), message),
        headers=exc.headers,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # Pydantic request-validation failures. Same envelope shape as every
    # other error; message concatenates each field error, similar in
    # spirit to Node's Zod-backed `validateBody` middleware.
    message = "; ".join(
        f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()
    )
    logger.warning(
        "Validation error on %s %s: %s", request.method, request.url.path, message
    )
    return JSONResponse(
        # 422, spelled as a literal: Starlette has renamed the
        # HTTP_422_UNPROCESSABLE_ENTITY constant across versions
        # (currently HTTP_422_UNPROCESSABLE_CONTENT, deprecating the old
        # name), so a literal avoids depending on either spelling.
        status_code=422,
        content=send_error(_code_for_status(422), message),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Anything else is an unexpected programming error: logged in full
    # server-side (stack trace included), but the client only ever sees a
    # generic message.
    logger.error(
        "Unhandled error on %s %s", request.method, request.url.path, exc_info=exc
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=send_error(
            "INTERNAL_ERROR", "Something went wrong. Please try again later."
        ),
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
