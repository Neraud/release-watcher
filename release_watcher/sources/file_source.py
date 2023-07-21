import logging
from typing import Dict, Sequence
import glob
from release_watcher.config_models import CommonConfig
from release_watcher.sources.source_manager import SourceConfig, SourceType
from release_watcher.sources.base_yaml_source_loader \
    import BaseYamlSourceLoader
from release_watcher.watchers import watcher_manager

logger = logging.getLogger(__name__)

SOURCE_NAME = 'file'


class FileSourceConfig(SourceConfig):
    """Class to store the configuration for a FileSource"""

    path: str = None

    def __init__(self, path: str):
        super().__init__(SOURCE_NAME)
        self.path = path

    def __str__(self) -> str:
        return '%s' % self.path


class FileSource(BaseYamlSourceLoader):
    """Implementation of an Source that reads from a YAML file"""

    def __init__(self, common_config: CommonConfig, config: FileSourceConfig):
        super().__init__(common_config, config)

    def read_watchers(self) -> Sequence[watcher_manager.WatcherConfig]:
        logger.debug("Reading watchers from file %s", self.config.path)
        
        watcher_configs = []
        for path in glob.glob(self.config.path):
            logger.debug(" - %s", path)
            watcher_configs.extend(self.parse_from_file(path))
    
        return watcher_configs


class FileSourceType(SourceType):
    """Class to represent the FileSource type of Source"""

    def __init__(self):
        super().__init__(SOURCE_NAME)

    def parse_config(self, global_conf: Dict,
                     source_config: Dict) -> FileSourceConfig:
        path = source_config['path']

        if not path.startswith("/"):
            path = global_conf['configFileDir'] + "/" + path

        return FileSourceConfig(path)

    def create_source(self, common_config: CommonConfig,
                      config: FileSourceConfig) -> FileSource:
        return FileSource(common_config, config)
