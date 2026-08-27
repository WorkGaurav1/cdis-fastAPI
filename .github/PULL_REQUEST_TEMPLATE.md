## What changed and why

<!-- One or two sentences. Focus on why, not just what — the diff already shows what. -->

## Checklist

- [ ] `ruff check . && ruff format --check . && pyright src && pytest` passes locally
- [ ] Added/updated tests for the change
- [ ] If a schema change: Alembic migration committed under `alembic/versions/`
- [ ] If touching auth/security-sensitive code: verified against real MySQL
      (`TEST_DB_BACKEND=mysql`), not just SQLite

## How to verify

<!-- Exact commands/steps a reviewer can run to confirm this works. -->
