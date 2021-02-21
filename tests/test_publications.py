"""Sample test suite."""
import json
import logging

# pylint:disable=redefined-outer-name,protected-access
import pytest

from publications_microservice.app import create_app

logger = logging.getLogger(__name__)


@pytest.fixture
def client():
    with create_app().test_client() as test_client:
        yield test_client


@pytest.fixture
def room_zero():
    return {
        "user_id": 1,
        "title": "Publication title",
        "description": "Some nice description",
        "rooms": 1,
        "beds": 1,
        "bathrooms": 1,
        "price_per_night": 10,
        "images": [],
        "loc": {"latitude": 0, "longitude": 0},
    }


def test_root(client):
    response = client.get("/")
    data = response.data
    assert data is not None
    assert 200 == response._status_code


def test_post(client, room_zero):
    response = client.post("/v1/publications", json=room_zero)
    assert 200 == response._status_code
    assert len(json.loads(response.data)) >= 1


def test_post_wo_prefix(client, room_zero):
    response = client.post("/publications", json=room_zero)
    assert 404 == response._status_code
