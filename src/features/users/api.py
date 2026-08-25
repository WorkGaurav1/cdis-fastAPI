# Users API Router.

from fastapi import APIRouter, Depends
from sqlmodel import Session

from config.database import get_session
from features.users.mapper import to_safe_user
from features.users.repository import list_users
from utils.apiResponse import send_success

router = APIRouter()


@router.get("")
def read_users(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    # Retrieve a list of all users.
    #
    # NOTE: no auth/permission check yet -- Node requires requireAuth +
    # requirePermission("users:read") here. That's tracked separately
    # (P0 steps 9-10 of the gap-analysis priority list): step 9 wires a
    # real auth dependency onto this route, step 10 adds the permission
    # check once RBAC tables exist.
    users = list_users(session, skip=skip, limit=limit)
    return send_success({"users": [to_safe_user(u) for u in users]})
