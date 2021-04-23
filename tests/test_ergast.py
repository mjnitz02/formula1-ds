import pytest

from formula1.ergast import ErgastClient

class TestErgastRequest(object):

    @pytest.fixture
    def ergast_client(self):
        return ErgastClient()

    def test_ergast_connection(self, ergast_client):
        pass