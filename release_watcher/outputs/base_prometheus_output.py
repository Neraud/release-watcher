import logging
from typing import Sequence
from prometheus_client import CollectorRegistry, Gauge
from release_watcher.outputs.output_manager import Output
from release_watcher.watchers import watcher_models

logger = logging.getLogger(__name__)


class BasePrometheusOutput(Output):
    """Base Output that exposes Prometheus metrics"""

    metrics_namespace = "releasewatcher"
    registry: CollectorRegistry = None
    new_releases_gauge: Gauge = None

    def _outputMetrics(self, results: Sequence[watcher_models.WatchResult]):
        if not self.new_releases_gauge:
            logger.debug("Initializing new_releases_gauge")
            label_names = ['name', 'type']
            self.new_releases_gauge = Gauge(
                '%s_new_releases_total' % self.metrics_namespace,
                'Number of new releases',
                label_names, registry=self.registry)

        for result in results:
            label_values = [
                str(result.config.name),
                result.config.watcher_type_name
            ]
            self.new_releases_gauge.labels(*label_values).set(
                len(result.missed_releases))
