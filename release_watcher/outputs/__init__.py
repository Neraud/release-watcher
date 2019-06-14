from release_watcher.outputs.output_manager import register_output_type
from release_watcher.outputs.csv_file_output import CsvFileOutputType
from release_watcher.outputs.yaml_file_output import YamlFileOutputType
from release_watcher.outputs.prometheus_file_output \
    import PrometheusFileOutputType
from release_watcher.outputs.prometheus_http_output \
    import PrometheusHttpOutputType

register_output_type(CsvFileOutputType())
register_output_type(YamlFileOutputType())
register_output_type(PrometheusFileOutputType())
register_output_type(PrometheusHttpOutputType())
