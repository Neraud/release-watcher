import logging
from abc import ABCMeta, abstractmethod
from typing import Dict, Sequence
from release_watcher.base_models import OutputConfig
from release_watcher.watchers import watcher_models

logger = logging.getLogger(__name__)

OUTPUT_TYPES = {}


class Output(metaclass=ABCMeta):
    """Base class to implement an Output"""

    config: OutputConfig = None

    def __init__(self, config: OutputConfig):
        self.config = config

    @abstractmethod
    def outputs(self, results: Sequence[watcher_models.WatchResult]):
        """Writes the results to the output"""

    def __repr__(self):
        return f'{self.__class__.__name__}({self.config})'


class OutputType(metaclass=ABCMeta):
    """Class to represent a type of Output

    It's used both to generate the OutputConfig for an Output,
    and as a factory to create the Output instance.
    """

    name: str = None

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def parse_config(self, global_conf: Dict,
                     source_config: Dict) -> OutputConfig:
        """Parses the raw configuration from the user and returns an
        OutputConfig instance"""
        return

    @abstractmethod
    def create_output(self, config: OutputConfig) -> Output:
        """Creates the Output instance from a configuation"""


def register_output_type(output_type: OutputType):
    """Regiters an OutputType to enable using it by name later"""

    logger.info('Registering output type : %s', output_type.name)
    OUTPUT_TYPES[output_type.name] = output_type


def get_output_type(name: str) -> OutputType:
    """Fetches a previously registered OutputType by name"""

    if name in OUTPUT_TYPES:
        return OUTPUT_TYPES[name]

    raise ValueError(f'The output type {name} is unknown')
