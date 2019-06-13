import logging
import json
import re
import requests
import dateutil.parser
from typing import Dict, Sequence
from release_watcher.watchers.watcher_models \
    import Release, WatchError, WatchResult
from release_watcher.watchers.watcher_manager \
    import Watcher, WatcherConfig, WatcherType

logger = logging.getLogger(__name__)

WATCHER_NAME = 'github_release'


class GithubReleaseWatcherConfig(WatcherConfig):
    """Class to store the configuration for a GithubReleaseWatcher"""

    repo: str = None
    release: str = None
    includes: Sequence[str] = []
    excludes: Sequence[str] = []

    def __init__(self, repo: str, release: str, includes: Sequence[str],
                 excludes: Sequence[str]):
        super().__init__(WATCHER_NAME)
        self.repo = repo
        self.release = release
        self.includes = includes
        self.excludes = excludes

    def __str__(self) -> str:
        return '%s:%s' % (self.repo, self.release)


class GithubReleaseWatcher(Watcher):
    """Implementation of a Watcher that checks for new releases in a GitHub
    repository"""

    def __init__(self, config: GithubReleaseWatcherConfig):
        super().__init__(config)

    def _do_watch(self) -> WatchResult:
        logger.debug("Watching Github release %s" % self.config)
        response = self._fetch_github_releases()
        current_release_name = self.config.release
        current_release = None
        missed_releases = []

        for include_re in self.config.includes:
            response = [
                release for release in response
                if re.compile(include_re).match(release['tag_name'])
            ]

        for exclude_re in self.config.excludes:
            response = [
                release for release in response
                if not re.compile(exclude_re).match(release['tag_name'])
            ]

        for release in response:
            new_release_name = release['tag_name']
            logger.debug(" - %s" % new_release_name)

            new_release_date = dateutil.parser.parse(release['published_at'])
            new_release = Release(new_release_name, new_release_date)

            if new_release_name == current_release_name:
                logger.debug("Current release '%s' found" %
                             current_release_name)
                current_release = new_release
                break

            missed_releases.append(new_release)

        if not current_release:
            logger.warning("Current release '%s' not found !",
                           current_release_name)

        logger.debug('Missed releases : %s', missed_releases)
        return WatchResult(self.config, current_release, missed_releases)

    def _fetch_github_releases(self) -> Sequence[Dict]:
        github_repo_url = 'https://api.github.com/repos/%s/releases' % \
            self.config.repo
        headers = {'Content-Type': 'application/json'}
        response = requests.get(github_repo_url, headers=headers)

        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            logger.debug('Github api call failed : code = %s, content = %s' %
                         (response.status_code, response.content))
            raise WatchError("Github api call failed : %s" % response)


class GithubReleaseWatcherType(WatcherType):
    """Class to represent the GithubReleaseWatcher type of Watcher"""

    def __init__(self):
        super().__init__(WATCHER_NAME)

    def parse_config(self, watcher_config: Dict) -> GithubReleaseWatcherConfig:
        repo = watcher_config['repo']
        release = str(watcher_config['release'])

        includes = watcher_config.get('includes', [])
        excludes = watcher_config.get('excludes', [])

        return GithubReleaseWatcherConfig(repo, release, includes, excludes)

    def create_watcher(self, watcher_config: GithubReleaseWatcherConfig
                       ) -> GithubReleaseWatcher:
        return GithubReleaseWatcher(watcher_config)
