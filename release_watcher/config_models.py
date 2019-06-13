from typing import Sequence
from release_watcher.sources import source_manager
from release_watcher.outputs import output_manager


class LoggerConfig:
    """Model representing the logger configuration"""

    type: str = None
    level: str = None
    path: str = None

    def __init__(self, type, level, path=None):
        self.type = type
        self.level = level
        self.path = path


class GlobalConfig:
    """Model representing the main configuration"""

    sources: Sequence[source_manager.SourceConfig] = []
    outputs: Sequence[output_manager.OutputConfig] = []

    def __init__(self):
        pass
