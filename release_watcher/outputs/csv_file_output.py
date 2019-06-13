import logging
import csv
from typing import Dict, Sequence
from release_watcher.outputs.output_manager \
    import Output, OutputConfig, OutputType
from release_watcher.watchers import watcher_models

logger = logging.getLogger(__name__)

OUTPUT_NAME = 'csv_file'


class CsvFileOutputConfig(OutputConfig):
    """Class to store the configuration for a CsvFileOutput"""

    path: str = None
    display_up_to_date: bool = True
    display_header: bool = True

    def __init__(self, path: str, display_up_to_date: bool,
                 display_header: bool):
        super().__init__(OUTPUT_NAME)
        self.path = path
        self.display_up_to_date = display_up_to_date
        self.display_header = display_header

    def __str__(self) -> str:
        return '%s(%s,%s)' % (self.path, self.display_up_to_date,
                              self.display_header)

    def __repr__(self) -> str:
        return 'CsvFileOutputConfig(%s)' % self


class CsvFileOutput(Output):
    """Implementation of an Output that writes to a CSV file"""

    def __init__(self, config: CsvFileOutputConfig):
        super().__init__(config)

    def outputs(self, results: Sequence[watcher_models.WatchResult]):
        logger.debug("Writing results to %s " % self.config.path)

        with open(self.config.path, mode='w') as result_file:
            csv_writer = csv.writer(result_file,
                                    delimiter=',',
                                    quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)

            if self.config.display_header:
                csv_writer.writerow([
                    'Type', 'Friendly name', 'Current release date',
                    'Missed releases', 'Newest release', 'Newest release date'
                ])

            for result in results:
                if not self.config.display_up_to_date and \
                        not result.missed_releases:
                    continue
                row = self._prepare_one_csv_row(result)
                csv_writer.writerow(row)

    def _prepare_one_csv_row(self,
                             result: Sequence[watcher_models.WatchResult]):
        if result.current_release:
            current_r_date = result.current_release.release_date
        else:
            current_r_date = ""

        if result.most_recent_release:
            most_recent_r_name = result.most_recent_release.name
            most_recent_r_date = result.most_recent_release.release_date
        else:
            most_recent_r_name = ""
            most_recent_r_date = ""

        return [
            result.config.name,
            str(result.config), current_r_date,
            len(result.missed_releases), most_recent_r_name, most_recent_r_date
        ]


class CsvFileOutputType(OutputType):
    """Class to represent the CsvFileOutput type of Output"""

    def __init__(self):
        super().__init__(OUTPUT_NAME)

    def parse_config(self, global_conf: Dict,
                     source_config: Dict) -> CsvFileOutputConfig:
        path = source_config['path']

        if not path.startswith("/"):
            path = global_conf['configFileDir'] + "/" + path

        display_up_to_date = source_config.get("displayUpToDate", True)
        display_header = source_config.get("displayHeader", True)

        return CsvFileOutputConfig(path, display_up_to_date, display_header)

    def create_output(self, config: OutputConfig) -> CsvFileOutput:
        return CsvFileOutput(config)
