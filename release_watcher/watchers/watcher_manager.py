import logging
from abc import ABCMeta, abstractmethod
import time
from typing import Dict
from release_watcher.base_models import WatcherConfig
from release_watcher.config_models import CommonConfig
from release_watcher.watchers.watcher_models import WatchResult

logger = logging.getLogger(__name__)

WATCHER_TYPES = {}


class Watcher(metaclass=ABCMeta):
    """Base class to implement a Watcher"""

    config: WatcherConfig = None

    def __init__(self, config: WatcherConfig):
        self.config = config

    def watch(self) -> WatchResult:
        """Runs the watch logic to look for new releases"""

        logger.info(' - running %s', self)
        result = None
        try:
            start_time = time.time()
            result = self._do_watch()
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            logger.info(' = Finished running %s in %d ms (%d missed releases found)',
                        self, duration_ms, len(result.missed_releases))
        except Exception as e:
            logger.exception('Error running %s : %s', self, e)

        return result

    @abstractmethod
    def _do_watch(self) -> WatchResult:
        pass

    def __repr__(self):
        return f'{self.__class__.__name__}({self.config})'


class WatcherType(metaclass=ABCMeta):
    """Class to represent a type of Watcher

    It's used both to generate the WatcherConfig for a Watcher,
    and as a factory to create the Watcher instance.
    """

    name: str = None

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def parse_config(self, common_config: CommonConfig, watcher_config: Dict) -> WatcherConfig:
        """Parses the raw configuration from the user and returns a WatcherConfig instance"""

    @abstractmethod
    def create_watcher(self, watcher_config: WatcherConfig) -> Watcher:
        """Creates the Watcher instance from a configuation"""


def register_watcher_type(watcher_type: WatcherType):
    """Regiters an WatcherType to enable using it by name later"""

    logger.info("Registering watcher type : %s", watcher_type.name)
    WATCHER_TYPES[watcher_type.name] = watcher_type


def get_watcher_type(name: str) -> WatcherType:
    """Fetches a previously registered WatcherType by name"""

    if name in WATCHER_TYPES:
        return WATCHER_TYPES[name]

    raise ValueError(f'The watcher type {name} is unknown')
