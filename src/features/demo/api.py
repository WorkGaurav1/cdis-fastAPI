from fastapi import APIRouter, Depends
from sqlmodel import Session

from config.database import get_session
from features.auth.dependencies import get_current_user
from features.demo.mapper import (
    to_chart_dataset_response,
    to_state_metric_response,
    to_table_dataset_response,
)
from features.demo.repository import (
    list_chart_datasets,
    list_chart_points,
    list_state_metrics,
    list_table_datasets,
    list_table_rows,
)
from features.users.models import User
from utils.apiResponse import send_success

router = APIRouter()

# Read-only demo/showcase data for the template's map, chart, and table
# gallery pages. Gated behind authentication only (no specific
# permission) -- matching src/routes/demo.routes.ts exactly, which
# guards all three routes with requireAuth alone.


@router.get("/map/states")
def get_map_states(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    metrics = list_state_metrics(session)
    return send_success({"states": [to_state_metric_response(m) for m in metrics]})


@router.get("/charts")
def get_charts(
    type: str | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    datasets = list_chart_datasets(session, chart_type=type)
    result = [
        to_chart_dataset_response(dataset, list_chart_points(session, dataset.id))
        for dataset in datasets
    ]
    return send_success({"datasets": result})


@router.get("/tables")
def get_tables(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    datasets = list_table_datasets(session)
    result = [
        to_table_dataset_response(dataset, list_table_rows(session, dataset.id))
        for dataset in datasets
    ]
    return send_success({"datasets": result})
