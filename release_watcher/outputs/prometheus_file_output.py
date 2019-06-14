import logging
from typing import Dict, Sequence
from prometheus_client import CollectorRegistry, Gauge, write_to_textfile
from release_watcher.outputs.output_manager \
    import Output, OutputConfig, OutputType
from release_watcher.watchers import watcher_models

logger = logging.getLogger(__name__)

OUTPUT_NAME = 'prometheus_file'


class PrometheusFileOutputConfig(OutputConfig):
    """Class to store the configuration for a PrometheusFileOutput"""

    path: str = None

    def __init__(self, path: str):
        super().__init__(OUTPUT_NAME)
        self.path = path

    def __str__(self) -> str:
        return '%s' % self.path

    def __repr__(self) -> str:
        return 'PrometheusFileOutputConfig(%s)' % self


class PrometheusFileOutput(Output):
    """Implementation of an Output that exposes Prometheus metrics"""

    registry: CollectorRegistry = None
    missed_releases_gauge: Gauge = None

    def __init__(self, config: PrometheusFileOutputConfig):
        super().__init__(config)

    def outputs(self, results: Sequence[watcher_models.WatchResult]):
        logger.debug("Writing results to %s " % self.config.path)

        if not self.registry:
            logger.debug("Initializing registry")
            self.registry = CollectorRegistry()

        if not self.missed_releases_gauge:
            logger.debug("Initializing missed_releases_gauge")
            self.missed_releases_gauge = Gauge('missed_releases',
                                               'Number of missed releases',
                                               ['name'],
                                               registry=self.registry)

        for result in results:
            self.missed_releases_gauge.labels(str(result.config)).set(
                len(result.missed_releases))

        write_to_textfile(self.config.path, self.registry)


class PrometheusFileOutputType(OutputType):
    """Class to represent the PrometheusFileOutput type of Output"""

    def __init__(self):
        super().__init__(OUTPUT_NAME)

    def parse_config(self, global_conf: Dict,
                     source_config: Dict) -> PrometheusFileOutputConfig:
        path = source_config['path']

        if not path.startswith("/"):
            path = global_conf['configFileDir'] + "/" + path

        return PrometheusFileOutputConfig(path)

    def create_output(self, config: OutputConfig) -> PrometheusFileOutput:
        return PrometheusFileOutput(config)
