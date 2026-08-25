# Demo/showcase database models -- mirrors the Node backend's
# DemoStateMetric/DemoChartDataset/DemoChartPoint/DemoTableDataset/
# DemoTableRow Prisma models (prisma/schema.prisma) field for field.
#
# Entirely synthetic -- safe to delete or replace wholesale when this
# template is used to start a real project. Kept separate from the
# domain models (User/Role/Permission/RefreshToken are real).

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from utils.time import utcnow


class DemoStateMetric(SQLModel, table=True):
    """Per-state metrics backing the Dashboard's India map widgets."""

    __tablename__ = "demo_state_metrics"

    id: Optional[int] = Field(default=None, primary_key=True)
    state_code: str = Field(unique=True, index=True, max_length=10)
    state_name: str = Field(max_length=100)

    # Drives the "Project Distribution" choropleth.
    project_count: int
    # Drives the "Activity Intensity" heatmap (0-100).
    activity_intensity: int

    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class DemoChartDataset(SQLModel, table=True):
    """A named dataset backing one chart-gallery example, e.g. "monthly-revenue"."""

    __tablename__ = "demo_chart_datasets"

    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True, max_length=150)
    title: str = Field(max_length=150)
    # "bar" | "line" | "area" | "pie" | "donut" | "radial" -- purely
    # descriptive; the frontend decides how to render a given dataset,
    # this isn't enforced.
    chart_type: str = Field(max_length=30)
    description: Optional[str] = Field(default=None, max_length=255)

    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class DemoChartPoint(SQLModel, table=True):
    """
    One data point in a chart dataset. `series` distinguishes multiple
    bars/lines sharing the same label, for grouped/stacked/multi-line charts.
    """

    __tablename__ = "demo_chart_points"

    id: Optional[int] = Field(default=None, primary_key=True)
    dataset_id: int = Field(foreign_key="demo_chart_datasets.id", index=True)

    label: str = Field(max_length=100)
    series: Optional[str] = Field(default=None, max_length=100)
    value: float
    sort_order: int = Field(default=0)


class DemoTableDataset(SQLModel, table=True):
    """A named dataset backing one table-gallery example, e.g. "orders"."""

    __tablename__ = "demo_table_datasets"

    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True, max_length=150)
    title: str = Field(max_length=150)
    description: Optional[str] = Field(default=None, max_length=255)

    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class DemoTableRow(SQLModel, table=True):
    """
    One row in a table dataset. Column shape varies per dataset (an
    "orders" table and an "employees" table don't share columns), so the
    row payload is JSON rather than a fixed set of typed columns.
    """

    __tablename__ = "demo_table_rows"

    id: Optional[int] = Field(default=None, primary_key=True)
    dataset_id: int = Field(foreign_key="demo_table_datasets.id", index=True)

    data: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    sort_order: int = Field(default=0)
