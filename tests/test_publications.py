"""Sample test suite."""
# pylint:disable=redefined-outer-name,protected-access
import pytest

from publications_microservice.app import create_app


@pytest.fixture
def client():
    with create_app().test_client() as test_client:
        yield test_client


@pytest.fixture
def room_zero():
    return {
        "user_id": 0,
        "title": "string",
        "description": "string",
        "rooms": 0,
        "beds": 0,
        "bathrooms": 0,
        "price_per_night": 0,
        "images": [{"url": "string"}],
        "loc": {"latitude": 0, "longitude": 0},
    }


def test_root(client):  # pylint:disable=redefined-outer-name
    response = client.get("/")
    data = response.data
    assert data is not None
    assert 200 == response._status_code


def test_post(client, room_zero):  # pylint:disable=redefined-outer-name
    response = client.post("/v1/publications", json=room_zero)
    assert 200 == response._status_code


def test_post_wo_prefix(client, room_zero):  # pylint:disable=redefined-outer-name
    response = client.post("/publications", json=room_zero)
    assert 404 == response._status_code
