
import logging
from typing import Dict, Sequence
from abc import ABCMeta
import json
import time
import requests
from release_watcher.watchers.watcher_models import WatchError
from release_watcher.watchers.watcher_manager import Watcher, WatcherConfig

logger = logging.getLogger(__name__)


class BaseGithubConfig(WatcherConfig):
    """Class to store the configuration for a BaseGithubWatcher"""

    repo: str = None
    username: str = None
    password: str = None
    timeout: float
    rate_limit_wait_max: int

    def __init__(self, watcher_type_name: str, name: str, repo: str):
        super().__init__(watcher_type_name, name)
        self.repo = repo


class BaseGithubWatcher(Watcher, metaclass=ABCMeta):
    """Base Watcher that implements Github related methods"""

    def _call_github_api(self, api_url: str) -> Sequence[Dict]:
        if api_url.startswith('http'):
            github_url = api_url
        else:
            github_url = f'https://api.github.com/repos/{self.config.repo}/{api_url}'
        headers = {'Content-Type': 'application/json'}
        return self._do_call_api(github_url, headers)

    def _do_call_api(self, github_url: str, headers: Dict) -> Sequence[Dict]:

        if self.config.username:
            auth = (self.config.username, self.config.password)
        else:
            auth = None

        response = requests.get(github_url, headers=headers, auth=auth, timeout=self.config.timeout)

        if response.status_code == 200:
            res = json.loads(response.content.decode('utf-8'))
        else:
            logger.debug('Github api call failed : code = %s, content = %s',
                         response.status_code, response.content)

            if response.headers.get('X-RateLimit-Remaining') == '0':
                res = self._handle_rate_limit(github_url, headers, response)
            else:
                raise WatchError(f'Github api call failed : {response}')

        return res

    def _handle_rate_limit(self, github_url: str, headers: Dict, response) -> Sequence[Dict]:
        rl_limit = int(response.headers.get('X-RateLimit-Limit'))
        rl_reset = int(response.headers.get('X-RateLimit-Reset'))
        logger.info('Rate limit exeeded (%d)', rl_limit)

        if rl_reset:
            rl_reset_sec = rl_reset - int(time.time())

            if rl_reset_sec <= self.config.rate_limit_wait_max:
                logger.debug('Rate limit will reset in %d seconds, waiting ...', rl_reset_sec)
                time.sleep(rl_reset_sec)
                return self._do_call_api(github_url, headers)

            raise WatchError('Github rate limit exeeded, and reset is too far '
                             f'({rl_reset_sec}s > {self.config.rate_limit_wait_max}s)')

        raise WatchError('Github rate limit exeeded with no reset')
