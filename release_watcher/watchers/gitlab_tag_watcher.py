import logging
import json
import re
import requests
import dateutil.parser
import datetime
from typing import Dict, Sequence
from release_watcher.watchers.watcher_models \
    import Release, WatchError, WatchResult
from release_watcher.watchers.watcher_manager \
    import Watcher, WatcherConfig, WatcherType

logger = logging.getLogger(__name__)

WATCHER_NAME = 'github_tag'


class GithubTagWatcherConfig(WatcherConfig):
    """Class to store the configuration for a GithubTagWatcher"""

    repo: str = None
    tag: str = None
    includes: Sequence[str] = []
    excludes: Sequence[str] = []

    def __init__(self, repo: str, tag: str, includes: Sequence[str],
                 excludes: Sequence[str]):
        super().__init__(WATCHER_NAME)
        self.repo = repo
        self.tag = tag
        self.includes = includes
        self.excludes = excludes

    def __str__(self) -> str:
        return '%s:%s' % (self.repo, self.tag)


class GithubTagWatcher(Watcher):
    """Implementation of a Watcher that checks for new tags in a GitHub
    repository"""

    def __init__(self, config: GithubTagWatcherConfig):
        super().__init__(config)

    def _do_watch(self) -> WatchResult:
        logger.debug("Watching Github tag %s" % self.config)
        response = self._fetch_github_tags()
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
            logger.debug(" - %s" % new_tag_name)

            new_tag_date = self._fetch_tag_date(tag)
            new_tag = Release(new_tag_name, new_tag_date)

            if new_tag_name == current_tag_name:
                logger.debug("Current tag '%s' found" % current_tag_name)
                current_tag = new_tag
                break

            missed_tags.append(new_tag)

        if not current_tag:
            logger.warning("Current tag '%s' not found !", current_tag_name)

        logger.debug('Missed tags : %s', missed_tags)
        return WatchResult(self.config, current_tag, missed_tags)

    def _fetch_github_tags(self) -> Sequence[Dict]:
        github_repo_url = 'https://api.github.com/repos/%s/tags' % \
            self.config.repo
        headers = {'Content-Type': 'application/json'}
        response = requests.get(github_repo_url, headers=headers)

        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            logger.debug('Github api call failed : code = %s, content = %s' %
                         (response.status_code, response.content))
            raise WatchError("Github api call failed : %s" % response)

    def _fetch_tag_date(self, tag_response: str) -> datetime:
        commit_url = tag_response['commit']['url']
        headers = {'Content-Type': 'application/json'}
        response = requests.get(commit_url, headers=headers)

        if response.status_code == 200:
            commit = json.loads(response.content.decode('utf-8'))
            return dateutil.parser.parse(commit['commit']['committer']['date'])
        else:
            logger.debug('Github api call failed : code = %s, content = %s' %
                         (response.status_code, response.content))
            raise WatchError("Github api call failed : %s" % response)


class GithubTagWatcherType(WatcherType):
    """Class to represent the GithubTagWatcher type of Watcher"""

    def __init__(self):
        super().__init__(WATCHER_NAME)

    def parse_config(self, watcher_config) -> GithubTagWatcherConfig:
        repo = watcher_config['repo']
        tag = str(watcher_config['tag'])

        includes = watcher_config.get('includes', [])
        excludes = watcher_config.get('excludes', [])

        return GithubTagWatcherConfig(repo, tag, includes, excludes)

    def create_watcher(self, watcher_config: GithubTagWatcherConfig
                       ) -> GithubTagWatcher:
        return GithubTagWatcher(watcher_config)
