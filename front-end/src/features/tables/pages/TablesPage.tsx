import { useQuery } from "@tanstack/react-query";

import { DataTable } from "@/shared";

import { tablesApi } from "../api/tablesApi";
import { tablesColumns } from "../tablesColumns";

function TablesPage() {
  const { data, isPending, isError } = useQuery({
    queryKey: ["tables", "users"],
    queryFn: () => tablesApi.listUsers(),
  });

  return (
    <div>
      <h1 className="mb-1 text-xl font-semibold text-gray-900">Tables</h1>
      <p className="mb-4 text-sm text-gray-500">The current user list, rendered with the reusable DataTable primitive.</p>
      <DataTable
        columns={tablesColumns}
        data={data?.users ?? []}
        isLoading={isPending}
        emptyMessage={isError ? "Failed to load users." : "No users found."}
        searchPlaceholder="Search users..."
      />
    </div>
  );
}

export default TablesPage;
