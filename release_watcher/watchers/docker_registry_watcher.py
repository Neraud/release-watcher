import logging
import json
import requests
import re
import www_authenticate
import dateutil.parser
import datetime
from typing import Dict, Sequence
from release_watcher.watchers.watcher_models \
    import Release, WatchError, WatchResult
from release_watcher.watchers.watcher_manager \
    import Watcher, WatcherConfig, WatcherType

logger = logging.getLogger(__name__)

WATCHER_NAME = 'docker_registry'


class DockerRegistryWatcherConfig(WatcherConfig):
    """Class to store the configuration for a DockerRegistryWatcher"""

    repo: str = None
    image: str = None
    tag: str = None
    includes: Sequence[str] = []
    excludes: Sequence[str] = []

    def __init__(self, repo: str, image: str, tag: str,
                 includes: Sequence[str], excludes: Sequence[str]):
        super().__init__(WATCHER_NAME)
        self.repo = repo
        self.image = image
        self.tag = tag
        self.includes = includes
        self.excludes = excludes

    def __str__(self) -> str:
        return '%s:%s:%s' % (self.repo, self.image, self.tag)


class DockerRegistryWatcher(Watcher):
    """Implementation of a Watcher that checks for new tags in a Docker
    Registry"""

    auth_token: str = None

    def __init__(self, config: DockerRegistryWatcherConfig):
        super().__init__(config)
        self.auth_token = None

    def _do_watch(self) -> WatchResult:
        logger.debug("Watching docker registry %s" % self.config)
        tags = self._get_all_tags_from_registry()

        for ire in self.config.includes:
            tags = [tag for tag in tags if re.compile(ire).match(tag)]

        for ere in self.config.excludes:
            tags = [tag for tag in tags if not re.compile(ere).match(tag)]

        releases = []
        for tag in tags:
            tag_date = self._get_tag_date(tag)
            releases.append(Release(tag, tag_date))

        # Sort with most recent first
        releases.sort(key=lambda r: r.release_date, reverse=True)

        current_tag = self.config.tag
        current_release = None
        missed_releases = []

        for release in releases:
            logger.debug(" - %s" % release.name)
            if release.name == current_tag:
                logger.debug("Current tag '%s' found" % current_tag)
                current_release = release
                break
            missed_releases.append(release)

        if not current_release:
            logger.warning("Current tag '%s' not found !", current_tag)

        logger.debug('Missed tags : %s', missed_releases)
        return WatchResult(self.config, current_release, missed_releases)

    def _get_all_tags_from_registry(self) -> Sequence[str]:
        api_response = self._call_registry_api_tags_list()

        if api_response.status_code == 401:
            if 'Www-Authenticate' in api_response.headers:
                logger.debug("Auhentication required, requesting a token")
                self.auth_token = self._call_docker_registry_api_auth(
                    api_response.headers['Www-Authenticate'])
                api_response = self._call_registry_api_tags_list()
            else:
                raise Exception("Authentication required" +
                                ", but no authentication method provided !")

        if api_response.status_code == 200:
            content = json.loads(api_response.content.decode('utf-8'))
            return content['tags']
        else:
            raise Exception(
                "Docker registry api call failed, response code %d" %
                api_response.status_code)

    def _call_registry_api_tags_list(self) -> requests.Response:
        docker_repo_url = 'https://%s/v2/%s/tags/list' % (self.config.repo,
                                                          self.config.image)
        headers = {'Content-Type': 'application/json'}

        if self.auth_token:
            headers['Authorization'] = 'Bearer %s' % self.auth_token

        response = requests.get(docker_repo_url, headers=headers)
        return response

    def _call_docker_registry_api_auth(self, authenticate_header: str) -> str:
        parsed_hearder = www_authenticate.parse(authenticate_header)
        realm = parsed_hearder['bearer']['realm']
        auth_params = []

        for key in parsed_hearder['bearer']:
            if key != 'realm':
                auth_params.append('%s=%s' %
                                   (key, parsed_hearder['bearer'][key]))
        auth_url = '%s?%s' % (realm, '&'.join(auth_params))
        headers = {'Content-Type': 'application/json'}
        response = requests.get(auth_url, headers=headers)

        if response.status_code == 200:
            content = json.loads(response.content.decode('utf-8'))
            return content['token']
        else:
            raise WatchError("Authentication failed, response code %d" %
                             response.status_code)

    def _get_tag_date(self, tag: str, authToken: str = None) -> datetime:
        docker_repo_url = 'https://%s/v2/%s/manifests/%s' % (
            self.config.repo, self.config.image, tag)
        headers = {'Content-Type': 'application/json'}

        if self.auth_token:
            headers['Authorization'] = 'Bearer %s' % self.auth_token

        response = requests.get(docker_repo_url, headers=headers)
        if response.status_code == 200:
            content = json.loads(response.content.decode('utf-8'))

            tag_date = None
            for history in content['history']:
                layer_date = dateutil.parser.parse(
                    json.loads(history['v1Compatibility'])['created'])
                if tag_date is None or layer_date > tag_date:
                    tag_date = layer_date

            return tag_date
        else:
            raise WatchError(
                "Docker registry api call failed, response code %d" %
                response.status_code)


class DockerRegistryWatcherType(WatcherType):
    """Class to represent the DockerRegistryWatcher type of Watcher"""

    def __init__(self):
        super().__init__(WATCHER_NAME)

    def parse_config(self,
                     watcher_config: Dict) -> DockerRegistryWatcherConfig:
        repo = watcher_config['repo']
        image = watcher_config['image']

        if repo == "registry-1.docker.io" and "/" not in image:
            image = "library/%s" % image

        tag = str(watcher_config['tag'])
        includes = watcher_config.get('includes', [])
        excludes = watcher_config.get('excludes', [])

        return DockerRegistryWatcherConfig(repo, image, tag, includes,
                                           excludes)

    def create_watcher(self, watcher_config: DockerRegistryWatcherConfig
                       ) -> DockerRegistryWatcher:
        return DockerRegistryWatcher(watcher_config)
