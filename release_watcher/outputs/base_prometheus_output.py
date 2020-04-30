import logging
from datetime import datetime, timezone
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
    release_age_gauge: Gauge = None

    def _outputMetrics(self, results: Sequence[watcher_models.WatchResult]):
        if not self.new_releases_gauge:
            logger.debug("Initializing new_releases_gauge")
            label_names = ['name', 'type']
            self.new_releases_gauge = Gauge(
                '%s_new_releases_total' % self.metrics_namespace,
                'Number of new releases',
                label_names, registry=self.registry)

        if not self.release_age_gauge:
            logger.debug("Initializing release_age_gauge")
            label_names = ['name', 'type']
            self.release_age_gauge = Gauge(
                '%s_release_age_seconds' % self.metrics_namespace,
                'Age of the current release',
                label_names, registry=self.registry)

        for result in results:
            label_values = [
                str(result.config.name),
                result.config.watcher_type_name
            ]
            self.new_releases_gauge.labels(*label_values).set(
                len(result.missed_releases))

            # This most probably won't take into account timezones
            # But it will most probably be used as converted as days,
            # so a few hours shouldn't matter
            if result.current_release:
                release_date = result.current_release.release_date
                if release_date.tzinfo:
                    now = datetime.now(timezone.utc)
                else:
                    now = datetime.now()
                release_age = (now - release_date).total_seconds()
            else:
                release_age = float("inf")

            self.release_age_gauge.labels(*label_values).set(release_age)
