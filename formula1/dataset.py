from formula1.ergast import QuerySeason


class ErgastDataset(object):
    def __init__(self) -> None:
        pass

    def build_dataset(self, season=None):
        query_season = QuerySeason()
        return query_season.call()
