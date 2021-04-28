import pytest

from formula1.ergast import (
    ErgastFilters,
    QueryBase,
    QueryRaceResults,
    QueryRaceSchedule,
    QuerySeason,
    QueryQualifyingResults,
)


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
        if supported:
            QueryBase(season=None, race=None, filters={filter: 1})
        else:
            with pytest.raises(ValueError):
                QueryBase(season=None, race=None, filters={filter: 1})

    @pytest.mark.parametrize(
        "supports,requires,season,result",
        [
            (True, False, None, True),
            (True, True, "current", True),
            (True, True, 1950, True),
            (True, True, 2000, True),
            (True, True, 2021, True),
            # Season not allowed string
            (False, False, "current", False),
            # Season not allowed int
            (False, False, 2000, False),
            # Season required but not provided
            (True, True, None, False),
            # Season is bad values
            (True, True, "junk", False),
            (True, True, 1949, False),
            (True, True, 2022, False),
        ],
    )
    def test_ergast_season_values(self, supports, requires, season, result):
        class TestQuery(QueryBase):
            supports_race = False
            supports_season = supports
            requires_season = requires

        if result:
            TestQuery(season=season)
        else:
            with pytest.raises(ValueError):
                TestQuery(season=season)

    @pytest.mark.parametrize(
        "supports,requires,race,result",
        [
            (True, False, None, True),
            (True, True, 1, True),
            (True, True, 10, True),
            (True, True, 23, True),
            # Race not allowed
            (False, False, 1, False),
            # Race required but not provided
            (True, True, None, False),
            # Race is bad values
            (True, True, 0, False),
            (True, True, 24, False),
        ],
    )
    def test_ergast_race_values(self, supports, requires, race, result):
        class TestQuery(QueryBase):
            supports_season = False
            supports_race = supports
            requires_race = requires

        if result:
            TestQuery(race=race)
        else:
            with pytest.raises(ValueError):
                TestQuery(race=race)

    def test_ergast_season_call(self):
        query = QuerySeason(season=None, race=None, filters=None)
        data = query.call()
        assert data is not None

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

    def test_ergast_season_query_takes_no_season_or_race(self):
        with pytest.raises(ValueError):
            QuerySeason(season="something", race=None, filters=None)

        with pytest.raises(ValueError):
            QuerySeason(season=None, race="something", filters=None)

        with pytest.raises(ValueError):
            QuerySeason(season="something", race="something", filters=None)

    def test_ergast_race_schedule_query(self):
        query = QueryRaceSchedule(season="current", race=None, filters=None)
        query_url = query.get_url()

        assert query_url == "https://ergast.com/api/f1/current"

        query = QueryRaceSchedule(season="current", race=2, filters=None)
        query_url = query.get_url()

        assert query_url == "https://ergast.com/api/f1/current/2"

        query = QueryRaceSchedule(
            season="current", race=2, filters={ErgastFilters.RESULTS: 1}
        )
        query_url = query.get_url()

        assert query_url == "https://ergast.com/api/f1/results/1/current/2"

        query = QueryRaceSchedule(
            season="current",
            race=2,
            filters={ErgastFilters.RESULTS: 1, ErgastFilters.DRIVERS: 1},
        )
        query_url = query.get_url()

        assert query_url == "https://ergast.com/api/f1/results/1/drivers/1/current/2"

    def test_ergast_race_schedule_query_requires_season(self):
        with pytest.raises(ValueError):
            QueryRaceSchedule(season=None, race=None, filters=None)

    def test_ergast_race_results_query(self):
        query = QueryRaceResults(season="current", race=2, filters=None)
        query_url = query.get_url()

        assert query_url == "https://ergast.com/api/f1/current/2/results"

        query = QueryRaceResults(
            season="current", race=2, filters={ErgastFilters.GRID: 1}
        )
        query_url = query.get_url()

        assert query_url == "https://ergast.com/api/f1/grid/1/current/2/results"

        query = QueryRaceResults(
            season="current",
            race=2,
            filters={ErgastFilters.GRID: 1, ErgastFilters.DRIVERS: 1},
        )
        query_url = query.get_url()

        assert (
            query_url == "https://ergast.com/api/f1/grid/1/drivers/1/current/2/results"
        )

    def test_ergast_race_results_query_requires_season_and_race(self):
        with pytest.raises(ValueError):
            QueryRaceResults(season=None, race=None, filters=None)

        with pytest.raises(ValueError):
            QueryRaceResults(season="current", race=None, filters=None)

    def test_ergast_race_results_query_does_not_support_results(self):
        with pytest.raises(ValueError):
            QueryRaceResults(
                season="current", race=1, filters={ErgastFilters.RESULTS: 1}
            )

    def test_ergast_qualifying_results_query(self):
        query = QueryQualifyingResults(season="current", race=2, filters=None)
        query_url = query.get_url()

        assert query_url == "https://ergast.com/api/f1/current/2/qualifying"

        query = QueryQualifyingResults(
            season="current", race=2, filters={ErgastFilters.GRID: 1}
        )
        query_url = query.get_url()

        assert query_url == "https://ergast.com/api/f1/grid/1/current/2/qualifying"

        query = QueryQualifyingResults(
            season="current",
            race=2,
            filters={ErgastFilters.GRID: 1, ErgastFilters.DRIVERS: 1},
        )
        query_url = query.get_url()

        assert (
            query_url
            == "https://ergast.com/api/f1/grid/1/drivers/1/current/2/qualifying"
        )
