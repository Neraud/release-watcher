import datetime
from typing import Sequence


class WatchError(Exception):
    """Exception raised when a watcher fails"""
    message: str = None

    def __init__(self, message: str):
        self.message = message


class Release:
    """Model for a release"""

    name: str = None
    release_date: datetime = None

    def __init__(self, name: str, release_date: datetime):
        self.name = name
        self.release_date = release_date

    def __repr__(self):
        return 'Release(%s, %s)' % (self.name, self.release_date)


class WatchResult:
    """Model for the result of a watch"""

    config = None
    current_release: Release = None
    missed_releases: Sequence[Release] = None
    most_recent_release: Release = None

    def __init__(self, config, current_release: Release,
                 missed_releases: Sequence[Release]):
        self.config = config
        self.current_release = current_release
        self.missed_releases = missed_releases

        if missed_releases:
            self.most_recent_release = missed_releases[0]
