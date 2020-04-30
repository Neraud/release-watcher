import click
import logging
import sys
import time
from release_watcher import config_loader
from release_watcher.config_models import GlobalConfig
from release_watcher.watcher_runner import WatcherRunner
from release_watcher.sources import source_manager
from release_watcher.watchers import watcher_manager
from release_watcher.outputs import output_manager
from typing import Dict, Sequence
logger = logging.getLogger(__name__)


@click.command()
@click.option('--config', default='config.yaml', help='Config file')
def main(config: str):
    """Entrypoint for the Release Watch application"""

    global_config = config_loader.load_conf(config)
    watchers = _create_watchers(global_config)

    if not watchers:
        logger.error("No configured watchers, nothing to do")
        sys.exit()

    watcher_runner = WatcherRunner(global_config, watchers)

    outputs = _create_ouputs(global_config.outputs)

    if global_config.core.run_mode == 'once':
        _run_once(watcher_runner, outputs)
    else:
        while True:
            _run_once(watcher_runner, outputs)
            logger.debug('Sleeping %d seconds ...' %
                         global_config.core.sleep_duration)
            time.sleep(global_config.core.sleep_duration)


def _create_watchers(global_config: GlobalConfig
                     ) -> Sequence[watcher_manager.Watcher]:
    logger.debug('Listing watchers from sources')
    watchers = []
    for source_conf in global_config.sources:
        logger.debug(' - Source : %s', source_conf.name)
        source_type = source_manager.get_source_type(source_conf.name)
        watchers_for_source = source_type.create_source(
            global_config.common, source_conf).read_watchers()
        logger.debug(' -> %d watchers for %s', len(watchers_for_source),
                     source_conf.name)
        for watcher_config in watchers_for_source:
            watcher_type = watcher_manager.get_watcher_type(
                watcher_config.watcher_type_name)
            watcher = watcher_type.create_watcher(watcher_config)
            watchers.append(watcher)
    return watchers


def _create_ouputs(outputs_conf: output_manager.OutputConfig
                   ) -> Sequence[output_manager.Output]:
    logger.info('Creating outputs')

    return [
        output_manager.get_output_type(
            output_conf.name).create_output(output_conf)
        for output_conf in outputs_conf
    ]


def _run_once(watcher_runner: WatcherRunner,
              outputs: Sequence[output_manager.Output]):
    results = watcher_runner.run()
    for output in outputs:
        logger.info(' - output : %s', output)
        output.outputs(results)
