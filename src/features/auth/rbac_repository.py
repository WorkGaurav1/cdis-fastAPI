# Persistence layer for RBAC -- mirrors the query shape Node gets "for
# free" via Prisma's nested `include` on user.roles.role.permissions
# (src/repositories/user.repository.ts), plus the seed-time upsert
# helpers src/../prisma/seed.ts relies on.

from sqlmodel import Session, select

from features.auth.rbac_models import Permission, Role, RolePermission, UserRole


def get_role_by_name(session: Session, name: str) -> Role | None:
    return session.exec(select(Role).where(Role.name == name)).first()


def get_permission_by_key(session: Session, key: str) -> Permission | None:
    return session.exec(select(Permission).where(Permission.key == key)).first()


def get_or_create_role(
    session: Session, name: str, description: str | None = None
) -> Role:
    role = get_role_by_name(session, name)
    if role is not None:
        return role
    role = Role(name=name, description=description)
    session.add(role)
    session.commit()
    session.refresh(role)
    return role


def get_or_create_permission(
    session: Session, key: str, description: str | None = None
) -> Permission:
    permission = get_permission_by_key(session, key)
    if permission is not None:
        return permission
    permission = Permission(key=key, description=description)
    session.add(permission)
    session.commit()
    session.refresh(permission)
    return permission


def ensure_role_has_permission(
    session: Session, role_id: int, permission_id: int
) -> None:
    existing = session.exec(
        select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )
    ).first()
    if existing is not None:
        return
    session.add(RolePermission(role_id=role_id, permission_id=permission_id))
    session.commit()


def ensure_user_has_role(session: Session, user_id: int, role_id: int) -> None:
    existing = session.exec(
        select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
    ).first()
    if existing is not None:
        return
    session.add(UserRole(user_id=user_id, role_id=role_id))
    session.commit()


def get_roles_and_permissions_for_user(
    session: Session, user_id: int
) -> tuple[list[str], list[str]]:
    """
    Returns (role_names, permission_keys) -- the effective permission set
    is the union of every permission on every role the user holds,
    deduplicated, mirroring toSafeUser()'s
    `Array.from(new Set(user.roles.flatMap(...)))` exactly.
    """
    roles = session.exec(
        select(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(  # type: ignore[arg-type]
            UserRole.user_id == user_id
        )
    ).all()
    role_names = [role.name for role in roles]

    if not roles:
        return role_names, []

    role_ids = [role.id for role in roles]
    permissions = session.exec(
        select(Permission)
        .join(RolePermission, RolePermission.permission_id == Permission.id)  # type: ignore[arg-type]
        .where(RolePermission.role_id.in_(role_ids))  # type: ignore[union-attr]
    ).all()
    permission_keys = sorted({permission.key for permission in permissions})

    return role_names, permission_keys
