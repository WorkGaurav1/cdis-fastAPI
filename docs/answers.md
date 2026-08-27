# Q&A / Interview Prep Guide

This document contains answers to common technical questions you might face during your presentation regarding the architecture and design decisions of this FastAPI project.

## 1. Why did you choose Ruff?
**Answer:** Ruff is an extremely fast Python linter and code formatter written in Rust. We chose it because it replaces multiple legacy tools (like Flake8, Black, isort, and Bandit) with a single, unified tool. It runs 10-100x faster than those older tools, significantly speeding up our CI/CD pipelines and developer workflow while enforcing strict code quality standards.

## 2. Why did you use SQLModel?
**Answer:** SQLModel is an ORM (Object-Relational Mapper) built by the creator of FastAPI. It brilliantly combines **SQLAlchemy** (the industry standard for Python database interaction) with **Pydantic** (the standard for data validation). By using SQLModel, we avoid writing duplicate code—we can use the exact same classes to validate incoming API requests and define our database tables, drastically reducing boilerplate and maintenance overhead.

## 3. What is Pydantic and what does it do?
**Answer:** Pydantic is a data validation and settings management library using Python type annotations. In our API, it guarantees that incoming data exactly matches our expected formats (e.g., ensuring an email field actually contains a valid email string, or an age is an integer). If the data is wrong, Pydantic automatically rejects the request with a helpful error message before the bad data can ever touch our business logic.

## 4. What is CORS and why is it required?
**Answer:** CORS (Cross-Origin Resource Sharing) is a browser security feature. By default, browsers prevent a website running on one domain (e.g., `http://localhost:5173`) from making API requests to a completely different domain (e.g., `http://localhost:8000`) to prevent malicious scripts from stealing data. We explicitly configure CORS in FastAPI to tell the browser: *"It is safe to allow our specific React frontend to communicate with this backend."*

## 5. What is the TRACE method and why is it dangerous?
**Answer:** TRACE is an HTTP method originally used for debugging network connections; it echoes back the exact request it received. However, it is dangerous because hackers can use it to perform **Cross-Site Tracing (XST)** attacks. If an attacker tricks a user's browser into sending a TRACE request, the server will echo back the user's secure HttpOnly session cookies, allowing the attacker to steal them. Disabling TRACE entirely neutralizes this risk.

## 6. Why do ServerTokens need to be disabled?
**Answer:** By default, web servers like Apache will include a "Server" header in their HTTP responses (e.g., `Server: Apache/2.4.41 (Ubuntu)`). This is called a Server Token. It is considered an information leak. If a hacker knows exactly what version of Apache and which OS you are running, they can easily look up known vulnerabilities for that specific version. Disabling it (`ServerTokens Prod`) hides this information, forcing attackers to guess.

## 7. What is the purpose of the `demo` folder inside `src`, and what do its files do?
**Answer:** The `demo` folder isolates the synthetic showcase data used for this template's map/chart/table gallery pages -- it's real, DB-backed data (seeded via `scripts/seed.py`, migrated via Alembic like every other table), not hardcoded in the route handlers.
*   **`api.py`**: The API endpoints (`/demo/map/states`, `/demo/charts`, `/demo/tables`) that serve this data to the React dashboard.
*   **`models.py`** / **`repository.py`**: The SQLModel tables and queries backing it (36 states/UTs, 8 chart datasets, 3 table datasets).
*   **`seed_data.py`**: The dataset definitions and randomized-value generation the seed script uses.

Because it's isolated in its own feature module, it can still be safely deleted once you replace it with real project data, without affecting the rest of the application.

## 8. What is the purpose of the `utils` folder?
**Answer:** The `utils` folder is for shared, reusable helper functions that don't belong to any specific feature (like Auth or Users). 
*   For example, `apiResponse.py` lives here. It contains the `send_success` and `send_error` functions that guarantee every single API endpoint throughout the entire backend returns data in the exact same `{ success: true, data: {} }` JSON format that our React frontend expects.

## 9. What is the purpose of the `tests` folder?
**Answer:** The `tests` folder contains automated test scripts (using `pytest`). These scripts programmatically simulate a user interacting with the backend (e.g., trying to log in with a bad password, or fetching data). Before deploying any new code to production, we run these tests to automatically verify that everything still works and that we haven't accidentally broken existing features.

## 10. How does the uth folder work and what does it do?
**Answer:** The uth folder is a modular feature directory dedicated entirely to handling user authentication and sessions.
*   **pi.py**: Defines the HTTP endpoints (/login, /logout, /me). When a user logs in successfully, this file generates a JWT (JSON Web Token) and securely attaches it to the user's browser using **HttpOnly Cookies** (which protects the token from being stolen by malicious JavaScript).
*   **security.py**: Handles all the cryptography. It uses crypt to verify hashed passwords against what is stored in the database, and it handles the cryptographical signing of the JWT session tokens.
*   **schemas.py**: Uses Pydantic to strictly define the required shape of a login request (e.g., demanding a valid email format and a password string).

## 11. Is everything automatically linted when you do a commit?
**Answer:** Yes! The project comes with a .pre-commit-config.yaml file specifically configured for **Ruff**. As long as developers run pre-commit install once when they first clone the repository, Git will automatically intercept every git commit they make. Before it actually saves the commit, it will run Ruff to strictly format the code and fix any linting errors. If their code has serious errors that Ruff can't auto-fix, the commit will be completely blocked until the developer fixes the bad code.
