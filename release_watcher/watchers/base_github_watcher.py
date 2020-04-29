
import logging
import json
from typing import Dict, Sequence
import requests

from release_watcher.watchers.watcher_manager \
    import Watcher, WatcherConfig

logger = logging.getLogger(__name__)

class BaseGithubConfig(WatcherConfig):
    """Class to store the configuration for a BaseGithubWatcher"""

    repo: str = None

    def __init__(self, watcher_type_name: str, name: str, repo: str):
        super().__init__(watcher_type_name, name)
        self.repo = repo


class BaseGithubWatcher(Watcher):
    """Base Watcher that implements Github related methods"""

    def __init__(self, config: WatcherConfig):
        super().__init__(config)

    def _call_github_api(self, api_url: str) -> Sequence[Dict]:
        if api_url.startswith('http'):
            github_url = api_url
        else:
            github_url = 'https://api.github.com/repos/%s/%s'\
                % (self.config.repo, api_url)
        headers = {'Content-Type': 'application/json'}
        response = requests.get(github_url, headers=headers)

        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            logger.debug('Github api call failed : code = %s, content = %s' %
                         (response.status_code, response.content))
            raise WatchError("Github api call failed : %s" % response)
