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
- Passwords must be hashed using `bcrypt` via `passlib`.
- All tokens must be generated using an asymmetric or strong symmetric key (HS256 minimum).
- All API endpoints must be rate-limited to prevent brute-force attacks.
- Responses must not reveal internal database existence (e.g., preventing username enumeration).
