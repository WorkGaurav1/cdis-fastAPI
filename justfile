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
