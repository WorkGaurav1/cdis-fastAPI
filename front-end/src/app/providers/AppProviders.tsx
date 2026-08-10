import type { ReactNode } from "react";

import { QueryClientProvider } from "@tanstack/react-query";

import { AuthProvider } from "@/auth/context";

import { queryClient } from "./queryClient";

interface AppProvidersProps {
  children: ReactNode;
}

export function AppProviders({
  children,
}: AppProvidersProps) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        {children}
      </AuthProvider>
    </QueryClientProvider>
  );
}
