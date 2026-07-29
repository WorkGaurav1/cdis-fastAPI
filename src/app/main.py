from fastapi import FastAPI
from features.users import api as users
from config.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])

@app.get("/health", tags=["health"])
def health_check():
    """
    Standard health check endpoint.
    """
    return {"status": "ok"}
