import requests

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
        """Initialize a new object

        Keyword Arguments:
            season {int or str} -- Season as integer or string (default: {None})
            race {int} -- Race number within the season (default: {None})
            filters {dict} -- Dictionary of desired filters (default: {None})
        """
        self.season = season
        self.race = race
        self.supported_filters = self.ALL_FILTERS
        self.filters = filters

    def check_filters(self) -> None:
        """Check filters are valid"""
        if self.filters is not None:
            for filt in self.filters.keys():
                if filt not in self.supported_filters:
                    self.raise_filter_not_supported(filt)

    def get_data(self) -> str:
        """Get data should be implemented in the child functions

        Returns:
            str -- string to add to the url
        """
        raise NotImplementedError

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

    def call(self) -> str:
        """Submit a call to the Ergast API

        Returns:
            str -- json response from the api
        """
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
    """Query object for querying Season level data"""

    def __init__(self, season=None, race=None, filters=None) -> None:
        super(QuerySeason, self).__init__(season=season, race=race, filters=filters)

        if self.season is not None:
            self.raise_season_not_supported()

        if self.race is not None:
            self.raise_race_not_supported()

        self.check_filters()

    def get_data(self) -> str:
        """Return data for seasons. Seasons does not have subfiltering
        directly on it and does not support season and race specifications.

        Returns:
            str -- string to add to url
        """
        return "/seasons"
