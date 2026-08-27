# Main Application Entrypoint.

import time
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text
from sqlmodel import Session

from app.limiter import limiter
from config.config import settings
from config.database import get_session
from features.auth import api as auth
from features.demo import api as demo
from features.users import api as users
from utils.apiResponse import send_success
from utils.error_handlers import register_error_handlers
from utils.logging import configure_logging, log_requests

_process_started_at = time.monotonic()

# Structured logging (JSON in prod/staging, console in dev, silent in
# test) with credential/token redaction -- see utils/logging.py. Must
# run before anything else logs, so the root logger's handlers are
# already in place.
configure_logging()

# Initialize the core FastAPI web application using settings from our config file
app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# One structured log line per request (method/path/status/duration/request
# id) -- mirrors src/app.ts's `pinoHttp({ logger })`.
app.middleware("http")(log_requests)

# Central error handling — every error path (raised HTTPExceptions,
# FastAPI's own 404/405s, request-validation failures, unhandled
# exceptions) resolves to the same {success:false,error:{code,message}}
# envelope used on the success path. Must be registered before routes are
# exercised, but registration order relative to `include_router` below
# doesn't matter to FastAPI.
register_error_handlers(app)

# CORS (Frontend Interoperability)
# Origin(s) come from settings.CORS_ORIGINS (config/config.py) --
# configurable per environment via the CORS_ORIGINS env var, rather than
# hardcoded here. credentials=True since authentication uses HttpOnly
# cookies, mirroring the Node backend's src/app.ts.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security & Rate Limiting (VAPT Requirements)
# Attach Rate Limiter to the app. SlowAPIMiddleware is what actually
# enforces limiter.default_limits (app/limiter.py) on routes that don't
# have their own @limiter.limit(...) -- without it, only explicitly
# decorated routes (like /auth/login) were ever throttled at all. The
# RateLimitExceeded -> {success,error} envelope handler is registered
# by register_error_handlers() above, alongside every other error path.
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    # Middleware to globally inject security headers to satisfy VAPT Task 1.5.
    response = await call_next(request)
    # Relaxed CSP to allow FastAPI's Swagger UI to load its external
    # JS/CSS from jsdelivr
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https://fastapi.tiangolo.com; "
        "frame-ancestors 'none'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# Feature Routers
# Attach feature routers to the main app, automatically prefixing all URLs
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(demo.router, prefix=f"{settings.API_V1_STR}/demo", tags=["demo"])


@app.get("/health", tags=["health"])
def health_check(session: Session = Depends(get_session)):
    """
    Liveness + readiness check, mirroring the Node backend's
    src/controllers/health.controller.ts exactly: verifies the process
    is up AND that the database is actually reachable (a real `SELECT
    1`, not a liveness-only ping), so this can be wired into container
    orchestration health checks as a genuine readiness probe. If the DB
    query raises, that propagates to the global exception handler
    (utils/error_handlers.py) and becomes a 500 -- the same fallback
    Express 5 gives Node's version, which has no try/catch of its own
    either.
    """
    # .execute(), not .exec(): SQLModel's Session.exec() is typed only
    # for statement-returning ORM queries (select()), not a raw
    # TextClause -- .execute() is the underlying SQLAlchemy Session
    # method both inherit, and is correctly typed for this.
    session.execute(text("SELECT 1"))
    return send_success(
        {
            "status": "ok",
            "uptimeSeconds": round(time.monotonic() - _process_started_at),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
