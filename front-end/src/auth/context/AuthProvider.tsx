import { useCallback, useEffect, useMemo, type PropsWithChildren } from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { AuthContext } from "./AuthContext";

import { ApiError } from "@/api";
import { logger } from "@/lib";

import { authService } from "../services";
import { AUTH_QUERY_KEYS, SESSION_EXPIRED_EVENT } from "../constants";

import type { LoginRequest, User } from "../types";

export function AuthProvider({ children }: PropsWithChildren) {
  const queryClient = useQueryClient();

  // Access/refresh tokens are httpOnly — invisible to JS — so there is
  // no client-side way to know whether a session might exist. The only
  // way to find out is to ask, once, on mount.
  const meQuery = useQuery({
    queryKey: AUTH_QUERY_KEYS.currentUser,
    queryFn: () => authService.getCurrentUser(),
    // A 401 here just means "not logged in" — not worth a retry.
    retry: false,
    // The global default (queryClient.ts) turns this off to avoid
    // surprising refetches. This query is the one deliberate exception:
    // permissions can change server-side mid-session (see Milestone 4's
    // live-permission-check design — a revoked permission takes effect
    // on the very next request), and pure client-side navigation never
    // remounts AuthProvider to pick that up on its own. "always" (not
    // just `true`) skips the staleTime check, so returning to the tab
    // re-verifies identity every time rather than only after some
    // arbitrary staleness window.
    refetchOnWindowFocus: "always",
  });

  const loginMutation = useMutation({
    mutationFn: (credentials: LoginRequest) => authService.login(credentials),
    onSuccess: (loggedInUser) => {
      queryClient.setQueryData<User>(AUTH_QUERY_KEYS.currentUser, loggedInUser);
    },
  });

  const logoutMutation = useMutation({
    mutationFn: () => authService.logout(),
    onSuccess: () => {
      queryClient.setQueryData<User | null>(AUTH_QUERY_KEYS.currentUser, null);
    },
  });

  useEffect(() => {
    function handleSessionExpired() {
      queryClient.setQueryData<User | null>(AUTH_QUERY_KEYS.currentUser, null);
    }

    window.addEventListener(SESSION_EXPIRED_EVENT, handleSessionExpired);

    return () => {
      window.removeEventListener(SESSION_EXPIRED_EVENT, handleSessionExpired);
    };
  }, [queryClient]);

  const login = useCallback(
    async (credentials: LoginRequest) => {
      await loginMutation.mutateAsync(credentials);
    },
    [loginMutation],
  );

  const logout = useCallback(async () => {
    await logoutMutation.mutateAsync();
  }, [logoutMutation]);

  const user = meQuery.data ?? null;
  const meError = meQuery.error;

  useEffect(() => {
    if (!meError) {
      return;
    }

    // A 401 here just means "not logged in" — expected, not worth
    // logging. Anything else (network failure, 500) is unexpected and
    // worth knowing about, even though the safe fallback is the same
    // either way: treat the user as signed out.
    if (!(meError instanceof ApiError) || meError.statusCode !== 401) {
      logger.warn("Failed to restore session", meError);
    }
  }, [meError]);

  const value = useMemo(
    () => ({
      user,
      loading: meQuery.isPending,
      isAuthenticated: user !== null,
      login,
      logout,
    }),
    [user, meQuery.isPending, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
