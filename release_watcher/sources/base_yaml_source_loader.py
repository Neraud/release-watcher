import logging
from abc import ABCMeta
from typing import Dict, Sequence
from yaml import load
from release_watcher.watchers import watcher_manager
from release_watcher.sources.source_manager import Source

logger = logging.getLogger(__name__)

try:
    from yaml import CLoader as Loader  # pylint: disable=ungrouped-imports
except ImportError:
    from yaml import Loader


class BaseYamlSourceLoader(Source, metaclass=ABCMeta):
    """Base Source class that reads Watcher configuration from a YAML file
    or content.

    It's used for both the FileSource and InlineSource implementation"""

    def parse_from_file(self, file: str) -> Sequence[watcher_manager.WatcherConfig]:
        """Reads data from a YAML file"""

        with open(file, 'r', encoding='UTF-8') as ymlfile:
            content = load(ymlfile, Loader=Loader)

        return self.parse_from_content(content)

    def parse_from_content(self, conf: Dict) -> Sequence[watcher_manager.WatcherConfig]:
        """Reads data from a YAML string"""

        parsed_sources_conf = []

        if 'watchers' in conf and isinstance(conf['watchers'], list):
            for watcher_conf in conf['watchers']:
                try:
                    parsed_source_conf = self._parse_one_watcher_conf(watcher_conf)
                    parsed_sources_conf.append(parsed_source_conf)
                except Exception as e:
                    logger.exception('Error configuring a watcher : %s', e)

        return parsed_sources_conf

    def _parse_one_watcher_conf(self, watcher_conf: Dict) -> watcher_manager.WatcherConfig:
        logger.debug(' - %s', watcher_conf)

        if 'type' in watcher_conf:
            watcher_type = watcher_manager.get_watcher_type(watcher_conf['type'])
            return watcher_type.parse_config(self.common_config, watcher_conf)

        raise ValueError('Missing type property on wather configuration')
