import logging
import json
import requests
import re
import dateutil.parser
import datetime
from typing import Dict, Sequence
from release_watcher.watchers.watcher_models \
    import Release, WatchError, WatchResult
from release_watcher.watchers.watcher_manager \
    import Watcher, WatcherConfig, WatcherType

logger = logging.getLogger(__name__)

WATCHER_TYPE_NAME = 'pypi'


class PyPIWatcherConfig(WatcherConfig):
    """Class to store the configuration for a PyPIWatcher"""

    package: str = None
    version: str = None
    includes: Sequence[str] = []
    excludes: Sequence[str] = []

    def __init__(self, name: str, package: str, version: str,
                 includes: Sequence[str], excludes: Sequence[str]):
        super().__init__(WATCHER_TYPE_NAME, name)
        self.package = package
        self.version = version
        self.includes = includes
        self.excludes = excludes

    def __str__(self) -> str:
        return '%s:%s' % (self.package, self.version)


class PyPIWatcher(Watcher):
    """Implementation of a Watcher that checks for new releases of a
    PyPI package"""

    def __init__(self, config: PyPIWatcherConfig):
        super().__init__(config)

    def _do_watch(self) -> WatchResult:
        logger.debug("Watching PyPI %s" % self.config)
        pypi_releases = self._get_all_releases_from_pypi()
        pypi_release_names = pypi_releases.keys()

        for ire in self.config.includes:
            pypi_release_names = [
                r for r in pypi_release_names if re.compile(ire).match(r)
            ]

        for ere in self.config.excludes:
            pypi_release_names = [
                r for r in pypi_release_names if not re.compile(ere).match(r)
            ]

        releases = []
        for r in pypi_release_names:
            if pypi_releases[r]:
                release_date = self._get_release_date(pypi_releases[r])
                releases.append(Release(r, release_date))

        # Sort with most recent first
        releases.sort(key=lambda r: r.release_date, reverse=True)

        current_version = self.config.version
        current_release = None
        missed_releases = []

        for release in releases:
            logger.debug(" - %s" % release.name)
            if release.name == current_version:
                logger.debug("Current release '%s' found" % current_version)
                current_release = release
                break
            missed_releases.append(release)

        if not current_release:
            logger.warning("Current release '%s' not found !", current_version)

        logger.debug('Missed releases : %s', missed_releases)
        return WatchResult(self.config, current_release, missed_releases)

    def _get_all_releases_from_pypi(self) -> Dict:
        api_response = self._call_pypi_api()

        if api_response.status_code == 200:
            content = json.loads(api_response.content.decode('utf-8'))
            return content['releases']
        else:
            raise WatchError("PyPI api call failed, response code %d" %
                             api_response.status_code)

    def _call_pypi_api(self) -> requests.Response:
        pypi_package_url = 'https://pypi.org/pypi/%s/json' % (
            self.config.package)
        headers = {'Content-Type': 'application/json'}

        response = requests.get(pypi_package_url, headers=headers)
        return response

    def _get_release_date(self, items: Sequence) -> datetime:
        dates = [dateutil.parser.parse(i["upload_time"]) for i in items]
        return min(dates)


class PyPIWatcherType(WatcherType):
    """Class to represent the PyPIWatcher type of Watcher"""

    def __init__(self):
        super().__init__(WATCHER_TYPE_NAME)

    def parse_config(self, watcher_config: Dict) -> PyPIWatcherConfig:
        package = watcher_config['package']
        version = str(watcher_config['version'])
        includes = watcher_config.get('includes', [])
        excludes = watcher_config.get('excludes', [])

        name = watcher_config.get('name', '%s:%s' % (package, version))

        return PyPIWatcherConfig(name, package, version, includes, excludes)

    def create_watcher(self, watcher_config: PyPIWatcherConfig) -> PyPIWatcher:
        return PyPIWatcher(watcher_config)
