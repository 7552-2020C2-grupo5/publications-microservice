"""Sample test suite."""
import json
import logging

# pylint:disable=redefined-outer-name,protected-access
import pytest

from publications_microservice.app import create_app
from publications_microservice.models import db

logger = logging.getLogger(__name__)


@pytest.fixture
def client():
    app = create_app()
    with app.app_context():
        db.create_all()
    with app.test_client() as test_client:
        yield test_client
    with app.app_context():
        db.drop_all()


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
    assert len(json.loads(response.data)) == 1


def test_loc_search(client, room_zero):
    response = client.post("/v1/publications", json=room_zero)
    assert response._status_code == 200
    response = client.get(
        "/v1/publications",
        json={"latitude": 0.1, "longitude": 0.1, "max_distance": 15.7},
    )
    assert response._status_code == 200
    assert len(json.loads(response.data)) == 1


def test_post_wo_prefix(client, room_zero):
    response = client.post("/publications", json=room_zero)
    assert 404 == response._status_code


def test_filter_blocked_default_blockchain_default(client, room_zero):
    # UNSET and not blocked
    r1 = client.post("/v1/publications", json=room_zero)
    assert r1._status_code == 200

    # UNSET and blocked
    r2 = client.post("/v1/publications", json=room_zero)
    assert r2._status_code == 200
    r = client.delete(f"/v1/publications/{json.loads(r2.data).get('id')}")
    assert r._status_code == 200

    # CONFIRMED and not blocked
    r3 = client.post("/v1/publications", json=room_zero)
    assert r3._status_code == 200
    r = client.patch(
        f"/v1/publications/{json.loads(r3.data).get('id')}",
        json={"blockchain_status": "CONFIRMED"},
    )
    assert r._status_code == 200

    # CONFIRMED and blocked
    r4 = client.post("/v1/publications", json=room_zero)
    assert r4._status_code == 200
    r = client.patch(
        f"/v1/publications/{json.loads(r4.data).get('id')}",
        json={"blockchain_status": "CONFIRMED"},
    )
    assert r._status_code == 200
    r = client.delete(f"/v1/publications/{json.loads(r4.data).get('id')}")
    assert r._status_code == 200

    search = client.get("/v1/publications")
    assert search._status_code == 200
    search_data = json.loads(search.data)
    print(search_data)
    assert len(search_data) == 1
    assert search_data[0]["id"] == json.loads(r3.data)["id"]


def test_filter_blocked_default_blockchain_explicit(client, room_zero):
    # UNSET and not blocked
    r1 = client.post("/v1/publications", json=room_zero)
    assert r1._status_code == 200

    # UNSET and blocked
    r2 = client.post("/v1/publications", json=room_zero)
    assert r2._status_code == 200
    r = client.delete(f"/v1/publications/{json.loads(r2.data).get('id')}")
    assert r._status_code == 200

    # CONFIRMED and not blocked
    r3 = client.post("/v1/publications", json=room_zero)
    assert r3._status_code == 200
    r = client.patch(
        f"/v1/publications/{json.loads(r3.data).get('id')}",
        json={"blockchain_status": "CONFIRMED"},
    )
    assert r._status_code == 200

    # CONFIRMED and blocked
    r4 = client.post("/v1/publications", json=room_zero)
    assert r4._status_code == 200
    r = client.patch(
        f"/v1/publications/{json.loads(r4.data).get('id')}",
        json={"blockchain_status": "CONFIRMED"},
    )
    assert r._status_code == 200
    r = client.delete(f"/v1/publications/{json.loads(r4.data).get('id')}")
    assert r._status_code == 200

    search = client.get("/v1/publications", data={"blockchain_status": "CONFIRMED"})
    assert search._status_code == 200
    search_data = json.loads(search.data)
    print(search_data)
    assert len(search_data) == 1
    assert search_data[0]["id"] == json.loads(r3.data)["id"]


def test_filter_blocked_true_blockchain_implicit(client, room_zero):
    # UNSET and not blocked
    r1 = client.post("/v1/publications", json=room_zero)
    assert r1._status_code == 200

    # UNSET and blocked
    r2 = client.post("/v1/publications", json=room_zero)
    assert r2._status_code == 200
    r = client.delete(f"/v1/publications/{json.loads(r2.data).get('id')}")
    assert r._status_code == 200

    # CONFIRMED and not blocked
    r3 = client.post("/v1/publications", json=room_zero)
    assert r3._status_code == 200
    r = client.patch(
        f"/v1/publications/{json.loads(r3.data).get('id')}",
        json={"blockchain_status": "CONFIRMED"},
    )
    assert r._status_code == 200

    # CONFIRMED and blocked
    r4 = client.post("/v1/publications", json=room_zero)
    assert r4._status_code == 200
    r = client.patch(
        f"/v1/publications/{json.loads(r4.data).get('id')}",
        json={"blockchain_status": "CONFIRMED"},
    )
    assert r._status_code == 200
    r = client.delete(f"/v1/publications/{json.loads(r4.data).get('id')}")
    assert r._status_code == 200

    search = client.get("/v1/publications", data={"filter_blocked": "true"})
    assert search._status_code == 200
    search_data = json.loads(search.data)
    print(search_data)
    assert len(search_data) == 1
    assert search_data[0]["id"] == json.loads(r3.data)["id"]


def test_filter_blocked_false_blockchain_implicit(client, room_zero):
    # UNSET and not blocked
    r1 = client.post("/v1/publications", json=room_zero)
    assert r1._status_code == 200

    # UNSET and blocked
    r2 = client.post("/v1/publications", json=room_zero)
    assert r2._status_code == 200
    r = client.delete(f"/v1/publications/{json.loads(r2.data).get('id')}")
    assert r._status_code == 200

    # CONFIRMED and not blocked
    r3 = client.post("/v1/publications", json=room_zero)
    assert r3._status_code == 200
    r = client.patch(
        f"/v1/publications/{json.loads(r3.data).get('id')}",
        json={"blockchain_status": "CONFIRMED"},
    )
    assert r._status_code == 200

    # CONFIRMED and blocked
    r4 = client.post("/v1/publications", json=room_zero)
    assert r4._status_code == 200
    r = client.patch(
        f"/v1/publications/{json.loads(r4.data).get('id')}",
        json={"blockchain_status": "CONFIRMED"},
    )
    assert r._status_code == 200
    r = client.delete(f"/v1/publications/{json.loads(r4.data).get('id')}")
    assert r._status_code == 200

    search = client.get("/v1/publications", data={"filter_blocked": "false"})
    assert search._status_code == 200
    search_data = json.loads(search.data)
    print(search_data)
    assert len(search_data) == 2
    assert set([search_data[0]["id"], search_data[1]["id"]]) == set(
        [json.loads(r3.data)["id"], json.loads(r4.data)["id"]]
    )
