import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import type { PropsWithChildren, ReactElement } from "react";

import { AuthContext } from "../context/AuthContext";
import type { AuthContextValue } from "../context/AuthContext";
import type { User } from "../types";
import { RequireAuth } from "./RequireAuth";

function renderWithAuth(value: AuthContextValue, initialPath = "/dashboard") {
  function AuthWrapper({ children }: PropsWithChildren): ReactElement {
    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
  }

  const router = createMemoryRouter(
    [
      { path: "/login", element: <p>Login Page</p> },
      {
        element: <RequireAuth />,
        children: [{ path: "/dashboard", element: <p>Protected Dashboard</p> }],
      },
    ],
    { initialEntries: [initialPath] },
  );

  return render(
    <AuthWrapper>
      <RouterProvider router={router} />
    </AuthWrapper>,
  );
}

const mockUser: User = { id: "u1", name: "Test", email: "test@example.com", roles: ["user"], permissions: [] };

describe("RequireAuth", () => {
  it("renders nothing while the session-restore check is still loading", () => {
    renderWithAuth({ user: null, isAuthenticated: false, loading: true, login: async () => {}, logout: async () => {} });

    expect(screen.queryByText("Protected Dashboard")).not.toBeInTheDocument();
    expect(screen.queryByText("Login Page")).not.toBeInTheDocument();
  });

  it("redirects to /login when not authenticated", async () => {
    renderWithAuth({ user: null, isAuthenticated: false, loading: false, login: async () => {}, logout: async () => {} });

    expect(await screen.findByText("Login Page")).toBeInTheDocument();
  });

  it("renders the protected route content when authenticated", async () => {
    renderWithAuth({
      user: mockUser,
      isAuthenticated: true,
      loading: false,
      login: async () => {},
      logout: async () => {},
    });

    expect(await screen.findByText("Protected Dashboard")).toBeInTheDocument();
  });
});
