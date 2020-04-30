from typing import Sequence
from release_watcher.base_models import SourceConfig, OutputConfig


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


class GithubConfig:
    """Model representing the github configuration"""

    username: str = None
    password: str = None
    rate_limit_wait_max: int = None


class CommonConfig:
    """Model representing common watchers configuration"""

    github: GithubConfig = None


class GlobalConfig:
    """Model representing the main configuration"""

    core: CoreConfig = None
    common: CommonConfig = None
    sources: Sequence[SourceConfig] = []
    outputs: Sequence[OutputConfig] = []

    def __init__(self):
        pass
