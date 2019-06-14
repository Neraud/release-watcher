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


class CoreConfig:
    """Model representing the core configuration"""

    threads: int = None
    run_mode: str = None
    sleep_duration: int = None

    def __init__(self, threads: int, run_mode: str,
                 sleep_duration: int = None):
        self.threads = threads
        self.run_mode = run_mode
        self.sleep_duration = sleep_duration


class GlobalConfig:
    """Model representing the main configuration"""

    core: CoreConfig = None
    sources: Sequence[source_manager.SourceConfig] = []
    outputs: Sequence[output_manager.OutputConfig] = []

    def __init__(self):
        pass
