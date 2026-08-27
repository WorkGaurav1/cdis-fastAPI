# CDIS Engineering Template (Python/FastAPI)

Production-ready backend engineering template for building secure, scalable, and maintainable web applications using standardized Python engineering practices. This backend is designed to be fully modular and interoperable with the CDIS React/Vite Frontend.

---

## Features

- **Framework**: Python + FastAPI
- **Database**: MySQL + SQLModel (SQLAlchemy), migrations via Alembic
- **Authentication**: JWT access tokens + opaque, DB-backed, rotating
  refresh tokens (reuse detection included) in Secure HttpOnly cookies;
  account lockout after repeated failed logins
- **Authorization**: Permission-based RBAC (Role/Permission/UserRole/
  RolePermission) -- routes declare a required permission, never a role
  name
- **Security**: Double-submit CSRF, global + per-endpoint rate
  limiting, strict CSP middleware (VAPT Compliant), structured JSON
  logging with credential/token redaction
- **Testing**: pytest, 85%+ coverage enforced, Pyright type-checked
- **Linting**: Ruff
- **Infrastructure**: Docker & Docker Compose, non-root runtime, container healthcheck
- **Architecture**: Domain-Driven / Feature-Based Modularity

---

## Repository Structure

```
.
├── apache/         # Apache2 Reverse Proxy & WAF (Planned Phase 2)
├── docs/           # Engineering documentation
├── src/            # FastAPI Python application codebase
│   ├── app/        # Core app initialization and global middleware
│   ├── config/     # Environment and Database configuration
│   └── features/   # Modular, domain-driven API routes (e.g., users, auth)
├── pyproject.toml  # Python dependencies and Ruff configuration
├── Dockerfile      # Python container build instructions
└── docker-compose.yml
```

---

## Prerequisites

- Git
- Docker
- Docker Compose
- *Note: You do not need to install Python locally, as the entire environment runs inside Docker.*

---

## Bootstrap

### Clone Repository

```bash
git clone <repository-url>
cd cdis-template-fastapi
```

### Start Database & Backend

This command will automatically download the MySQL image, build the Python FastAPI image, install all `pyproject.toml` dependencies natively, and start the hot-reloading server:

```bash
docker compose up -d --build
```

### Apply Migrations & Seed Data

The database schema (users, refresh tokens, roles/permissions, demo
data) is managed by Alembic, not created automatically on boot. After
the containers are up, apply migrations and seed roles/permissions,
default accounts, and demo/showcase data:

```bash
docker compose exec api alembic upgrade head
docker compose exec api python -m scripts.seed
```

Both are safe to re-run (`alembic upgrade head` is a no-op once up to
date; the seed script upserts roles/permissions/demo data and skips
any user email that already exists). The seed script creates three
default accounts, each holding the role matching its name, all with
password `password`:

| Email | Role | Permissions |
|---|---|---|
| `admin@example.com` | admin | `users:read`, `users:write`, `roles:manage` |
| `manager@example.com` | manager | `users:read` |
| `user@example.com` | user | *(none)* |

### Accessing the Server

Once running, the interactive Swagger documentation is instantly available at:
👉 `http://localhost:8000/docs`

### Running Tests, Lint, and Type Checking Locally

```bash
just lint       # ruff check + ruff format
just typecheck  # pyright
just test       # pytest, with coverage enforced (85% floor)
```

(Requires a local Python environment with `pip install -e .[dev]` --
see `justfile` for the exact commands if you don't use `just`.)

---

## Documentation

| Document | Purpose |
|----------|---------|
| `docs/architecture/system-architecture.md` | System architecture & ORM explanations |
| `docs/standards/engineering-standards.md` | Python linting (Ruff) and Security standards |
| `docs/development/adding-feature.md` | Workflow for adding new API routes modularly |
| `docs/random/` | Legacy and VAPT audit documentation |

---

## References

- FastAPI — https://fastapi.tiangolo.com/
- SQLModel — https://sqlmodel.tiangolo.com/
- Ruff — https://docs.astral.sh/ruff/
- Docker — https://docs.docker.com/
- OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/
