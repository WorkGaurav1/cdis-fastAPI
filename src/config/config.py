# Application Configuration Module.

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # These values can be overridden by a local .env file or system
    # environment variables.
    PROJECT_NAME: str = "CDIS Template FastAPI"
    API_V1_STR: str = "/api/v1"

    # Mirrors the Node backend's NODE_ENV (src/config/env.ts): defaults to
    # "development" if unset, same as Node's `process.env["NODE_ENV"] ??
    # "development"", and pydantic rejects anything outside these four
    # values the same way Node's explicit check does. Cookie `secure`
    # (below) and other environment-conditional behavior key off this.
    ENVIRONMENT: Literal["development", "test", "staging", "production"] = "development"

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

    # Token/cookie lifetimes. Not secrets, so a sane default (matching the
    # Node backend's .env.example defaults) is fine here rather than
    # requiring every deployment to set them explicitly. Both the JWT's
    # own expiry and its cookie's max-age are derived from the same
    # setting (see features/auth/cookies.py) so they can't drift apart --
    # see docs/parity-notes.md for the Node-side bug this specifically
    # avoids repeating.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Account lockout (matches the Node backend's .env.example defaults:
    # ACCOUNT_LOCKOUT_MAX_ATTEMPTS=5, ACCOUNT_LOCKOUT_DURATION_MINUTES=15).
    LOCKOUT_MAX_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15

    # Tell pydantic to read from a .env file if it exists, and ignore
    # extra variables it doesn't recognize.
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )


# Instantiate a global settings object that can be imported anywhere in the app
settings = Settings()
