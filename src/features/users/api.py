# Users API Router.

from fastapi import APIRouter, Depends
from sqlmodel import Session

from config.database import get_session
from features.auth.dependencies import require_permission
from features.auth.rbac_repository import get_roles_and_permissions_for_user
from features.users.mapper import to_safe_user
from features.users.models import User
from features.users.repository import list_users
from utils.apiResponse import send_success

router = APIRouter()


@router.get("")
def read_users(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("users:read")),
):
    # Retrieve a list of all users. Mirrors Node's
    # requireAuth + requirePermission("users:read") route guard
    # (src/routes/user.routes.ts) exactly.
    _ = current_user
    users = list_users(session, skip=skip, limit=limit)
    safe_users = []
    for user in users:
        roles, permissions = get_roles_and_permissions_for_user(session, user.id)
        safe_users.append(to_safe_user(user, roles, permissions))
    return send_success({"users": safe_users})
