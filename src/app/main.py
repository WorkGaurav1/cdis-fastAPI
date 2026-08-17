# Main Application Entrypoint.

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from config.config import settings
from app.limiter import limiter
from features.users import api as users
from features.auth import api as auth
from features.demo import api as demo

# Initialize the core FastAPI web application using settings from our config file
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS (Frontend Interoperability)
# This allows the React/Vite frontend (running on ports 5173 or 3000) 
# to securely communicate with this FastAPI backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security & Rate Limiting (VAPT Requirements)
# Attach Rate Limiter to the app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    # Middleware to globally inject security headers to satisfy VAPT Task 1.5.
    response = await call_next(request)
    # Relaxed CSP to allow FastAPI's Swagger UI to load its external JS/CSS from jsdelivr
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
    Used by load balancers and container orchestrators (like Docker/Kubernetes) to verify the server is running.
    """
    return {"status": "ok"}

