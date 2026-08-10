import { describe, expect, it } from "vitest";
import { renderHook } from "@testing-library/react";
import type { PropsWithChildren, ReactElement } from "react";

import { AuthContext } from "../context/AuthContext";
import type { AuthContextValue } from "../context/AuthContext";
import type { User } from "../types";
import { hasPermission, usePermission } from "./usePermission";

function makeUser(permissions: string[]): User {
  return { id: "u1", name: "Test User", email: "test@example.com", roles: ["user"], permissions };
}

function wrapperWithUser(user: User | null) {
  const value: AuthContextValue = {
    user,
    isAuthenticated: user !== null,
    loading: false,
    login: async () => {},
    logout: async () => {},
  };

  return function Wrapper({ children }: PropsWithChildren): ReactElement {
    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
  };
}

describe("usePermission", () => {
  it("returns false when there is no authenticated user", () => {
    const { result } = renderHook(() => usePermission("users:read"), { wrapper: wrapperWithUser(null) });

    expect(result.current).toBe(false);
  });

  it("returns true when the user has the exact permission", () => {
    const { result } = renderHook(() => usePermission("users:read"), {
      wrapper: wrapperWithUser(makeUser(["users:read"])),
    });

    expect(result.current).toBe(true);
  });

  it("returns false when the user lacks the permission", () => {
    const { result } = renderHook(() => usePermission("users:write"), {
      wrapper: wrapperWithUser(makeUser(["users:read"])),
    });

    expect(result.current).toBe(false);
  });

  it("returns true if the user has at least one of several required permissions", () => {
    const { result } = renderHook(() => usePermission(["roles:manage", "users:read"]), {
      wrapper: wrapperWithUser(makeUser(["users:read"])),
    });

    expect(result.current).toBe(true);
  });
});

describe("hasPermission (plain function, used where a hook can't be called — e.g. inside a loop)", () => {
  it("returns false for a null user", () => {
    expect(hasPermission(null, "users:read")).toBe(false);
  });

  it("checks the same any-of semantics as the hook", () => {
    const user = makeUser(["users:read"]);

    expect(hasPermission(user, "users:read")).toBe(true);
    expect(hasPermission(user, "users:write")).toBe(false);
    expect(hasPermission(user, ["users:write", "users:read"])).toBe(true);
  });
});
