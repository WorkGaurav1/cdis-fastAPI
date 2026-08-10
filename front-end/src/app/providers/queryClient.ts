import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // The token-refresh interceptor already handles transient 401s by
      // retrying once at the HTTP layer — a query-level retry on top of
      // that would just repeat a failure that's already been resolved
      // (or definitively hasn't).
      retry: false,
      refetchOnWindowFocus: false,
    },
  },
});
