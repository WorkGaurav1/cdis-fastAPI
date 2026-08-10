import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import type { PropsWithChildren, ReactElement } from "react";

import { AuthContext } from "../context/AuthContext";
import type { AuthContextValue } from "../context/AuthContext";
import type { User } from "../types";
import { RequirePermission } from "./RequirePermission";

function renderWithUser(user: User | null) {
  const value: AuthContextValue = {
    user,
    isAuthenticated: user !== null,
    loading: false,
    login: async () => {},
    logout: async () => {},
  };

  function AuthWrapper({ children }: PropsWithChildren): ReactElement {
    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
  }

  const router = createMemoryRouter(
    [
      { path: "/forbidden", element: <p>Forbidden Page</p> },
      {
        element: <RequirePermission permission="users:read" />,
        children: [{ path: "/users", element: <p>Users Page</p> }],
      },
    ],
    { initialEntries: ["/users"] },
  );

  return render(
    <AuthWrapper>
      <RouterProvider router={router} />
    </AuthWrapper>,
  );
}

describe("RequirePermission", () => {
  it("redirects to /forbidden when the user lacks the required permission", async () => {
    renderWithUser({ id: "u1", name: "Test", email: "test@example.com", roles: ["user"], permissions: [] });

    expect(await screen.findByText("Forbidden Page")).toBeInTheDocument();
  });

  it("redirects to /forbidden when there is no user at all", async () => {
    renderWithUser(null);

    expect(await screen.findByText("Forbidden Page")).toBeInTheDocument();
  });

  it("renders the route content when the user has the required permission", async () => {
    renderWithUser({
      id: "u1",
      name: "Test",
      email: "test@example.com",
      roles: ["manager"],
      permissions: ["users:read"],
    });

    expect(await screen.findByText("Users Page")).toBeInTheDocument();
  });
});
