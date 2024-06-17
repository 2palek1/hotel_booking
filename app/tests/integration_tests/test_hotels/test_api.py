from httpx import AsyncClient
import pytest


@pytest.mark.parametrize("location, date_from, date_to, status_code, detail", [
    ("Алтай", "2023-01-01", "2022-01-01", 400, "date_from can not be after date_to"),
    ("Алтай", "2023-01-01", "2023-03-01", 400, "Hotel can not be booked for over a month"),
    ("Алтай", "2023-01-01", "2023-01-14", 200, None),
])

async def test_get_hotels_by_location_and_time(
    location,
    date_to,
    date_from,
    status_code,
    detail,
    ac: AsyncClient,
):
    response = await ac.get(
        f"/hotels/{location}",
        params={
            "date_from": date_from,
            "date_to": date_to,
        })
    assert response.status_code == status_code
    if str(status_code).startswith("4"):
        assert response.json()["detail"] == detail