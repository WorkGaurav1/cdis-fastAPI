"""
Main Application Entrypoint.
This file is responsible for initializing the FastAPI app, configuring global settings,
and attaching the individual feature routers (like users, auth, etc.) to the main application hub.
"""

# ---------------------------------------------------------
# External Imports
# ---------------------------------------------------------
from fastapi import FastAPI

# ---------------------------------------------------------
# Internal Imports
# ---------------------------------------------------------
from config.config import settings
from features.users import api as users

# Initialize the core FastAPI web application using settings from our config file
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Attach the 'users' feature router to the main app, automatically prefixing all its URLs
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])

@app.get("/health", tags=["health"])
def health_check():
    """
    Standard health check endpoint.
    Used by load balancers and container orchestrators (like Docker/Kubernetes) to verify the server is running.
    """
    return {"status": "ok"}
