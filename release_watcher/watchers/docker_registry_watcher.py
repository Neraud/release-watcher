import logging
import json
from typing import Dict, Sequence
import re
import datetime
import requests
import www_authenticate
import dateutil.parser
from release_watcher.config_models import CommonConfig
from release_watcher.watchers.watcher_models import Release, WatchError, WatchResult
from release_watcher.watchers.watcher_manager import Watcher, WatcherConfig, WatcherType

logger = logging.getLogger(__name__)

WATCHER_TYPE_NAME = 'docker_registry'


class DockerRegistryWatcherConfig(WatcherConfig):
    """Class to store the configuration for a DockerRegistryWatcher"""

    repo: str = None
    image: str = None
    tag: str = None
    includes: Sequence[str] = []
    excludes: Sequence[str] = []
    timeout: float

    def __init__(self, name: str, repo: str, image: str, tag: str,
                 includes: Sequence[str], excludes: Sequence[str], timeout: float):
        super().__init__(WATCHER_TYPE_NAME, name)
        self.repo = repo
        self.image = image
        self.tag = tag
        self.includes = includes
        self.excludes = excludes
        self.timeout = timeout

    def __str__(self) -> str:
        return f'{self.repo}:{self.image}:{self.tag}'


class DockerRegistryWatcher(Watcher):
    """Implementation of a Watcher that checks for new tags in a Docker
    Registry"""

    auth_token: str = None

    def __init__(self, config: DockerRegistryWatcherConfig):
        super().__init__(config)
        self.auth_token = None

    def _do_watch(self) -> WatchResult:
        logger.debug('Watching docker registry %s', self.config)
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
            logger.debug(' - %s', release.name)
            if release.name == current_tag:
                logger.debug('Current tag %s found', current_tag)
                current_release = release
                break
            missed_releases.append(release)

        if not current_release:
            logger.warning('Current tag %s not found !', current_tag)

        logger.debug('Missed tags : %s', missed_releases)
        return WatchResult(self.config, current_release, missed_releases)

    def _get_all_tags_from_registry(self, page_url=None) -> Sequence[str]:
        api_response = self._call_registry_api_tags_list(page_url)

        if api_response.status_code == 401:
            if 'Www-Authenticate' in api_response.headers:
                logger.debug('Auhentication required, requesting a token')
                self.auth_token = self._call_docker_registry_api_auth(
                    api_response.headers['Www-Authenticate'])
                api_response = self._call_registry_api_tags_list(page_url)
            else:
                raise Exception('Authentication required, but no authentication method provided !')

        if api_response.status_code == 200:
            content = json.loads(api_response.content.decode('utf-8'))
            tags = content['tags']
            if 'next' in api_response.links:
                next_url = api_response.links['next']['url']
                next_tags = self._get_all_tags_from_registry(next_url)
                tags += next_tags
            return tags

        raise Exception(
            f'Docker registry api call failed, response code {api_response.status_code}')

    def _call_registry_api_tags_list(self, page_url=None) -> requests.Response:
        if page_url:
            docker_repo_url = f'https://{self.config.repo}{page_url}'
        else:
            docker_repo_url = f'https://{self.config.repo}/v2/{self.config.image}/tags/list'
        headers = {'Content-Type': 'application/json'}

        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'

        response = requests.get(docker_repo_url, headers=headers, timeout=self.config.timeout)
        return response

    def _call_docker_registry_api_auth(self, authenticate_header: str) -> str:
        parsed_hearder = www_authenticate.parse(authenticate_header)
        realm = parsed_hearder['bearer']['realm']
        auth_params = []

        for key in parsed_hearder['bearer']:
            if key != 'realm':
                auth_params.append('%s=%s' %
                                   (key, parsed_hearder['bearer'][key]))
        auth_url = f'{realm}?{"&".join(auth_params)}'
        headers = {'Content-Type': 'application/json'}
        response = requests.get(auth_url, headers=headers, timeout=self.config.timeout)

        if response.status_code == 200:
            content = json.loads(response.content.decode('utf-8'))
            return content['token']

        raise WatchError(f'Authentication failed, response code {response.status_code}')

    def _get_tag_date(self, tag: str) -> datetime:
        docker_repo_url = f'https://{self.config.repo}/v2/{self.config.image}/manifests/{tag}'
        headers = {
            'Accept': ','.join([
                'application/vnd.docker.distribution.manifest.v2+json',
                'application/vnd.oci.image.index.v1+json',
                'application/vnd.oci.image.manifest.v1+json',
            ])
        }

        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'

        response = requests.get(docker_repo_url, headers=headers, timeout=self.config.timeout)
        if response.status_code == 200:
            content = json.loads(response.content.decode('utf-8'))
            tag_date = None

            if 'manifests' in content:
                for manifest in content['manifests']:
                    m_date = self._get_date_from_manifest(manifest['digest'])
                    if m_date is None:
                        continue

                    if tag_date is None or m_date > tag_date:
                        tag_date = m_date
            else:
                tag_date = self._get_tag_date_from_config(
                    content['config']['digest'])

            return tag_date

        logger.debug('Docker registry api call failed, response code %d', response.status_code)
        logger.debug('headers : %s', response.headers)
        logger.debug('content: %s', response.content)
        raise WatchError(f'Docker registry api call failed, response code {response.status_code}')

    def _get_date_from_manifest(self, digest: str) -> datetime:
        api_url = f'https://{self.config.repo}/v2/{self.config.image}/manifests/{digest}'
        headers = {
            'Accept': ','.join([
                'application/vnd.docker.distribution.manifest.v2+json',
                'application/vnd.oci.image.manifest.v1+json',
            ])
        }

        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'

        response = requests.get(api_url, headers=headers, timeout=self.config.timeout)
        if response.status_code == 200:
            content = json.loads(response.content.decode('utf-8'))
            return self._get_tag_date_from_config(content['config']['digest'])

        logger.debug('Docker registry api call failed, response code %d', response.status_code)
        logger.debug('headers : %s', response.headers)
        logger.debug('content: %s', response.content)
        raise WatchError(f'Docker registry api call failed, response code {response.status_code}')

    def _get_tag_date_from_config(self, digest: str) -> datetime:
        api_url = f'https://{self.config.repo}/v2/{self.config.image}/blobs/{digest}'
        headers = {
            'Accept': ','.join([
                'application/vnd.docker.distribution.manifest.v2+json',
                'application/vnd.oci.image.manifest.v1+json',
            ])
        }

        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'

        response = requests.get(api_url, headers=headers, timeout=self.config.timeout)
        if response.status_code == 200:
            content = json.loads(response.content.decode('utf-8'))
            if 'created' in content:
                return dateutil.parser.parse(content['created'])
            else:
                return None

        logger.debug('Docker registry api call failed, response code %d', response.status_code)
        logger.debug('headers : %s', response.headers)
        logger.debug('content: %s', response.content)
        raise WatchError(f'Docker registry api call failed, response code {response.status_code}')


class DockerRegistryWatcherType(WatcherType):
    """Class to represent the DockerRegistryWatcher type of Watcher"""

    def __init__(self):
        super().__init__(WATCHER_TYPE_NAME)

    def parse_config(self, common_config: CommonConfig,
                     watcher_config: Dict) -> DockerRegistryWatcherConfig:
        repo = watcher_config['repo']
        image = watcher_config['image']

        if repo == 'registry-1.docker.io' and '/' not in image:
            image = f'library/{image}'

        tag = str(watcher_config['tag'])
        includes = watcher_config.get('includes', [])
        excludes = watcher_config.get('excludes', [])
        name = watcher_config.get('name', f'{repo}:{image}')
        timeout = watcher_config.get('timeout', common_config.docker.timeout)

        return DockerRegistryWatcherConfig(name, repo, image, tag, includes, excludes, timeout)

    def create_watcher(self, watcher_config: DockerRegistryWatcherConfig) -> DockerRegistryWatcher:
        return DockerRegistryWatcher(watcher_config)
