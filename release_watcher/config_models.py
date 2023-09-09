from typing import Sequence
from release_watcher.base_models import SourceConfig, OutputConfig


class ConfigException(Exception):
    """Exception raised when a something is wrong with the configuration"""
    message: str = None

    def __init__(self, message: str):
        self.message = message


class LoggerConfig:
    """Model representing the logger configuration"""

    logger_type: str = None
    level: str = None
    path: str = None

    def __init__(self, logger_type: str, level: str, path: str = None):
        self.logger_type = logger_type
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
