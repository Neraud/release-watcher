import logging
import abc
from typing import Dict, Sequence
from release_watcher.base_models import SourceConfig
from release_watcher.config_models import CommonConfig
from release_watcher.watchers.watcher_manager import WatcherConfig

logger = logging.getLogger(__name__)

SOURCE_TYPES = {}


class Source(metaclass=abc.ABCMeta):
    """Base class to implement a Source"""

    config: SourceConfig = None
    common_config: CommonConfig = None

    def __init__(self, common_config: CommonConfig, config: SourceConfig):
        self.common_config = common_config
        self.config = config

    @abc.abstractmethod
    def read_watchers(self, common_config: CommonConfig) \
            -> Sequence[WatcherConfig]:
        """Reads the watchers list from the source"""
        pass

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.config)


class SourceType(metaclass=abc.ABCMeta):
    """Class to represent a type of Source

    It's used both to generate the SourceConfig for a Source,
    and as a factory to create the Source instance.
    """

    name: str = None

    def __init__(self, name: str):
        self.name = name

    @abc.abstractmethod
    def parse_config(self, source_config: Dict) -> SourceConfig:
        """Parses the raw configuration from the user and returns a
        SourceConfig instance"""
        pass

    @abc.abstractmethod
    def create_source(self, common_config: CommonConfig,
                      config: SourceConfig) -> Source:
        """Creates the Source instance from a configuation"""
        pass


def register_source_type(source_type: SourceType):
    """Regiters an SourceType to enable using it by name later"""

    logger.info("Registering source type : %s", source_type.name)
    SOURCE_TYPES[source_type.name] = source_type


def get_source_type(name: str) -> SourceType:
    """Fetches a previously registered SourceType by name"""

    if name in SOURCE_TYPES:
        return SOURCE_TYPES[name]
    else:
        raise ValueError('The source type %s is unknown' % name)
