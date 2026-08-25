# Demo/showcase seed data definitions -- ports prisma/seed.ts's
# DEMO_STATES/CHART_DATASETS/TABLE_DATASETS constants and generation
# logic 1:1 (same distribution shapes, same dataset definitions).

import random
from datetime import datetime, timedelta

# [name, code] pairs -- must match
# front-end/public/data/india-districts.geojson's st_nm/st_code.
# All 36 states/UTs.
DEMO_STATES: list[tuple[str, str]] = [
    ("Mizoram", "15"),
    ("Tamil Nadu", "33"),
    ("Madhya Pradesh", "23"),
    ("Maharashtra", "27"),
    ("Chhattisgarh", "22"),
    ("Gujarat", "24"),
    ("Odisha", "21"),
    ("Andhra Pradesh", "37"),
    ("Karnataka", "29"),
    ("Goa", "30"),
    ("Kerala", "32"),
    ("Telangana", "36"),
    ("West Bengal", "19"),
    ("Puducherry", "34"),
    ("Arunachal Pradesh", "12"),
    ("Assam", "18"),
    ("Nagaland", "13"),
    ("Meghalaya", "17"),
    ("Manipur", "14"),
    ("Tripura", "16"),
    ("Uttar Pradesh", "09"),
    ("Rajasthan", "08"),
    ("Delhi", "07"),
    ("Haryana", "06"),
    ("Sikkim", "11"),
    ("Bihar", "10"),
    ("Jharkhand", "20"),
    ("Ladakh", "38"),
    ("Jammu and Kashmir", "01"),
    ("Himachal Pradesh", "02"),
    ("Punjab", "03"),
    ("Uttarakhand", "05"),
    ("Chandigarh", "04"),
    ("Lakshadweep", "31"),
    ("Andaman and Nicobar Islands", "35"),
    ("Dadra and Nagar Haveli and Daman and Diu", "26"),
]


def random_project_count() -> int:
    # Skewed toward low/zero project counts with a few standouts, same
    # shape as prisma/seed.ts's distribution.
    roll = random.random()
    if roll < 0.3:
        return 0
    if roll < 0.55:
        return random.randint(1, 5)
    if roll < 0.75:
        return random.randint(5, 19)
    if roll < 0.88:
        return random.randint(20, 49)
    if roll < 0.96:
        return random.randint(50, 99)
    return random.randint(100, 150)


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]


def _chart_datasets() -> list[dict]:
    return [
        {
            "slug": "monthly-revenue",
            "title": "Monthly Revenue",
            "chart_type": "bar",
            "description": "Single-series bar chart -- revenue per month.",
            "points": [
                {"label": label, "value": random.randint(20_000, 90_000)}
                for label in MONTHS
            ],
        },
        {
            "slug": "quarterly-sales-by-region",
            "title": "Quarterly Sales by Region",
            "chart_type": "bar",
            "description": "Grouped bar chart -- multiple series sharing the same "
            "labels.",
            "points": [
                {
                    "label": quarter,
                    "series": region,
                    "value": random.randint(5_000, 40_000),
                }
                for quarter in ("Q1", "Q2", "Q3", "Q4")
                for region in ("North", "South", "East", "West")
            ],
        },
        {
            "slug": "website-traffic",
            "title": "Website Traffic",
            "chart_type": "line",
            "description": "Single-series line chart -- daily visits.",
            "points": [
                {"label": label, "value": random.randint(800, 5_000)}
                for label in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
            ],
        },
        {
            "slug": "revenue-vs-cost",
            "title": "Revenue vs. Cost",
            "chart_type": "line",
            "description": "Multi-series line chart -- two series sharing the same "
            "labels.",
            "points": [
                point
                for label in MONTHS
                for point in (
                    {
                        "label": label,
                        "series": "Revenue",
                        "value": random.randint(30_000, 90_000),
                    },
                    {
                        "label": label,
                        "series": "Cost",
                        "value": random.randint(15_000, 50_000),
                    },
                )
            ],
        },
        {
            "slug": "user-growth",
            "title": "User Growth",
            "chart_type": "area",
            "description": "Area chart -- cumulative users over time.",
            "points": _user_growth_points(),
        },
        {
            "slug": "market-share",
            "title": "Market Share",
            "chart_type": "pie",
            "description": "Pie chart -- share of total by category.",
            "points": [
                {"label": label, "value": random.randint(10, 40)}
                for label in (
                    "Product A",
                    "Product B",
                    "Product C",
                    "Product D",
                    "Other",
                )
            ],
        },
        {
            "slug": "budget-allocation",
            "title": "Budget Allocation",
            "chart_type": "donut",
            "description": "Donut chart -- share of total budget by department.",
            "points": [
                {"label": label, "value": random.randint(10, 35)}
                for label in (
                    "Engineering",
                    "Marketing",
                    "Sales",
                    "Operations",
                    "Support",
                )
            ],
        },
        {
            "slug": "team-performance",
            "title": "Team Performance",
            "chart_type": "radial",
            "description": "Radial chart -- percentage completion per team.",
            "points": [
                {"label": label, "value": random.randint(45, 98)}
                for label in ("Frontend", "Backend", "QA", "DevOps")
            ],
        },
    ]


def _user_growth_points() -> list[dict]:
    total = random.randint(200, 500)
    points = []
    for label in MONTHS:
        total += random.randint(100, 800)
        points.append({"label": label, "value": total})
    return points


ORDER_STATUSES = ["Pending", "Shipped", "Delivered", "Cancelled"]
DEPARTMENTS = ["Engineering", "Marketing", "Sales", "Support", "Operations"]
CATEGORIES = ["Electronics", "Apparel", "Home & Kitchen", "Sports", "Books"]


def _table_datasets() -> list[dict]:
    return [
        {
            "slug": "orders",
            "title": "Orders",
            "description": "A typical e-commerce order list -- id, customer, "
            "amount, status, date.",
            "rows": [
                {
                    "orderId": f"ORD-{1000 + index}",
                    "customer": f"Customer {index + 1}",
                    "amount": random.randint(500, 15_000),
                    "status": random.choice(ORDER_STATUSES),
                    "placedOn": (
                        datetime.now() - timedelta(days=random.randint(0, 60))
                    ).strftime("%Y-%m-%d"),
                }
                for index in range(24)
            ],
        },
        {
            "slug": "employees",
            "title": "Employees",
            "description": "A typical HR/admin employee directory.",
            "rows": [
                {
                    "name": f"Employee {index + 1}",
                    "department": random.choice(DEPARTMENTS),
                    "email": f"employee{index + 1}@example.com",
                    "isActive": random.random() > 0.15,
                }
                for index in range(18)
            ],
        },
        {
            "slug": "products",
            "title": "Products",
            "description": "A typical product catalog -- name, category, price, "
            "stock, rating.",
            "rows": [
                {
                    "name": f"Product {index + 1}",
                    "category": random.choice(CATEGORIES),
                    "price": random.randint(199, 24_999),
                    "stock": random.randint(0, 500),
                    "rating": round((3 + random.random() * 2) * 10) / 10,
                }
                for index in range(20)
            ],
        },
    ]


# Generated once at import time -- same "build the seed payload, then
# upsert it" split prisma/seed.ts uses. Regenerating on every seed run
# gives fresh random values each time (matching Node's behavior: the
# seed script re-rolls project counts/values on every run too).
def build_chart_datasets() -> list[dict]:
    return _chart_datasets()


def build_table_datasets() -> list[dict]:
    return _table_datasets()
