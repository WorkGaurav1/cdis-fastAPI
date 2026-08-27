# Main Application Entrypoint.

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware

from app.limiter import limiter
from config.config import settings
from features.auth import api as auth
from features.demo import api as demo
from features.users import api as users
from utils.error_handlers import register_error_handlers
from utils.logging import configure_logging, log_requests

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
def health_check():
    """
    Standard health check endpoint.
    Used by load balancers and container orchestrators (like Docker/
    Kubernetes) to verify the server is running.
    """
    return {"status": "ok"}
