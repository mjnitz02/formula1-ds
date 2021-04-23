import requests
import numpy as np

from typing import Tuple


class ErgastSeasons(object):
    CURRENT = "current"


class ErgastFilters(object):
    CIRCUITS = "circuits"
    CONSTRUCTORS = "constructors"
    DRIVERS = "drivers"
    GRID = "grid"
    RESULTS = "results"
    FASTEST = "fastest"
    STATUS = "status"


class QueryBase(object):
    BASE_URL = "https://ergast.com/api/f1"
    URL_FORMAT = "{base}{filter}{data}"
    ALL_FILTERS = [
        ErgastFilters.CIRCUITS,
        ErgastFilters.CONSTRUCTORS,
        ErgastFilters.DRIVERS,
        ErgastFilters.GRID,
        ErgastFilters.RESULTS,
        ErgastFilters.FASTEST,
        ErgastFilters.STATUS,
    ]

    def __init__(self, season=None, race=None, filters=None):
        self.season = season
        self.race = race
        self.supported_filters = self.ALL_FILTERS
        self.filters = filters

    def check_filters(self) -> None:
        if self.filters is not None:
            for filt in self.filters.keys():
                if filt not in self.supported_filters:
                    self.raise_filter_not_supported(filt)

    def get_data(self) -> str:
        raise NotImplementedError

    def get_filter(self) -> str:
        filters = ""
        if self.filters is not None:
            for filter, value in self.filters.items():
                filters += "/{}/{}".format(filter, value)
        return filters

    def get_url(self) -> str:
        data = self.get_data()
        filter = self.get_filter()
        return self.URL_FORMAT.format(base=self.BASE_URL, data=data, filter=filter)

    def call(self) -> str:
        r = requests.get("{}.json".format(self.get_url()))

        assert r.status_code == 200
        json_data = r.json()

        return json_data

    def raise_season_not_supported(self) -> None:
        raise ValueError("Season is not supported for this query")

    def raise_race_not_supported(self) -> None:
        raise ValueError("Race is not supported for this query")

    def raise_filter_not_supported(self, filter) -> None:
        raise ValueError("Filter '{}' is not supported for this query".format(filter))


class QuerySeason(QueryBase):
    def __init__(self, season=None, race=None, filters=None) -> None:
        super(QuerySeason, self).__init__(season=season, race=race, filters=filters)

        if self.season is not None:
            self.raise_season_not_supported()

        if self.race is not None:
            self.raise_race_not_supported()

        self.check_filters()

    def get_data(self) -> str:
        return "/seasons"
