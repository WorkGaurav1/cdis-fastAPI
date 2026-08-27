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
# then commit both lock files. --allow-unsafe is required: pip-tools
# (a dev dependency, needed to run this very command) transitively
# depends on pip itself, and `pip install --require-hashes` refuses to
# proceed at all if pip/setuptools are left unpinned.
lock:
    pip-compile --generate-hashes --allow-unsafe pyproject.toml -o requirements.lock
    pip-compile --extra=dev --generate-hashes --allow-unsafe pyproject.toml -o requirements-dev.lock

# Checks both lock files for known vulnerabilities (OSV + PyPI advisory
# data), mirroring the Node backend's `npm audit --audit-level=high`.
audit:
    pip-audit -r requirements.lock
    pip-audit -r requirements-dev.lock
