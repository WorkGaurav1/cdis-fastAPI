import type { ColumnDef } from "@tanstack/react-table";

import type { User } from "@/auth";

export const usersTableColumns: ColumnDef<User, unknown>[] = [
  { accessorKey: "name", header: "Name" },
  { accessorKey: "email", header: "Email" },
  {
    id: "roles",
    header: "Roles",
    accessorFn: (user) => user.roles.join(", "),
  },
];
