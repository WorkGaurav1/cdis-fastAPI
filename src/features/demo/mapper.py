# Maps demo/showcase DB models to the exact response shapes Node's
# src/services/demo.service.ts produces (camelCase keys -- these are
# wire-format JSON, not Python identifiers).

from features.demo.models import (
    DemoChartDataset,
    DemoChartPoint,
    DemoStateMetric,
    DemoTableDataset,
    DemoTableRow,
)


def to_state_metric_response(metric: DemoStateMetric) -> dict:
    return {
        "id": metric.id,
        "stateCode": metric.state_code,
        "stateName": metric.state_name,
        "projectCount": metric.project_count,
        "activityIntensity": metric.activity_intensity,
    }


def to_chart_dataset_response(
    dataset: DemoChartDataset, points: list[DemoChartPoint]
) -> dict:
    return {
        "id": dataset.id,
        "slug": dataset.slug,
        "title": dataset.title,
        "chartType": dataset.chart_type,
        "description": dataset.description,
        "points": [
            {"label": p.label, "series": p.series, "value": p.value} for p in points
        ],
    }


def to_table_dataset_response(
    dataset: DemoTableDataset, rows: list[DemoTableRow]
) -> dict:
    return {
        "id": dataset.id,
        "slug": dataset.slug,
        "title": dataset.title,
        "description": dataset.description,
        "rows": [row.data for row in rows],
    }
