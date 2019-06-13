import click
import logging
import sys
from release_watcher import config_loader
from release_watcher.watcher_runner import WatcherRunner
from release_watcher.sources import source_manager
from release_watcher.watchers import watcher_manager
from release_watcher.watchers.watcher_models import WatchResult
from release_watcher.outputs import output_manager
from typing import Dict, Sequence
logger = logging.getLogger(__name__)


@click.command()
@click.option('--config', default='config.yaml', help='Config file')
def main(config: str):
    """Entrypoint for the Release Watch application"""

    conf = config_loader.load_conf(config)
    watchers = _create_watchers(conf.sources)

    if not watchers:
        logger.error("No configured watchers, nothing to do")
        sys.exit()

    watcher_runner = WatcherRunner(watchers)
    results = watcher_runner.run()
    _generate_outputs(conf.outputs, results)


def _create_watchers(sources_conf: Sequence[Dict]
                     ) -> Sequence[watcher_manager.Watcher]:
    logger.debug('Listing watchers from sources')
    watchers = []
    for source_conf in sources_conf:
        logger.debug(' - Source : %s', source_conf.name)
        source_type = source_manager.get_source_type(source_conf.name)
        watchers_for_source = source_type.create_source(
            source_conf).read_watchers()
        logger.debug(' -> %d watchers for %s', len(watchers_for_source),
                     source_conf.name)
        for watcher_config in watchers_for_source:
            watcher_type = watcher_manager.get_watcher_type(
                watcher_config.name)
            watcher = watcher_type.create_watcher(watcher_config)
            watchers.append(watcher)
    return watchers


def _generate_outputs(outputs_conf: output_manager.OutputConfig,
                      results: Sequence[WatchResult]):
    logger.info('Generating outputs')
    for output_conf in outputs_conf:
        output = output_manager.get_output_type(
            output_conf.name).create_output(output_conf)
        logger.info(' - output : %s', output)
        output.outputs(results)
