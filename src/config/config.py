"""
Application Configuration Module.
This file handles loading and validating all environment variables (e.g., from a .env file).
It ensures that the application will not start if required secrets are missing.
"""

# ---------------------------------------------------------
# External Imports
# ---------------------------------------------------------
from pydantic_settings import BaseSettings, SettingsConfigDict

# ---------------------------------------------------------
# Internal Imports
# ---------------------------------------------------------
# (No internal imports for the config module)

class Settings(BaseSettings):
    # These values can be overridden by a local .env file or system environment variables
    PROJECT_NAME: str = "CDIS Template FastAPI"
    API_V1_STR: str = "/api/v1"
    
    # The connection string used to connect to the Database.
    # To switch databases, simply change the URL prefix! For example:
    # Postgres: "postgresql+psycopg2://user:password@localhost/dbname"
    # MongoDB:  "mongodb://user:password@localhost:27017/dbname" (Note: MongoDB requires an ODM like Beanie instead of SQLModel)
    DATABASE_URL: str = "mysql+pymysql://user:password@localhost/dbname"
    
    # Security / Auth settings
    # IMPORTANT: In production, change this to a securely generated random string and store it in .env
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"

    # Tell pydantic to read from a .env file if it exists, and ignore extra variables it doesn't recognize
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

# Instantiate a global settings object that can be imported anywhere in the app
settings = Settings()
