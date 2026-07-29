# Repository Explanation & Glossary

This document explains the architecture of the `cdis-template-fastapi` repository, detailing what every file does and defining key FastAPI terminology. Use this as your "cheat sheet" to answer any questions about the repository!

## Key Terminology Explained

### What is PEP 621?
PEP (Python Enhancement Proposal) 621 is the official standard for how Python projects should define their metadata and dependencies. Historically, Python used `setup.py` or `requirements.txt`. PEP 621 mandated that all of this configuration should be standardized in a single, easy-to-read file called `pyproject.toml`.

### What are FastAPI "Path Operations"?
In FastAPI, a "path operation" is just a fancy term for an API endpoint. 
- The **path** is the URL (e.g., `/users`).
- The **operation** is the HTTP method used (e.g., `GET`, `POST`, `PUT`, `DELETE`).
So, when you write `@router.get("/users")`, you are defining a "path operation."

### What are "Response Models"?
A response model is a Pydantic schema (or SQLModel) that dictates exactly what data your API is allowed to send back to the user. For example, if you set `response_model=UserResponse`, FastAPI will take the raw database object, automatically filter out the password (because the password isn't in `UserResponse`), and convert it to clean JSON before sending it to the client.

### What is "Router Inclusion"?
Instead of stuffing all your endpoints (users, products, orders) into one massive `main.py` file, FastAPI uses `APIRouter`. You create a separate router in a file like `endpoints/users.py`. Then, in `main.py`, you "include" that router (`app.include_router(users.router)`). This acts like a folder structure for your API, keeping the code modular and clean.

### What are "First Steps"?
"First steps" refers to the core initialization of a FastAPI application. It is the literal code required to get the app running: importing FastAPI, creating the `app = FastAPI()` object, and defining a simple root or health-check endpoint.

---

## File-by-File Breakdown

### The Application Core (`src/app/`)
*   **`main.py`**: The entrypoint of the application. It creates the FastAPI instance, mounts the `/api/v1` prefix, and attaches the routers.
*   **`core/config.py`**: Uses `pydantic-settings` to securely load and validate environment variables (like your `DATABASE_URL` and `PROJECT_NAME`).
*   **`api/v1/endpoints/users.py`**: Contains the actual API logic (path operations) for user-related actions, like fetching all users or creating a new user.
*   **`schemas/user.py`**: Contains `SQLModel` schemas that define the shape of data moving across the network (e.g., `UserCreate` for input, `UserResponse` for output).
*   **`models/user.py`**: Contains the `SQLModel` database definition (with `table=True`). This tells MySQL exactly what columns the `users` table should have.

### Infrastructure & DevOps
*   **`docker-compose.yml`**: A configuration file for Docker that lets developers spin up the API and a MySQL database locally with one command.
*   **`Dockerfile`**: The blueprint that tells Docker how to package the application into a minimal, secure container for production deployment.
*   **`pyproject.toml`**: The central configuration file (following PEP 621) that lists all Python dependencies and contains settings for tools like Ruff and Pytest.
*   **`.pre-commit-config.yaml`**: A Git hook configuration. It forces the `ruff` linter to run automatically every time a developer tries to `git commit`, preventing bad code from being saved.
*   **`justfile`**: A modern command runner (like a Makefile) that provides shortcuts like `just up` or `just lint` so developers don't have to memorize long terminal commands.

### Testing
*   **`tests/conftest.py`**: A setup file for Pytest. It creates a fake `TestClient` version of your app that the tests can use to simulate HTTP requests.
*   **`tests/test_users.py`**: The actual automated tests that verify your user endpoints are working correctly.

### CI/CD (Continuous Integration)
*   **`.github/workflows/lint-and-test.yml`**: A GitHub Actions script. It runs automatically in the cloud whenever someone opens a Pull Request, verifying that the code passes linting (Ruff) and testing (Pytest) before allowing the code to be merged.
