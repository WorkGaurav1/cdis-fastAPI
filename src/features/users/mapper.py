# Maps the internal User DB model to the safe, external response shape
# -- never the hashed password, never internal-only fields. Mirrors the
# Node backend's src/mappers/user.mapper.ts (toSafeUser).
#
# Deliberately pure: roles/permissions are passed in already-computed
# (via features/auth/rbac_repository.py::get_roles_and_permissions_for_user)
# rather than queried here, mirroring how Node's toSafeUser only ever
# transforms an already-loaded object -- persistence stays out of the
# mapper layer.

from features.users.models import User


def to_safe_user(user: User, roles: list[str], permissions: list[str]) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "name": user.full_name,
        "roles": roles,
        "permissions": permissions,
    }
