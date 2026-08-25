# Verifies GET /api/v1/demo/{map/states,charts,tables} -- all three
# require authentication, mirroring Node's requireAuth-only guard on
# the demo routes (open to any signed-in user, no specific permission),
# and all three return real DB-backed data (scripts/seed.py), matching
# prisma/seed.ts's shape and volume.

from fastapi.testclient import TestClient

from config.config import settings

MAP_STATES_URL = f"{settings.API_V1_STR}/demo/map/states"
CHARTS_URL = f"{settings.API_V1_STR}/demo/charts"
TABLES_URL = f"{settings.API_V1_STR}/demo/tables"
LOGIN_URL = f"{settings.API_V1_STR}/auth/login"


def _login(client: TestClient) -> None:
    response = client.post(
        LOGIN_URL, json={"email": "admin@example.com", "password": "password"}
    )
    assert response.status_code == 200, response.json()


def test_demo_routes_require_authentication(client: TestClient):
    client.cookies.clear()
    for url in (MAP_STATES_URL, CHARTS_URL, TABLES_URL):
        response = client.get(url)
        assert response.status_code == 401, url


def test_map_states_returns_all_36_states_with_int_activity_intensity(
    client: TestClient,
):
    _login(client)

    response = client.get(MAP_STATES_URL)

    assert response.status_code == 200
    states = response.json()["data"]["states"]
    # Regression guard for the bug this replaces: the old stub had 6
    # hardcoded states and activityIntensity as a 0.0-0.9 float.
    assert len(states) == 36
    for state in states:
        assert isinstance(state["activityIntensity"], int)
        assert 0 <= state["activityIntensity"] <= 100
        assert isinstance(state["projectCount"], int)
        assert state["stateCode"]
        assert state["stateName"]
    client.cookies.clear()


def test_charts_returns_all_eight_seeded_datasets_with_points(client: TestClient):
    _login(client)

    response = client.get(CHARTS_URL)

    assert response.status_code == 200
    datasets = response.json()["data"]["datasets"]
    assert len(datasets) == 8
    slugs = {d["slug"] for d in datasets}
    assert "monthly-revenue" in slugs
    assert "quarterly-sales-by-region" in slugs

    single_series = next(d for d in datasets if d["slug"] == "monthly-revenue")
    assert single_series["chartType"] == "bar"
    assert len(single_series["points"]) == 6
    assert single_series["points"][0]["label"] == "Jan"

    multi_series = next(d for d in datasets if d["slug"] == "revenue-vs-cost")
    series_names = {p["series"] for p in multi_series["points"]}
    assert series_names == {"Revenue", "Cost"}
    client.cookies.clear()


def test_charts_type_query_param_filters_results(client: TestClient):
    _login(client)

    response = client.get(CHARTS_URL, params={"type": "line"})

    assert response.status_code == 200
    datasets = response.json()["data"]["datasets"]
    assert len(datasets) == 2
    assert all(d["chartType"] == "line" for d in datasets)
    client.cookies.clear()


def test_tables_returns_all_three_seeded_datasets_with_rows(client: TestClient):
    _login(client)

    response = client.get(TABLES_URL)

    assert response.status_code == 200
    datasets = response.json()["data"]["datasets"]
    assert len(datasets) == 3
    slugs = {d["slug"] for d in datasets}
    assert slugs == {"orders", "employees", "products"}

    orders = next(d for d in datasets if d["slug"] == "orders")
    assert len(orders["rows"]) == 24
    assert "orderId" in orders["rows"][0]
    assert "customer" in orders["rows"][0]
    client.cookies.clear()
