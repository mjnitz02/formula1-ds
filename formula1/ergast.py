import requests
import numpy as np

from pandas import DataFrame

"""
This package provides interfaces to the Ergast API.

The Ergast Developer API is an experimental web service which provides
a historical record of motor racing data for non-commercial purposes.
Please read the terms and conditions of use. The API provides data
for the Formula One series, from the beginning of the world
championships in 1950.

Overview
All API queries require a GET request using a URL of the form:
http[s]://ergast.com/api/<series>/<season>/<round>/...
"""


class ErgastFilters(object):
    """List of common enums for Ergast filters"""

    CIRCUITS = "circuits"
    CONSTRUCTORS = "constructors"
    DRIVERS = "drivers"
    GRID = "grid"
    RESULTS = "results"
    FASTEST = "fastest"
    STATUS = "status"


class QueryBase(object):
    """Base object for querying against Ergast APIs"""

    BASE_URL = "https://ergast.com/api/f1"
    URL_FORMAT = "{base}{filter}{data}"
    SUPPORTED_FILTERS = [
        ErgastFilters.CIRCUITS,
        ErgastFilters.CONSTRUCTORS,
        ErgastFilters.DRIVERS,
        ErgastFilters.GRID,
        ErgastFilters.RESULTS,
        ErgastFilters.FASTEST,
        ErgastFilters.STATUS,
    ]

    supports_season = False
    requires_season = False
    supports_race = False
    requires_race = False
    supports_lap = False
    requires_lap = False

    def __init__(self, season=None, race=None, lap=None, filters=None):
        """Initialize a new object

        Keyword Arguments:
            season {int or str} -- Season as integer or string (default: {None})
            race {int} -- Race number within the season (default: {None})
            filters {dict} -- Dictionary of desired filters (default: {None})
        """
        self.season = season
        self.race = race
        self.lap = lap
        self.supported_filters = self.SUPPORTED_FILTERS
        self.filters = filters

        self.check_season()
        self.check_race()
        self.check_lap()
        self.check_filters()

    def check_filters(self) -> None:
        """Check filters are valid"""
        if self.filters is not None:
            for filt in self.filters.keys():
                if filt not in self.supported_filters:
                    self.raise_filter_not_supported(filt)

    def check_season(self) -> None:
        """Check the season value is valid"""
        if self.supports_season:
            if self.requires_season and self.season is None:
                raise ValueError("Season is required for this query")

            if isinstance(self.season, str):
                if self.season != "current":
                    raise ValueError(
                        "Season supports the string value 'current' or an integer between 1950 and 2021"
                    )
            elif self.season is not None:
                self.season = np.int(self.season)
                if self.season < 1950 or self.season > 2021:
                    raise ValueError(
                        "Season supports the string value 'current' or integers between 1950 and 2021"
                    )
        else:
            if self.season is not None:
                raise ValueError("Season is not supported for this query")

    def check_race(self) -> None:
        """Check the season value is valid"""
        if self.supports_race:
            if self.requires_race and self.race is None:
                raise ValueError("Race is required for this query")

            if self.race is not None:
                self.race = np.int(self.race)
                if self.race < 1 or self.race > 23:
                    raise ValueError("Race supports integers between 1 and 23")
        else:
            if self.race is not None:
                raise ValueError("Race is not supported for this query")

    def check_lap(self) -> None:
        """Check the season value is valid"""
        if self.supports_lap:
            if self.requires_lap and self.lap is None:
                raise ValueError("Lap is required for this query")

            if self.lap is not None:
                self.lap = np.int(self.lap)
                if self.lap < 1:
                    raise ValueError("Lap supports integers values greater than 1")
                if self.lap > 100:
                    raise ValueError("No races have more than 100 laps")
        else:
            if self.lap is not None:
                raise ValueError("Lap is not supported for this query")

    def get_data(self) -> str:
        """Get data should be implemented in the child functions

        Returns:
            str -- string to add to the url
        """
        raise NotImplementedError

    def format_data(self, json_data) -> DataFrame:
        return json_data

    def get_filter(self) -> str:
        """Concatenate filters together

        Returns:
            str -- string to add to the url
        """
        filters = ""
        if self.filters is not None:
            for filter, value in self.filters.items():
                filters += "/{}/{}".format(filter, value)
        return filters

    def get_url(self) -> str:
        """Combine pieces of request into a final url

        Returns:
            str -- url for request
        """
        data = self.get_data()
        filter = self.get_filter()
        return self.URL_FORMAT.format(base=self.BASE_URL, data=data, filter=filter)

    def call(self, keep_url=False) -> str:
        """Submit a call to the Ergast API

        Returns:
            str -- json response from the api
        """
        r = requests.get("{}.json".format(self.get_url()))

        assert r.status_code == 200
        json_data = r.json()
        formatted_data = self.format_data(json_data)

        if not keep_url:
            if (
                isinstance(formatted_data, DataFrame)
                and "url" in formatted_data.columns
            ):
                formatted_data = formatted_data.drop(columns=["url"])

        return formatted_data

    def raise_season_required(self) -> None:
        raise ValueError("Season is required for this query")

    def raise_season_not_supported(self) -> None:
        raise ValueError("Season is not supported for this query")

    def raise_race_not_supported(self) -> None:
        raise ValueError("Race is not supported for this query")

    def raise_filter_not_supported(self, filter) -> None:
        raise ValueError("Filter '{}' is not supported for this query".format(filter))


