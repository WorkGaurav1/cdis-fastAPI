from fastapi import APIRouter, Depends

from features.auth.dependencies import get_current_user
from features.users.models import User
from utils.apiResponse import send_success

router = APIRouter()

# Dummy state data for the India map
fake_states_db = [
    { "id": "1", "stateCode": "27", "stateName": "Maharashtra", "projectCount": 120, "activityIntensity": 0.8 },
    { "id": "2", "stateCode": "29", "stateName": "Karnataka", "projectCount": 95, "activityIntensity": 0.7 },
    { "id": "3", "stateCode": "07", "stateName": "Delhi", "projectCount": 150, "activityIntensity": 0.9 },
    { "id": "4", "stateCode": "24", "stateName": "Gujarat", "projectCount": 60, "activityIntensity": 0.5 },
    { "id": "5", "stateCode": "33", "stateName": "Tamil Nadu", "projectCount": 110, "activityIntensity": 0.75 },
    { "id": "6", "stateCode": "09", "stateName": "Uttar Pradesh", "projectCount": 45, "activityIntensity": 0.3 }
]

@router.get("/map/states")
def get_map_states(current_user: User = Depends(get_current_user)):
    # Returns dummy statistics for state boundaries.
    #
    # NOTE: Node guards this with requireAuth only -- no specific
    # permission, open to any signed-in user -- so a plain auth
    # dependency is the full parity target here, unlike /users (P0 step 10).
    # The data itself (6 hardcoded states, activityIntensity as a 0-1
    # float rather than Node's 0-100 int across all 36 states/UTs) is a
    # separate, already-tracked gap (P1 step 13).
    _ = current_user
    return send_success({"states": fake_states_db})
