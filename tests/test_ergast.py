import pytest

from formula1.ergast import ErgastFilters, QueryBase, QuerySeason


class TestQueries(object):
    @pytest.mark.parametrize(
        "filter,supported",
        [
            (ErgastFilters.CIRCUITS, True),
            (ErgastFilters.CONSTRUCTORS, True),
            (ErgastFilters.DRIVERS, True),
            (ErgastFilters.GRID, True),
            (ErgastFilters.RESULTS, True),
            (ErgastFilters.FASTEST, True),
            (ErgastFilters.STATUS, True),
            ("bad_filter", False),
        ],
    )
    def test_ergast_query_default_filters(self, filter, supported):

        query = QueryBase(season="current", race=None, filters={filter: 1})
        if supported:
            query.check_filters()
        else:
            with pytest.raises(ValueError):
                query.check_filters()

    def test_ergast_season_call(self):
        query = QuerySeason(season=None, race=None, filters=None)
        data = query.call()
        assert data

    def test_ergast_season_query(self):
        query = QuerySeason(season=None, race=None, filters=None)
        query_url = query.get_url()

        assert query_url == "https://ergast.com/api/f1/seasons"

        query = QuerySeason(season=None, race=None, filters={ErgastFilters.RESULTS: 1})
        query_url = query.get_url()

        assert query_url == "https://ergast.com/api/f1/results/1/seasons"

        query = QuerySeason(
            season=None,
            race=None,
            filters={ErgastFilters.RESULTS: 1, ErgastFilters.DRIVERS: 1},
        )
        query_url = query.get_url()

        assert query_url == "https://ergast.com/api/f1/results/1/drivers/1/seasons"
