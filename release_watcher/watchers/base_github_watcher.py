
import logging
import json
import time
from typing import Dict, Sequence
import requests

from release_watcher.watchers.watcher_models \
    import WatchError
from release_watcher.watchers.watcher_manager \
    import Watcher, WatcherConfig

logger = logging.getLogger(__name__)


class BaseGithubConfig(WatcherConfig):
    """Class to store the configuration for a BaseGithubWatcher"""

    repo: str = None
    rate_limit_wait_max: int = 120

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
        return self._do_call_api(github_url, headers)

    def _do_call_api(self, github_url: str, headers: Dict) \
            -> Sequence[Dict]:

        response = requests.get(github_url, headers=headers)

        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            logger.debug('Github api call failed : code = %s, content = %s' %
                         (response.status_code, response.content))

            if response.headers.get('X-RateLimit-Remaining') == "0":
                return self._handle_rate_limit(github_url, headers, response)
            else:
                raise WatchError("Github api call failed : %s" % response)

    def _handle_rate_limit(self, github_url: str, headers: Dict, response) \
            -> Sequence[Dict]:
        rl_limit = int(response.headers.get('X-RateLimit-Limit'))
        rl_reset = int(response.headers.get('X-RateLimit-Reset'))
        logger.info('Rate limit exeeded (%d)' % rl_limit)

        if rl_reset:
            rl_reset_sec = rl_reset - int(time.time())

            if rl_reset_sec <= self.config.rate_limit_wait_max:
                logger.debug('Rate limit will reset in %d seconds, waiting ...'
                             % rl_reset_sec)
                time.sleep(rl_reset_sec)
                self._do_call_api(github_url, headers)
            else:
                raise WatchError(
                    "Github rate limit exeeded, "
                    "and reset is too far (%ds > %ds)"
                    % (rl_reset_sec, self.config.rate_limit_wait_max))
