import logging
from typing import Dict
import dateutil.parser
from release_watcher.config_models import CommonConfig
from release_watcher.watchers.watcher_models import Release, WatchResult
from release_watcher.watchers.watcher_manager import WatcherType
from release_watcher.watchers.base_github_watcher import BaseGithubWatcher, BaseGithubConfig

logger = logging.getLogger(__name__)

WATCHER_TYPE_NAME = 'github_commit'


class GithubCommitWatcherConfig(BaseGithubConfig):
    """Class to store the configuration for a GithubCommitWatcher"""

    branch: str = None
    commit: str = None

    def __init__(self, name: str, repo: str, branch: str, commit: str):
        super().__init__(WATCHER_TYPE_NAME, name, repo)
        self.branch = branch
        self.commit = commit

    def __str__(self) -> str:
        return f'{self.repo}:{self.branch}'


class GithubCommitWatcher(BaseGithubWatcher):
    """Implementation of a Watcher that checks for new commits in a GitHub repository"""

    def __init__(self, config: GithubCommitWatcherConfig):
        super().__init__(config)

    def _do_watch(self) -> WatchResult:
        logger.debug('Watching Github commit %s', self.config)
        api_url = f'commits?sha={self.config.branch}'
        response = self._call_github_api(api_url)
        current_commit_hash = self.config.commit
        current_commit_release = None
        missed_commits = []

        for commit in response:
            new_commit = commit['sha']
            logger.debug(' - %s', new_commit)

            new_commit_date = dateutil.parser.parse(
                commit['commit']['committer']['date'])
            commit = Release(new_commit, new_commit_date)

            if new_commit == current_commit_hash:
                logger.debug('Current commit %s found', current_commit_hash)
                current_commit_release = commit
                break

            missed_commits.append(commit)

        if not current_commit_release:
            logger.warning('Current commit %s not found !',
                           current_commit_hash)

        logger.debug('Missed commits : %s', missed_commits)
        return WatchResult(self.config, current_commit_release, missed_commits)


class GithubCommitWatcherType(WatcherType):
    """Class to represent the GithubCommitWatcher type of Watcher"""

    def __init__(self):
        super().__init__(WATCHER_TYPE_NAME)

    def parse_config(self, common_config: CommonConfig, watcher_config: Dict):
        repo = watcher_config['repo']
        branch = watcher_config['branch']
        commit = str(watcher_config['commit'])
        name = watcher_config.get('name', repo)

        config = GithubCommitWatcherConfig(name, repo, branch, commit)
        config.username = watcher_config.get('username', common_config.github.username)
        config.password = watcher_config.get('password', common_config.github.password)
        config.timeout = watcher_config.get('timeout', common_config.github.timeout)
        config.rate_limit_wait_max = watcher_config.get(
            'rate_limit_wait_max', common_config.github.rate_limit_wait_max)

        return config

    def create_watcher(self, watcher_config: GithubCommitWatcherConfig
                       ) -> GithubCommitWatcher:
        return GithubCommitWatcher(watcher_config)
