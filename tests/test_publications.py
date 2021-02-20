"""Sample test suite."""
import pytest

from publications_microservice.app import create_app


@pytest.fixture
def client():
    with create_app().test_client() as test_client:
        yield test_client


def test_root(client):  # pylint:disable=redefined-outer-name
    response = client.get("/")
    data = response.data
    assert data is not None
