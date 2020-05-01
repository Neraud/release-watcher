import logging
from typing import Dict, Sequence
from prometheus_client import CollectorRegistry, write_to_textfile
from release_watcher.outputs.base_prometheus_output import BasePrometheusOutput
from release_watcher.outputs.output_manager \
    import OutputConfig, OutputType
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


class PrometheusFileOutput(BasePrometheusOutput):
    """Implementation of an Output that exposes Prometheus metrics"""

    def __init__(self, config: PrometheusFileOutputConfig):
        super().__init__(config)

    def outputs(self, results: Sequence[watcher_models.WatchResult]):
        logger.debug("Writing results to %s " % self.config.path)
        self._outputMetrics(results)
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
