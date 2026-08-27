up:
    docker compose up --build

down:
    docker compose down

lint:
    ruff check .
    ruff format .

typecheck:
    pyright --pythonpath "$(command -v python)" src

test:
    pytest

# Regenerates requirements.lock / requirements-dev.lock from
# pyproject.toml's dependencies. Run this after changing dependencies,
# then commit both lock files.
lock:
    pip-compile --generate-hashes pyproject.toml -o requirements.lock
    pip-compile --extra=dev --generate-hashes pyproject.toml -o requirements-dev.lock
