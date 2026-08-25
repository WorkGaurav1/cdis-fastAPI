# RBAC database models -- mirrors the Node backend's Role/Permission/
# UserRole/RolePermission Prisma models (prisma/schema.prisma) field for
# field, including the composite primary keys on the two join tables.

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from utils.time import utcnow


class Role(SQLModel, table=True):
    """An assignable role (e.g. admin, manager, user)."""

    __tablename__ = "roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)

    created_at: datetime = Field(default_factory=utcnow)


class Permission(SQLModel, table=True):
    """A granular permission (e.g. "users:read", "reports:export")."""

    __tablename__ = "permissions"

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, index=True, max_length=150)
    description: Optional[str] = Field(default=None, max_length=255)

    created_at: datetime = Field(default_factory=utcnow)


class UserRole(SQLModel, table=True):
    """Join table: which roles a user holds."""

    __tablename__ = "user_roles"

    user_id: int = Field(foreign_key="users.id", primary_key=True)
    role_id: int = Field(foreign_key="roles.id", primary_key=True, index=True)

    assigned_at: datetime = Field(default_factory=utcnow)


class RolePermission(SQLModel, table=True):
    """Join table: which permissions a role grants."""

    __tablename__ = "role_permissions"

    role_id: int = Field(foreign_key="roles.id", primary_key=True)
    permission_id: int = Field(
        foreign_key="permissions.id", primary_key=True, index=True
    )
