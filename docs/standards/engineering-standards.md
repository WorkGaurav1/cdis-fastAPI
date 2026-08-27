# Engineering Standards

## Linting & Formatting
This project uses **Ruff**, an extremely fast Python linter.

- All Python code must comply with the `pyproject.toml` Ruff rules.
- Line length is capped at 88 characters.
- Imports are sorted automatically.

To run the linter:
```bash
ruff check .
```

## Security Standards
- Passwords must be hashed using `bcrypt` (`features/auth/security.py`).
- All tokens must be generated using an asymmetric or strong symmetric key (HS256 minimum).
- All API endpoints must be rate-limited to prevent brute-force attacks
  (a global baseline limiter, plus a stricter one on `/auth/login` keyed
  by IP + attempted email).
- Responses must not reveal internal database existence (e.g., preventing username enumeration).
- Refresh tokens are opaque, DB-backed, and rotate on every use, with
  reuse detection (`features/auth/service.py`).
- Authorization is permission-based (Role/Permission/UserRole/
  RolePermission), never by role name alone.
