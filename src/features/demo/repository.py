# Persistence layer for demo/showcase data -- mirrors
# src/repositories/demo.repository.ts's query shapes exactly (ordering
# included). Read-only from the API's perspective; only scripts/seed.py
# writes this data.

from sqlmodel import Session, select

from features.demo.models import (
    DemoChartDataset,
    DemoChartPoint,
    DemoStateMetric,
    DemoTableDataset,
    DemoTableRow,
)


def list_state_metrics(session: Session) -> list[DemoStateMetric]:
    return list(
        session.exec(select(DemoStateMetric).order_by(DemoStateMetric.state_name)).all()
    )


def list_chart_datasets(
    session: Session, chart_type: str | None = None
) -> list[DemoChartDataset]:
    query = select(DemoChartDataset)
    if chart_type:
        query = query.where(DemoChartDataset.chart_type == chart_type)
    query = query.order_by(DemoChartDataset.title)
    return list(session.exec(query).all())


def list_chart_points(session: Session, dataset_id: int) -> list[DemoChartPoint]:
    return list(
        session.exec(
            select(DemoChartPoint)
            .where(DemoChartPoint.dataset_id == dataset_id)
            # order_by() on an int-typed column specifically confuses
            # Pyright's overload resolution for SQLModel/SQLAlchemy's
            # stubs (it's fine on the str-typed columns used elsewhere
            # in this file) -- a real SQLAlchemy query-building idiom,
            # not a type error.
            .order_by(DemoChartPoint.sort_order)  # pyright: ignore[reportArgumentType]
        ).all()
    )


def list_table_datasets(session: Session) -> list[DemoTableDataset]:
    return list(
        session.exec(select(DemoTableDataset).order_by(DemoTableDataset.title)).all()
    )


def list_table_rows(session: Session, dataset_id: int) -> list[DemoTableRow]:
    return list(
        session.exec(
            select(DemoTableRow)
            .where(DemoTableRow.dataset_id == dataset_id)
            # Same int-typed-column order_by() stub limitation as
            # list_chart_points() above.
            .order_by(DemoTableRow.sort_order)  # pyright: ignore[reportArgumentType]
        ).all()
    )


# --- Seed-time upsert helpers (only scripts/seed.py calls these) --------


def upsert_state_metric(
    session: Session,
    *,
    state_code: str,
    state_name: str,
    project_count: int,
    activity_intensity: int,
) -> None:
    existing = session.exec(
        select(DemoStateMetric).where(DemoStateMetric.state_code == state_code)
    ).first()
    if existing is None:
        session.add(
            DemoStateMetric(
                state_code=state_code,
                state_name=state_name,
                project_count=project_count,
                activity_intensity=activity_intensity,
            )
        )
    else:
        existing.state_name = state_name
        existing.project_count = project_count
        existing.activity_intensity = activity_intensity
        session.add(existing)
    session.commit()


def upsert_chart_dataset(
    session: Session, *, slug: str, title: str, chart_type: str, description: str | None
) -> DemoChartDataset:
    existing = session.exec(
        select(DemoChartDataset).where(DemoChartDataset.slug == slug)
    ).first()
    if existing is None:
        existing = DemoChartDataset(
            slug=slug, title=title, chart_type=chart_type, description=description
        )
    else:
        existing.title = title
        existing.chart_type = chart_type
        existing.description = description
    session.add(existing)
    session.commit()
    session.refresh(existing)
    return existing


def replace_chart_points(session: Session, dataset_id: int, points: list[dict]) -> None:
    # Simplest idempotent strategy for child rows: replace them wholesale,
    # same as prisma/seed.ts's deleteMany + createMany.
    for existing in list_chart_points(session, dataset_id):
        session.delete(existing)
    session.commit()
    for index, point in enumerate(points):
        session.add(
            DemoChartPoint(
                dataset_id=dataset_id,
                label=point["label"],
                series=point.get("series"),
                value=point["value"],
                sort_order=index,
            )
        )
    session.commit()


def upsert_table_dataset(
    session: Session, *, slug: str, title: str, description: str | None
) -> DemoTableDataset:
    existing = session.exec(
        select(DemoTableDataset).where(DemoTableDataset.slug == slug)
    ).first()
    if existing is None:
        existing = DemoTableDataset(slug=slug, title=title, description=description)
    else:
        existing.title = title
        existing.description = description
    session.add(existing)
    session.commit()
    session.refresh(existing)
    return existing


def replace_table_rows(session: Session, dataset_id: int, rows: list[dict]) -> None:
    for existing in list_table_rows(session, dataset_id):
        session.delete(existing)
    session.commit()
    for index, row in enumerate(rows):
        session.add(DemoTableRow(dataset_id=dataset_id, data=row, sort_order=index))
    session.commit()