class QuerySeason(QueryBase):
    """Query object for querying Season level data"""

    def __init__(self, **kwargs) -> None:
        super(QuerySeason, self).__init__(**kwargs)

    def get_data(self) -> str:
        """Return data for seasons. Seasons does not have subfiltering
        directly on it and does not support season and race specifications.

        Returns:
            str -- string to add to url
        """
        return "/seasons"

    def format_data(self, json_data) -> DataFrame:
        return DataFrame(json_data["MRData"]["SeasonTable"]["Seasons"])


class QueryRaceSchedule(QueryBase):
    """Query object for querying Season level data"""

    supports_season = True
    requires_season = True
    supports_race = True

    def __init__(self, **kwargs) -> None:
        super(QueryRaceSchedule, self).__init__(**kwargs)

    def get_data(self) -> str:
        """Return data for seasons. Seasons does not have subfiltering
        directly on it and does not support season and race specifications.

        Returns:
            str -- string to add to url
        """
        if self.race:
            return "/{}/{}".format(self.season, self.race)
        else:
            return "/{}".format(self.season)

    def format_data(self, json_data) -> DataFrame:
        return DataFrame(json_data["MRData"]["RaceTable"]["Races"])


class QueryRaceResults(QueryBase):
    """Query object for querying Season level data"""

    supports_season = True
    requires_season = True
    supports_race = True
    requires_race = True

    SUPPORTED_FILTERS = [
        ErgastFilters.CIRCUITS,
        ErgastFilters.CONSTRUCTORS,
        ErgastFilters.DRIVERS,
        ErgastFilters.GRID,
        ErgastFilters.FASTEST,
        ErgastFilters.STATUS,
    ]

    def __init__(self, **kwargs) -> None:
        super(QueryRaceResults, self).__init__(**kwargs)

    def get_data(self) -> str:
        """Return data for seasons. Seasons does not have subfiltering
        directly on it and does not support season and race specifications.

        Returns:
            str -- string to add to url
        """
        if self.race:
            return "/{}/{}/results".format(self.season, self.race)
        else:
            return "/{}/results".format(self.season)

    def format_data(self, json_data) -> DataFrame:
        return DataFrame(json_data["MRData"]["RaceTable"]["Races"][0]["Results"])


class QueryQualifyingResults(QueryBase):
    """Query object for querying Season level data"""

    supports_season = True
    requires_season = True
    supports_race = True
    requires_race = True

    def __init__(self, **kwargs) -> None:
        super(QueryQualifyingResults, self).__init__(**kwargs)

    def get_data(self) -> str:
        """Return data for seasons. Seasons does not have subfiltering
        directly on it and does not support season and race specifications.

        Returns:
            str -- string to add to url
        """
        if self.race:
            return "/{}/{}/qualifying".format(self.season, self.race)
        else:
            return "/{}/qualifying".format(self.season)

    def format_data(self, json_data) -> DataFrame:
        return DataFrame(
            json_data["MRData"]["RaceTable"]["Races"][0]["QualifyingResults"]
        )


class QueryLapTimes(QueryBase):
    """Query object for querying Season level data"""

    supports_season = True
    requires_season = True
    supports_race = True
    requires_race = True
    supports_lap = True
    requires_lap = True

    SUPPORTED_FILTERS = []

    def __init__(self, **kwargs) -> None:
        super(QueryLapTimes, self).__init__(**kwargs)

    def get_data(self) -> str:
        """Return data for seasons. Seasons does not have subfiltering
        directly on it and does not support season and race specifications.

        Returns:
            str -- string to add to url
        """
        return "/{}/{}/laps/{}".format(self.season, self.race, self.lap)

    def format_data(self, json_data) -> DataFrame:
        return DataFrame(
            json_data["MRData"]["RaceTable"]["Races"][0]["Laps"]["Timings"]
        )
