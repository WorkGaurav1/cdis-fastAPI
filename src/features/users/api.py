# Users API Router.

from fastapi import APIRouter, Depends
from sqlmodel import Session

from config.database import get_session
from features.auth.dependencies import get_current_user
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
    current_user: User = Depends(get_current_user),
):
    # Retrieve a list of all users.
    #
    # NOTE: Node also requires the users:read permission here
    # (requirePermission("users:read")) -- that's tracked separately
    # (P0 step 10 of the gap-analysis priority list), since no
    # Role/Permission tables exist yet. Every authenticated user can
    # list users in the meantime.
    _ = current_user
    users = list_users(session, skip=skip, limit=limit)
    return send_success({"users": [to_safe_user(u) for u in users]})
