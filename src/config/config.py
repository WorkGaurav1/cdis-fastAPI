# Application Configuration Module.

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # These values can be overridden by a local .env file or system
    # environment variables.
    PROJECT_NAME: str = "CDIS Template FastAPI"
    API_V1_STR: str = "/api/v1"

    # The connection string used to connect to the Database.
    # To switch databases, simply change the URL prefix! For example:
    # Postgres: "postgresql+psycopg2://user:password@localhost/dbname"
    # MongoDB:  "mongodb://user:password@localhost:27017/dbname"
    # (Note: MongoDB requires an ODM like Beanie instead of SQLModel)
    #
    # No default on purpose (fail-fast, mirroring the Node backend's
    # src/config/env.ts, which requires every var unconditionally rather
    # than silently falling back): copy .env.example to .env and fill
    # this in for local development; set it as a real environment
    # variable in every other environment.
    DATABASE_URL: str

    # Security / Auth settings.
    #
    # No default on purpose — a checked-in fallback secret is a real
    # security hole (anyone with repo access could forge tokens for any
    # deployment that forgot to override it). Generate a unique,
    # securely-random value per environment; never reuse the value from
    # .env.example.
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # Tell pydantic to read from a .env file if it exists, and ignore
    # extra variables it doesn't recognize.
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )


# Instantiate a global settings object that can be imported anywhere in the app
settings = Settings()
