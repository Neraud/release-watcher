
import abc


class OutputConfig(metaclass=abc.ABCMeta):
    """Base class to store the configuration for an Output"""

    name: str = None

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self)


class SourceConfig(metaclass=abc.ABCMeta):
    """Base class to store the configuration for a Source"""

    name: str = None

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self)


class WatcherConfig(metaclass=abc.ABCMeta):
    """Base class to store the configuration for a Watcher"""

    watcher_type_name: str = None
    name: str = None

    def __init__(self, watcher_type_name: str, name: str):
        self.watcher_type_name = watcher_type_name
        self.name = name

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self)
