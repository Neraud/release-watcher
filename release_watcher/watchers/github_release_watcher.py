import logging
from typing import Dict, Sequence
import re
import dateutil.parser
from release_watcher.config_models import CommonConfig
from release_watcher.watchers.watcher_models import Release, WatchResult
from release_watcher.watchers.watcher_manager import WatcherType
from release_watcher.watchers.base_github_watcher import BaseGithubWatcher, BaseGithubConfig

logger = logging.getLogger(__name__)

WATCHER_TYPE_NAME = 'github_release'


class GithubReleaseWatcherConfig(BaseGithubConfig):
    """Class to store the configuration for a GithubReleaseWatcher"""

    release: str = None
    includes: Sequence[str] = []
    excludes: Sequence[str] = []

    def __init__(self, name: str, repo: str, release: str,
                 includes: Sequence[str], excludes: Sequence[str]):
        super().__init__(WATCHER_TYPE_NAME, name, repo)
        self.release = release
        self.includes = includes
        self.excludes = excludes

    def __str__(self) -> str:
        return f'{self.repo}:{self.release}'


class GithubReleaseWatcher(BaseGithubWatcher):
    """Implementation of a Watcher that checks for new releases in a GitHub repository"""

    def __init__(self, config: GithubReleaseWatcherConfig):
        super().__init__(config)

    def _do_watch(self) -> WatchResult:
        logger.debug('Watching Github release %s', self.config)
        response = self._call_github_api('releases')
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
            logger.debug(' - %s', new_release_name)

            new_release_date = dateutil.parser.parse(release['published_at'])
            new_release = Release(new_release_name, new_release_date)

            if new_release_name == current_release_name:
                logger.debug('Current release %s found', current_release_name)
                current_release = new_release
                break

            missed_releases.append(new_release)

        if not current_release:
            logger.warning('Current release %s not found !', current_release_name)

        logger.debug('Missed releases : %s', missed_releases)
        return WatchResult(self.config, current_release, missed_releases)


class GithubReleaseWatcherType(WatcherType):
    """Class to represent the GithubReleaseWatcher type of Watcher"""

    def __init__(self):
        super().__init__(WATCHER_TYPE_NAME)

    def parse_config(self, common_config: CommonConfig, watcher_config: Dict) \
            -> GithubReleaseWatcherConfig:
        repo = watcher_config['repo']
        release = str(watcher_config['release'])

        includes = watcher_config.get('includes', [])
        excludes = watcher_config.get('excludes', [])
        name = watcher_config.get('name', repo)

        config = GithubReleaseWatcherConfig(name, repo, release, includes, excludes)

        config.username = watcher_config.get('username', common_config.github.username)
        config.password = watcher_config.get('password', common_config.github.password)
        config.rate_limit_wait_max = watcher_config.get(
            'rate_limit_wait_max', common_config.github.rate_limit_wait_max)

        return config

    def create_watcher(self, watcher_config: GithubReleaseWatcherConfig) -> GithubReleaseWatcher:
        return GithubReleaseWatcher(watcher_config)
