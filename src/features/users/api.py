# Users API Router.

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from config.database import get_session
from features.auth.dependencies import require_permission
from features.auth.rbac_repository import get_roles_and_permissions_for_user
from features.users.mapper import to_safe_user
from features.users.models import User
from features.users.repository import count_users, list_users
from utils.apiResponse import send_success
from utils.db import require_id

router = APIRouter()


@router.get("")
def read_users(
    # Bounds and defaults match the Node backend's paginationQuerySchema
    # (back-end/src/data-transfer-object/pagination.dto.ts) exactly --
    # same contract, either backend. limit=100 with no upper bound used
    # to let a caller request the entire table in one unbounded query;
    # capped here for the same reason Node's was.
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("users:read")),
):
    # Retrieve a page of users. Mirrors Node's
    # requireAuth + requirePermission("users:read") route guard
    # (src/routes/user.routes.ts) exactly.
    _ = current_user
    users = list_users(session, offset=offset, limit=limit)
    safe_users = []
    for user in users:
        roles, permissions = get_roles_and_permissions_for_user(
            session, require_id(user.id)
        )
        safe_users.append(to_safe_user(user, roles, permissions))
    total = count_users(session)
    return send_success(
        {
            "users": safe_users,
            "pagination": {"limit": limit, "offset": offset, "total": total},
        }
    )
