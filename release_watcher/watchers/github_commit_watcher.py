import logging
import json
import dateutil.parser
from typing import Dict, Sequence
from release_watcher.config_models \
    import CommonConfig
from release_watcher.watchers.watcher_models \
    import Release, WatchError, WatchResult
from release_watcher.watchers.watcher_manager \
    import Watcher, WatcherConfig, WatcherType
from release_watcher.watchers.base_github_watcher \
    import BaseGithubWatcher, BaseGithubConfig

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
        return '%s:%s' % (self.repo, self.branch)


class GithubCommitWatcher(BaseGithubWatcher):
    """Implementation of a Watcher that checks for new commits in a GitHub
    repository"""

    def __init__(self, config: GithubCommitWatcherConfig):
        super().__init__(config)

    def _do_watch(self) -> WatchResult:
        logger.debug("Watching Github commit %s" % self.config)
        api_url = 'commits?sha=%s' % self.config.branch
        response = self._call_github_api(api_url)
        current_commit_hash = self.config.commit
        current_commit_release = None
        missed_commits = []

        for commit in response:
            new_commit = commit['sha']
            logger.debug(" - %s" % new_commit)

            new_commit_date = dateutil.parser.parse(
                commit['commit']['committer']['date'])
            commit = Release(new_commit, new_commit_date)

            if new_commit == current_commit_hash:
                logger.debug("Current commit '%s' found" % current_commit_hash)
                current_commit_release = commit
                break

            missed_commits.append(commit)

        if not current_commit_release:
            logger.warning("Current commit '%s' not found !",
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

        return GithubCommitWatcherConfig(name, repo, branch, commit)

    def create_watcher(self, watcher_config: GithubCommitWatcherConfig
                       ) -> GithubCommitWatcher:
        return GithubCommitWatcher(watcher_config)
