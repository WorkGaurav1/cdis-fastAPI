import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";

import type { User } from "@/auth";
import { BarChart } from "@/shared";

import { graphsApi } from "../api/graphsApi";

interface RoleCount {
  role: string;
  count: number;
}

/** Real, derived from the actual user list — never fabricated. */
function countUsersByRole(users: User[]): RoleCount[] {
  const counts = new Map<string, number>();

  for (const user of users) {
    for (const role of user.roles) {
      counts.set(role, (counts.get(role) ?? 0) + 1);
    }
  }

  return Array.from(counts.entries()).map(([role, count]) => ({ role, count }));
}

function GraphsPage() {
  const { data, isPending, isError } = useQuery({
    queryKey: ["graphs", "users"],
    queryFn: () => graphsApi.listUsers(),
  });

  // data?.users is a stable reference from the query cache; a `?? []`
  // fallback inline here would be a fresh array every render, defeating
  // this memo — so the fallback lives inside the memo body instead.
  const roleCounts = useMemo(() => countUsersByRole(data?.users ?? []), [data?.users]);

  return (
    <div>
      <h1 className="mb-1 text-xl font-semibold text-gray-900">Graphs</h1>
      <p className="mb-4 text-sm text-gray-500">Users per role, computed live from the current user list.</p>

      {isError ? (
        <p className="text-sm text-red-600">Failed to load users.</p>
      ) : isPending ? (
        <p className="text-sm text-gray-500">Loading…</p>
      ) : (
        <BarChart data={roleCounts} xKey="role" yKey="count" title="Users by Role" height={320} />
      )}
    </div>
  );
}

export default GraphsPage;
