import logging
from typing import Dict, Sequence
from release_watcher.sources.source_manager import SourceConfig, SourceType
from release_watcher.sources.base_yaml_source_loader \
    import BaseYamlSourceLoader
from release_watcher.watchers import watcher_manager

logger = logging.getLogger(__name__)

SOURCE_NAME = 'inline'


class InlineSourceConfig(SourceConfig):
    """Class to store the configuration for a InlineSource"""

    inline_conf: str = None

    def __init__(self, inline_conf: str):
        super().__init__(SOURCE_NAME)
        self.inline_conf = inline_conf

    def __str__(self) -> str:
        return ''


class InlineSource(BaseYamlSourceLoader):
    """Implementation of an Source that reads from the main configuration
    file"""

    def __init__(self, config: InlineSourceConfig):
        super().__init__(config)

    def read_watchers(self) -> Sequence[watcher_manager.WatcherConfig]:
        logger.debug("Reading inline watchers")
        return self.parse_from_content(self.config.inline_conf)


class InlineSourceType(SourceType):
    """Class to represent the InlineSource type of Source"""

    def __init__(self):
        super().__init__(SOURCE_NAME)

    def parse_config(self, global_conf: Dict,
                     source_config: Dict) -> InlineSourceConfig:
        return InlineSourceConfig(source_config)

    def create_source(self, config: InlineSourceConfig) -> InlineSource:
        return InlineSource(config)
