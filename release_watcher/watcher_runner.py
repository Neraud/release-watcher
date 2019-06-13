import logging
from typing import Sequence

from release_watcher.watchers.watcher_manager import Watcher
from release_watcher.watchers.watcher_models import WatchResult

logger = logging.getLogger(__name__)


class WatcherRunner:
    """Class that runs the configured watchers"""

    watchers: Sequence[Watcher] = []

    def __init__(self, watchers: Sequence[Watcher]):
        self.watchers = watchers

    def run(self) -> Sequence[WatchResult]:
        """Runs the configured watchers and returns the list of results

        Watchers are run sequentially"""

        logger.info("Running all watchers")
        results = []

        for watcher in self.watchers:
            logger.info(" - running %s", watcher)
            result = watcher.watch()
            if result:
                results.append(result)

        return results
