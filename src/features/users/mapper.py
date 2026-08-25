# Maps the internal User DB model to the safe, external response shape
# -- never the hashed password, never internal-only fields. Mirrors the
# Node backend's src/mappers/user.mapper.ts (toSafeUser).

from features.users.models import User


def to_safe_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "name": user.full_name,
        # TODO(P0 step 10): real roles/permissions, derived from the
        # Role/Permission/UserRole/RolePermission tables, the way
        # toSafeUser() computes them on the Node side. Those tables
        # don't exist yet, so this is an honest empty placeholder --
        # never fabricated authorization data.
        "roles": [],
        "permissions": [],
    }
