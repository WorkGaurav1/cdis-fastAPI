import { useQuery } from "@tanstack/react-query";

import { DataTable } from "@/shared";

import { userApi } from "../api/userApi";
import { usersTableColumns } from "../usersTableColumns";

function UsersPage() {
  const { data, isPending, isError } = useQuery({
    queryKey: ["users", "list"],
    queryFn: () => userApi.list(),
  });

  return (
    <div>
      <h1 className="mb-4 text-xl font-semibold text-gray-900">Users</h1>
      <DataTable
        columns={usersTableColumns}
        data={data?.users ?? []}
        isLoading={isPending}
        emptyMessage={isError ? "Failed to load users." : "No users found."}
        searchPlaceholder="Search users..."
      />
    </div>
  );
}

export default UsersPage;
