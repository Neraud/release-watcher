import click
import logging
import sys
import time
from release_watcher import config_loader
from release_watcher.watcher_runner import WatcherRunner
from release_watcher.sources import source_manager
from release_watcher.watchers import watcher_manager
from release_watcher.watchers.watcher_models import WatchResult
from release_watcher.outputs import output_manager
from release_watcher.config_models import GlobalConfig
from typing import Dict, Sequence
logger = logging.getLogger(__name__)


@click.command()
@click.option('--config', default='config.yaml', help='Config file')
def main(config: str):
    """Entrypoint for the Release Watch application"""

    global_config = config_loader.load_conf(config)
    watchers = _create_watchers(global_config.sources)

    if not watchers:
        logger.error("No configured watchers, nothing to do")
        sys.exit()

    watcher_runner = WatcherRunner(watchers)

    if global_config.core.run_mode == 'once':
        _run_once(global_config, watcher_runner)
    else:
        while True:
            _run_once(global_config, watcher_runner)
            logger.debug('Sleeping %d seconds ...' %
                         global_config.core.sleep_duration)
            time.sleep(global_config.core.sleep_duration)


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


def _run_once(global_config: GlobalConfig, watcher_runner: WatcherRunner):
    results = watcher_runner.run()
    _generate_outputs(global_config.outputs, results)


def _generate_outputs(outputs_conf: output_manager.OutputConfig,
                      results: Sequence[WatchResult]):
    logger.info('Generating outputs')
    for output_conf in outputs_conf:
        output = output_manager.get_output_type(
            output_conf.name).create_output(output_conf)
        logger.info(' - output : %s', output)
        output.outputs(results)
