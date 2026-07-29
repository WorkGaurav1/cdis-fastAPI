# Blueprint Architecture References

This document outlines the official documentation, standard templates, and community best practices that informed the architecture and specific code structures within this repository. 

None of the code in this boilerplate is arbitrary; it is synthesized directly from the recommendations of the creators of these tools.

## 1. Overall Project Structure (`src/` layout)
The `src/app` separation, along with splitting `api/`, `core/`, `models/`, and `schemas/`, is the widely accepted standard for production FastAPI applications.
*   **Tiangolo's Official Full-Stack Template:** [https://github.com/tiangolo/full-stack-fastapi-template](https://github.com/tiangolo/full-stack-fastapi-template)
*   **FastAPI Docs (Bigger Applications):** [https://fastapi.tiangolo.com/tutorial/bigger-applications/](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
*   **Python Packaging Authority (The `src` layout):** [https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)

## 2. Configuration (`src/app/core/config.py`)
The use of `pydantic-settings` with `BaseSettings` and `SettingsConfigDict` to load environment variables and validate settings is the official approach recommended by both Pydantic v2 and FastAPI.
*   **Pydantic Settings Documentation:** [https://docs.pydantic.dev/latest/concepts/pydantic_settings/](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
*   **FastAPI Advanced Settings:** [https://fastapi.tiangolo.com/advanced/settings/](https://fastapi.tiangolo.com/advanced/settings/)

## 3. Application Entrypoint (`src/app/main.py`)
The initialization of the `FastAPI` app, the inclusion of `APIRouter`s, and the standard `/health` endpoint are standard practices taught in the FastAPI introductory tutorials.
*   **FastAPI First Steps:** [https://fastapi.tiangolo.com/tutorial/first-steps/](https://fastapi.tiangolo.com/tutorial/first-steps/)
*   **FastAPI Router Inclusion:** [https://fastapi.tiangolo.com/tutorial/bigger-applications/#include-an-apirouter-with-a-custom-prefix-tags-responses-and-dependencies](https://fastapi.tiangolo.com/tutorial/bigger-applications/#include-an-apirouter-with-a-custom-prefix-tags-responses-and-dependencies)

## 4. Models and Schemas (`src/app/models/user.py` & `src/app/schemas/user.py`)
The code structure unifying Pydantic data validation with SQLAlchemy ORM models using `SQLModel` comes directly from the SQLModel official tutorial. The use of a `Base` class with `table=True` for the database model is a hallmark of SQLModel design.
*   **SQLModel Main Tutorial:** [https://sqlmodel.tiangolo.com/tutorial/](https://sqlmodel.tiangolo.com/tutorial/)
*   **SQLModel with FastAPI:** [https://sqlmodel.tiangolo.com/tutorial/fastapi/](https://sqlmodel.tiangolo.com/tutorial/fastapi/)

## 5. Endpoints (`src/app/api/v1/endpoints/users.py`)
The definition of HTTP verbs (`@router.get`, `@router.post`), dependency injection, and `response_model` enforcement comes from the FastAPI routing guides.
*   **FastAPI Path Operations:** [https://fastapi.tiangolo.com/tutorial/path-params/](https://fastapi.tiangolo.com/tutorial/path-params/)
*   **FastAPI Response Models:** [https://fastapi.tiangolo.com/tutorial/response-model/](https://fastapi.tiangolo.com/tutorial/response-model/)

## 6. Testing Framework (`tests/conftest.py` & `tests/test_users.py`)
The use of `conftest.py` to yield a `TestClient` generator is the official testing strategy for FastAPI applications, relying on Pytest fixtures.
*   **FastAPI Testing Docs:** [https://fastapi.tiangolo.com/tutorial/testing/](https://fastapi.tiangolo.com/tutorial/testing/)
*   **Pytest Fixtures:** [https://docs.pytest.org/en/7.1.x/reference/fixtures.html](https://docs.pytest.org/en/7.1.x/reference/fixtures.html)

## 7. Dockerization (`Dockerfile` & `docker-compose.yml`)
The multi-stage `Dockerfile` (using a `builder` stage to compile wheels and a clean `final` stage) and the local volume-mapped `docker-compose.yml` for hot-reloading are industry-standard DevOps patterns for Python web servers.
*   **FastAPI Docker Deployment:** [https://fastapi.tiangolo.com/deployment/docker/](https://fastapi.tiangolo.com/deployment/docker/)
*   **Docker Multi-stage Builds:** [https://docs.docker.com/build/building/multi-stage/](https://docs.docker.com/build/building/multi-stage/)

## 8. Code Quality (`pyproject.toml` & `.pre-commit-config.yaml`)
Consolidating dependencies and configurations (like Ruff and Pytest) into `pyproject.toml` is the modern Python standard (PEP 621). The use of Pre-commit hooks for Ruff formatting guarantees adherence to PEP 8 before code reaches the repository.
*   **Ruff Official Docs:** [https://docs.astral.sh/ruff/](https://docs.astral.sh/ruff/)
*   **Pre-commit Official Docs:** [https://pre-commit.com/](https://pre-commit.com/)
*   **Python PEP 621 (pyproject.toml):** [https://peps.python.org/pep-0621/](https://peps.python.org/pep-0621/)
*   **Python PEP 8 (Style Guide):** [https://peps.python.org/pep-0008/](https://peps.python.org/pep-0008/)

## 9. CI/CD (`.github/workflows/lint-and-test.yml`)
The GitHub Actions workflow syntax for checking out code, setting up Python, installing dependencies, and running Pytest/Ruff is directly adapted from the official GitHub Actions Python templates.
*   **GitHub Actions for Python:** [https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)
