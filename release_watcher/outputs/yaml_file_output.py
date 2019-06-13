import logging
import yaml
from typing import Dict, Sequence
from release_watcher.outputs.output_manager \
    import Output, OutputConfig, OutputType
from release_watcher.watchers import watcher_models

logger = logging.getLogger(__name__)

OUTPUT_NAME = 'yaml_file'


class YamlFileOutputConfig(OutputConfig):
    """Class to store the configuration for a YamlFileOutput"""

    path: str = None
    display_up_to_date: bool = True

    def __init__(self, path: str, display_up_to_date: bool):
        super().__init__(OUTPUT_NAME)
        self.path = path
        self.display_up_to_date = display_up_to_date

    def __str__(self) -> str:
        return '%s(%s)' % (self.path, self.display_up_to_date)

    def __repr__(self) -> str:
        return 'YamlFileOutputConfig(%s)' % self


class YamlFileOutput(Output):
    """Implementation of an Output that writes to a YAML file"""

    def __init__(self, config: YamlFileOutputConfig):
        super().__init__(config)

    def outputs(self, results: Sequence[watcher_models.WatchResult]):
        logger.debug("Writing results as to %s " % self.config.path)

        yaml_dict = {'results': []}
        for result in results:
            if not self.config.display_up_to_date and \
                    not result.missed_releases:
                continue

            result_dict = {}
            result_dict['type'] = result.config.name
            result_dict['friendlyName'] = str(result.config)
            if result.current_release:
                result_dict['currentReleaseDate'] = \
                    result.current_release.release_date

            result_dict['missedReleaseCount'] = len(result.missed_releases)
            result_dict['missedReleases'] = []

            for missed_release in result.missed_releases:
                mr_dict = {}
                mr_dict['name'] = missed_release.name
                mr_dict['date'] = str(missed_release.release_date)
                result_dict['missedReleases'].append(mr_dict)

            if result.most_recent_release:
                result_dict['newestRelease'] = {
                    'name': result.most_recent_release.name,
                    'date': str(result.most_recent_release.release_date)
                }

            yaml_dict['results'].append(result_dict)

        with open(self.config.path, mode='w') as result_file:
            yaml.dump(yaml_dict, result_file, default_flow_style=False)


class YamlFileOutputType(OutputType):
    """Class to represent the YamlFileOutput type of Output"""

    def __init__(self):
        super().__init__(OUTPUT_NAME)

    def parse_config(self, global_conf: Dict,
                     source_config: Dict) -> YamlFileOutputConfig:
        path = source_config['path']

        if not path.startswith("/"):
            path = global_conf['configFileDir'] + "/" + path

        display_up_to_date = source_config.get("displayUpToDate", True)

        return YamlFileOutputConfig(path, display_up_to_date)

    def create_output(self, config: OutputConfig) -> YamlFileOutput:
        return YamlFileOutput(config)
