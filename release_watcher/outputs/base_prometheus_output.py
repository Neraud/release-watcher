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
            label_names = ['name', 'type']
            self.missed_releases_gauge = Gauge(
                'missed_releases', 'Number of missed releases',
                label_names, registry=self.registry)

        for result in results:
            label_values = [
                str(result.config.name),
                result.config.watcher_type_name
            ]
            self.missed_releases_gauge.labels(*label_values).set(
                len(result.missed_releases))
