import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";

import type { User } from "@/auth";
import { PieChart } from "@/shared";

import { chartsApi } from "../api/chartsApi";

interface RoleShare {
  role: string;
  percentage: number;
}

/**
 * Same underlying user-by-role data as Graphs, but cut as a real
 * percentage-of-total breakdown rather than raw counts — a different,
 * still-honest view of the same data, not a duplicate page.
 */
function roleSharesFromUsers(users: User[]): RoleShare[] {
  const counts = new Map<string, number>();

  for (const user of users) {
    for (const role of user.roles) {
      counts.set(role, (counts.get(role) ?? 0) + 1);
    }
  }

  const total = users.length;
  if (total === 0) return [];

  return Array.from(counts.entries()).map(([role, count]) => ({
    role,
    percentage: Math.round((count / total) * 100),
  }));
}

function ChartsPage() {
  const { data, isPending, isError } = useQuery({
    queryKey: ["charts", "users"],
    queryFn: () => chartsApi.listUsers(),
  });

  const roleShares = useMemo(() => roleSharesFromUsers(data?.users ?? []), [data?.users]);

  return (
    <div>
      <h1 className="mb-1 text-xl font-semibold text-gray-900">Charts</h1>
      <p className="mb-4 text-sm text-gray-500">Role distribution as a share of all users, computed live.</p>

      {isError ? (
        <p className="text-sm text-red-600">Failed to load users.</p>
      ) : isPending ? (
        <p className="text-sm text-gray-500">Loading…</p>
      ) : roleShares.length === 0 ? (
        <p className="text-sm text-gray-500">No users found.</p>
      ) : (
        <PieChart data={roleShares} nameKey="role" valueKey="percentage" title="Role Distribution (%)" height={320} />
      )}
    </div>
  );
}

export default ChartsPage;
