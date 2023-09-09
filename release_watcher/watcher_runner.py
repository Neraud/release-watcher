import logging
from typing import Sequence
from concurrent.futures import ThreadPoolExecutor

from release_watcher.config_models import GlobalConfig
from release_watcher.watchers.watcher_manager import Watcher
from release_watcher.watchers.watcher_models import WatchResult

logger = logging.getLogger(__name__)


class WatcherRunner:
    """Class that runs the configured watchers"""

    config: GlobalConfig = None
    watchers: Sequence[Watcher] = []

    def __init__(self, config: GlobalConfig, watchers: Sequence[Watcher]):
        self.config = config
        self.watchers = watchers

    def run(self) -> Sequence[WatchResult]:
        """Runs the configured watchers and returns the list of results

        Watchers are run sequentially"""
        threads = self.config.core.threads
        logger.info('Running all watchers with %d threads', threads)

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [
                executor.submit(watcher.watch) for watcher in self.watchers
            ]

        results = list(filter(lambda r: r, map(lambda f: f.result(), futures)))

        return results
