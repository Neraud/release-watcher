import logging
import json
import requests
import dateutil.parser
from typing import Dict, Sequence
from release_watcher.watchers.watcher_models \
    import Release, WatchError, WatchResult
from release_watcher.watchers.watcher_manager \
    import Watcher, WatcherConfig, WatcherType

logger = logging.getLogger(__name__)

WATCHER_NAME = 'github_commit'


class GithubCommitWatcherConfig(WatcherConfig):
    """Class to store the configuration for a GithubCommitWatcher"""

    repo: str = None
    branch: str = None
    commit: str = None

    def __init__(self, repo: str, branch: str, commit: str):
        super().__init__(WATCHER_NAME)
        self.repo = repo
        self.branch = branch
        self.commit = commit

    def __str__(self) -> str:
        return '%s:%s' % (self.repo, self.branch)


class GithubCommitWatcher(Watcher):
    """Implementation of a Watcher that checks for new commits in a GitHub
    repository"""

    def __init__(self, config: GithubCommitWatcherConfig):
        super().__init__(config)

    def _do_watch(self) -> WatchResult:
        logger.debug("Watching Github commit %s" % self.config)
        response = self._call_github_api()
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

    def _call_github_api(self) -> Sequence[Dict]:
        github_repo_url = 'https://api.github.com/repos/%s/commits?sha=%s'\
            % (self.config.repo, self.config.branch)
        headers = {'Content-Type': 'application/json'}
        response = requests.get(github_repo_url, headers=headers)

        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            logger.debug('Github api call failed : code = %s, content = %s' %
                         (response.status_code, response.content))
            raise WatchError("Github api call failed : %s" % response)


class GithubCommitWatcherType(WatcherType):
    """Class to represent the GithubCommitWatcher type of Watcher"""

    def __init__(self):
        super().__init__(WATCHER_NAME)

    def parse_config(self, watcher_config: Dict):
        repo = watcher_config['repo']
        branch = watcher_config['branch']
        commit = str(watcher_config['commit'])

        return GithubCommitWatcherConfig(repo, branch, commit)

    def create_watcher(self, watcher_config: GithubCommitWatcherConfig
                       ) -> GithubCommitWatcher:
        return GithubCommitWatcher(watcher_config)
