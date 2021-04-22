import pytest
from formula1.ergast import ErgastClient


class TestErgastRequest():

    @pytest.fixture
    def ergast_client():
        return ErgastClient()

    def test_ergast_connection(ergast_client):
        pass