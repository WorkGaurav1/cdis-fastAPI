# System Architecture

This backend is built using a **Feature-Based Architecture** (also known as Domain-Driven Design) rather than a traditional Layered Architecture.

## Core Technologies
- **Framework**: FastAPI (Python)
- **Database ORM**: SQLModel (SQLAlchemy)
- **Database Engine**: MySQL
- **Authentication**: JWT (JSON Web Tokens) with Secure HTTP-Only Cookies
- **Rate Limiting**: SlowAPI

## Why Feature-Based?
Unlike traditional architectures that group files by *type* (e.g., all models in one folder, all routers in another), this architecture groups files by *feature* (e.g., `src/features/users/`).
This significantly reduces cognitive load and makes the backend perfectly modular. If a feature needs to be removed, you simply delete its folder.
