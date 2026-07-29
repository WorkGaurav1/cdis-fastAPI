# CDIS Template FastAPI 🚀

Welcome to the **CDIS Standard Template for FastAPI Applications**. This repository serves as the foundational boilerplate for building highly secure, production-grade, and scalable backend services within the organization.

It enforces a strict, modular architecture designed for developer productivity, convention over configuration, and security by default.

---

## 🛠 Technologies Used

This template is built on the shoulders of industry giants, utilizing the most modern and robust Python tooling available:

*   **[FastAPI](https://fastapi.tiangolo.com/):** The core web framework. Exceptionally fast, highly intuitive, and automatically generates interactive API documentation.
*   **[SQLModel](https://sqlmodel.tiangolo.com/):** Combines the power of **SQLAlchemy** (for database interactions) and **Pydantic** (for data validation) into a single, seamless developer experience.
*   **[MySQL 8.0](https://www.mysql.com/):** The robust, enterprise-ready relational database powering the backend.
*   **[Docker](https://www.docker.com/) & Compose:** Fully containerized for instant local development and minimal-footprint production deployments.
*   **[Pytest](https://docs.pytest.org/):** The industry-standard testing framework, pre-configured for automated API endpoint testing.
*   **[Ruff](https://docs.astral.sh/ruff/):** An extremely fast Python linter and formatter that automatically enforces PEP 8 styling.

---

## 🚀 Getting Started (Local Development)

We believe in **Developer Experience First**. You do not need to install Python, configure virtual environments, or set up local databases to start working on this project. 

### Prerequisites
1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Running)
2. [Just](https://github.com/casey/just) (A modern command runner)

### 1. Start the Environment
To spin up the MySQL database and the FastAPI server, simply run:
```bash
just up
```
*(This triggers `docker compose up --build`. The server will automatically hot-reload whenever you save a Python file!)*

### 2. View the Interactive Documentation
Once the server is running, FastAPI automatically generates documentation for you. Open your browser and navigate to:
*   **Swagger UI (Interactive):** [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs) - *Use this to test endpoints directly in your browser.*
*   **ReDoc (Reading):** [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)

### 3. Run the Automated Tests
To verify that everything is working correctly without affecting your local database, run:
```bash
just test
```
*(This triggers Pytest using a specialized TestClient).*

### 4. Format and Lint Your Code
Before submitting a Pull Request, ensure your code follows the PEP 8 standard. Run:
```bash
just lint
```
*(Note: A pre-commit hook is also configured to run this automatically whenever you type `git commit`).*

### 5. Stop the Environment
When you are done for the day, spin down the containers gracefully:
```bash
just down
```

---

## 📚 Further Reading

If you are new to this repository or want to understand *why* things are built the way they are, please read our internal documentation:

*   🔗 **[Official References](docs/REFERENCES.md)**: Links to the exact tutorials and official documentation that inspired this codebase.
