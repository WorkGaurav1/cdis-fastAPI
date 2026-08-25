# Database engine and session management.
#
# One process-wide engine (connection pool), a fresh Session per request
# via FastAPI's dependency injection -- mirrors the Node backend's
# src/lib/prisma.ts (one Prisma client instance, request-scoped queries).

from collections.abc import Generator

from sqlmodel import Session, create_engine

from config.config import settings

# pool_pre_ping guards against stale connections after the DB (or a
# container restart) silently drops idle ones -- without it, the first
# query on a dead connection fails instead of transparently reconnecting.
engine = create_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
