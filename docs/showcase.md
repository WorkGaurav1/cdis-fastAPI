# CDIS Application Showcase

This document details exactly how to perform a "Hot Swap" demonstration, proving to stakeholders that the new containerized FastAPI infrastructure acts as a perfect drop-in replacement for the original Node.js architecture.

## 1. Initial Setup (Node.js Backend)

First, demonstrate that the original architecture works as expected.

1.  **Start the Node Database:**
    *   Navigate to the `demo-repo/demo-repo` directory.
    *   Run `docker compose up -d mysql` to start the local MySQL container.
2.  **Start the Node Backend:**
    *   Navigate to `demo-repo/demo-repo/back-end`.
    *   Run `npm run dev` to start the Node server on port 4000.
3.  **Start the React Frontend:**
    *   Navigate to your frontend project.
    *   Ensure `.env` contains: `VITE_API_BASE_URL=http://localhost:4000/api/v1`
    *   Run `npm run dev`.
4.  **Demonstrate Application Flow:**
    *   Log in using the default credentials (`admin@example.com` / `password`).
    *   Open your browser's Developer Tools (F12) and go to the **Network** tab.
    *   Filter for `XHR` and click on an API request (e.g., `me` or `states`).
    *   Point out the **Request URL** in the Headers panel to prove it is communicating with `http://localhost:4000`.

## 2. The Hot Swap (Transition to FastAPI)

Next, transition the backend infrastructure live without shutting down the frontend.

1.  **Start the FastAPI Infrastructure:**
    *   Navigate to `cdis-template-fastapi`.
    *   Run `docker compose up -d`. This spins up the secure Apache Reverse Proxy and the FastAPI backend.
2.  **Repoint the Frontend:**
    *   Open your frontend's `.env` file.
    *   Change the API URL to point to the secure Apache Proxy:
        ```env
        VITE_API_BASE_URL=https://localhost/api/v1
        ```
    *   Save the file. React will automatically reload the application in the background.

## 3. Proving the Drop-in Replacement

Finally, demonstrate that the application continues to function identically, but is now communicating with the new infrastructure.

1.  **Re-Authenticate:**
    *   Because the backend infrastructure has changed, the user's session will be invalid.
    *   Log in again with `admin@example.com` / `password`.
2.  **Show the New Traffic Flow:**
    *   Ensure your browser's **Network** tab is still open and filtered to `XHR`.
    *   Click on a new API request (e.g., `me` or `states`).
    *   Point out the new **Request URL** in the Headers panel.
    *   It will now read `https://localhost/api/v1/...`.
    *   This proves that the frontend is now securely routing traffic through the Apache Proxy into the new Python/FastAPI environment, while the user experience remains completely unchanged.
