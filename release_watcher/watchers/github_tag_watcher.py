import logging
from typing import Sequence
import re
import dateutil.parser
from release_watcher.config_models import CommonConfig
from release_watcher.watchers.watcher_models import Release, WatchResult
from release_watcher.watchers.watcher_manager import WatcherType
from release_watcher.watchers.base_github_watcher import BaseGithubWatcher, BaseGithubConfig

logger = logging.getLogger(__name__)

WATCHER_TYPE_NAME = 'github_tag'


class GithubTagWatcherConfig(BaseGithubConfig):
    """Class to store the configuration for a GithubTagWatcher"""

    tag: str = None
    includes: Sequence[str] = []
    excludes: Sequence[str] = []

    def __init__(self, name: str, repo: str, tag: str,
                 includes: Sequence[str], excludes: Sequence[str]):
        super().__init__(WATCHER_TYPE_NAME, name, repo)
        self.tag = tag
        self.includes = includes
        self.excludes = excludes

    def __str__(self) -> str:
        return f'{self.repo}:{self.tag}'


class GithubTagWatcher(BaseGithubWatcher):
    """Implementation of a Watcher that checks for new tags in a GitHub repository"""

    def __init__(self, config: GithubTagWatcherConfig):
        super().__init__(config)

    def _do_watch(self) -> WatchResult:
        logger.debug('Watching Github tag %s', self.config)
        response = self._call_github_api('tags')

        current_tag_name = self.config.tag
        current_tag = None
        missed_tags = []

        for include_re in self.config.includes:
            response = [
                tag for tag in response
                if re.compile(include_re).match(tag['name'])
            ]

        for exclude_re in self.config.excludes:
            response = [
                tag for tag in response
                if not re.compile(exclude_re).match(tag['name'])
            ]

        for tag in response:
            new_tag_name = tag['name']
            logger.debug(' - %s', new_tag_name)

            commit_url = tag['commit']['url']
            commit = self._call_github_api(commit_url)
            new_tag_date_string = commit['commit']['committer']['date']
            new_tag_date = dateutil.parser.parse(new_tag_date_string)
            new_tag = Release(new_tag_name, new_tag_date)

            if new_tag_name == current_tag_name:
                logger.debug('Current tag %s found', current_tag_name)
                current_tag = new_tag
                break

            missed_tags.append(new_tag)

        if not current_tag:
            logger.warning('Current tag %s not found !', current_tag_name)

        logger.debug('Missed tags : %s', missed_tags)
        return WatchResult(self.config, current_tag, missed_tags)


class GithubTagWatcherType(WatcherType):
    """Class to represent the GithubTagWatcher type of Watcher"""

    def __init__(self):
        super().__init__(WATCHER_TYPE_NAME)

    def parse_config(self, common_config: CommonConfig, watcher_config) -> GithubTagWatcherConfig:
        repo = watcher_config['repo']
        tag = str(watcher_config['tag'])

        includes = watcher_config.get('includes', [])
        excludes = watcher_config.get('excludes', [])
        name = watcher_config.get('name', repo)

        config = GithubTagWatcherConfig(name, repo, tag, includes, excludes)
        config.username = watcher_config.get('username', common_config.github.username)
        config.password = watcher_config.get('password', common_config.github.password)
        config.timeout = watcher_config.get('timeout', common_config.github.timeout)
        config.rate_limit_wait_max = watcher_config.get(
            'rate_limit_wait_max', common_config.github.rate_limit_wait_max)

        return config

    def create_watcher(self, watcher_config: GithubTagWatcherConfig) -> GithubTagWatcher:
        return GithubTagWatcher(watcher_config)
