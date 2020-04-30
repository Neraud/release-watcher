import logging
from typing import Sequence
from prometheus_client import CollectorRegistry, Gauge
from release_watcher.outputs.output_manager import Output
from release_watcher.watchers import watcher_models

logger = logging.getLogger(__name__)


class BasePrometheusOutput(Output):
    """Base Output that exposes Prometheus metrics"""

    missed_releases_gauge: Gauge = None
    registry: CollectorRegistry = None

    def _outputMetrics(self, results: Sequence[watcher_models.WatchResult]):
        if not self.missed_releases_gauge:
            logger.debug("Initializing missed_releases_gauge")
            self.missed_releases_gauge = Gauge('missed_releases',
                                               'Number of missed releases',
                                               ['name'],
                                               registry=self.registry)
        for result in results:
            self.missed_releases_gauge.labels(str(result.config.name)).set(
                len(result.missed_releases))
