import logging
from pathlib import Path
from os import path
from typing import Dict, Sequence
from yaml import load
from release_watcher.sources import source_manager
from release_watcher.outputs import output_manager
from release_watcher.config_models import \
    ConfigException, GlobalConfig, LoggerConfig, CommonConfig, CoreConfig, \
    GithubConfig, DockerConfig, PypiConfig, RawHtmlConfig

try:
    from yaml import CLoader as Loader  # pylint: disable=ungrouped-imports
except ImportError:
    from yaml import Loader

logger = logging.getLogger(__name__)


def load_conf(config_file: str) -> GlobalConfig:
    """Load configuration from the main config file

    It reads the main config file and :
    * reads the logger configuration
    * init the loggers
    * parses the source configuration
    * parses the outputs configuration
    """

    logger.info('Loading configuration file  : %s', config_file)

    with open(config_file, 'r', encoding='UTF-8') as ymlfile:
        conf = load(ymlfile, Loader=Loader)

    conf['configFileDir'] = path.dirname(Path(config_file).resolve())
    _init_logger(_parse_logger_conf(conf))

    return _parse_conf(conf)


def _parse_logger_conf(conf: Dict) -> LoggerConfig:
    default_conf = {'type': 'stdout', 'level': 'INFO'}
    conf_logger = conf.get('logger', default_conf)

    logger_type = conf_logger.get('type', 'stdout')
    logger_path = None

    if logger_type == 'file':
        logger_path = conf_logger.get('path', 'release_watcher.log')
    elif logger_type != 'stdout':
        logger.warning('logger.type %s is invalid, falling back to stdout', logger_type)
        logger_type = 'stdout'

    logger_level = conf_logger.get('level', 'INFO').upper()

    if logger_level not in ['DEBUG', 'INFO', 'WARN', 'ERROR']:
        logger.warning('logger.level %s is invalid, falling back to INFO', logger_level)
        logger_level = 'INFO'

    return LoggerConfig(logger_type, logger_level, logger_path)


def _init_logger(logger_conf: LoggerConfig):
    if logger_conf.logger_type == 'file':
        logging.basicConfig(filename=logger_conf.path, level=logger_conf.level)
    else:
        logging.basicConfig(level=logger_conf.level)


def _parse_conf(conf: Dict) -> GlobalConfig:
    config = GlobalConfig()
    config.core = _parse_core_conf(conf)
    config.common = CommonConfig()
    config.common.github = _parse_github_conf(conf)
    config.common.docker = _parse_docker_conf(conf)
    config.common.pypi = _parse_pypi_conf(conf)
    config.common.raw_html = _parse_raw_html_conf(conf)

    config.sources = _parse_sources_conf(conf)
    if not config.sources:
        raise ConfigException('No valid source configuration found')

    config.outputs = _parse_outputs_conf(conf)
    if not config.outputs:
        raise ConfigException('No valid output configuration found')

    return config


def _parse_core_conf(conf: Dict) -> CoreConfig:
    logger.debug('Loading core configuration')

    default_conf = {'threads': 2, 'runMode': 'once', 'sleepDuration': 5}

    core_conf = conf.get('core', default_conf)
    threads = core_conf.get('threads', default_conf['threads'])

    if not isinstance(threads, int):
        logger.warning('threads %s is not a number, falling back to %d',
                       threads, default_conf['threads'])
        threads = default_conf['threads']

    run_mode = core_conf.get('runMode', default_conf['runMode'])

    sleep_duration = None
    if run_mode == 'repeat':
        sleep_duration = core_conf.get('sleepDuration',
                                       default_conf['sleepDuration'])
        if not isinstance(sleep_duration, int):
            logger.warning('sleepDuration %s is not a number, falling back to %d',
                           sleep_duration, default_conf['sleepDuration'])
            sleep_duration = default_conf['sleepDuration']
    elif run_mode != 'once':
        logger.warning('runMode %s is unknown, falling back to %s',
                       run_mode, default_conf['runMode'])
        run_mode = default_conf['runMode']

    core_config = CoreConfig(threads, run_mode)
    core_config.sleep_duration = sleep_duration
    return core_config


def _parse_github_conf(conf: Dict) -> GithubConfig:
    logger.debug('Loading github configuration')

    default_conf = {
        'timeout': 10,
        'rate_limit_wait_max': 120,
    }

    common_conf = conf.get('common', {'github': default_conf})
    github_conf = common_conf.get('github', default_conf)
    github_config = GithubConfig()

    github_config.username = github_conf.get('username')
    github_config.password = github_conf.get('password')

    timeout = github_conf.get('timeout', default_conf['timeout'])
    if not isinstance(timeout, (int, float)):
        logger.warning('timeout %s is not a number, falling back to %d',
                       timeout, default_conf['timeout'])
        timeout = default_conf['timeout']
    github_config.timeout = timeout

    rate_limit_wait_max = github_conf.get('rate_limit_wait_max',
                                          default_conf['rate_limit_wait_max'])
    if not isinstance(rate_limit_wait_max, int):
        logger.warning('rate_limit_wait_max %s is not a number, falling back to %d',
                       rate_limit_wait_max, default_conf['rate_limit_wait_max'])
        rate_limit_wait_max = default_conf['rate_limit_wait_max']
    github_config.rate_limit_wait_max = rate_limit_wait_max

    return github_config


def _parse_docker_conf(conf: Dict) -> DockerConfig:
    logger.debug('Loading docker configuration')

    default_conf = {
        'timeout': 10,
    }

    common_conf = conf.get('common', {'docker': default_conf})
    docker_conf = common_conf.get('docker', default_conf)
    docker_config = DockerConfig()

    timeout = docker_conf.get('timeout', default_conf['timeout'])
    if not isinstance(timeout, (int, float)):
        logger.warning('timeout %s is not a number, falling back to %d',
                       timeout, default_conf['timeout'])
        timeout = default_conf['timeout']
    docker_config.timeout = timeout

    return docker_config


def _parse_pypi_conf(conf: Dict) -> PypiConfig:
    logger.debug('Loading pypi configuration')

    default_conf = {
        'timeout': 10,
    }

    common_conf = conf.get('common', {'pypi': default_conf})
    pypi_conf = common_conf.get('pypi', default_conf)
    pypi_config = PypiConfig()

    timeout = pypi_conf.get('timeout', default_conf['timeout'])
    if not isinstance(timeout, (int, float)):
        logger.warning('timeout %s is not a number, falling back to %d',
                       timeout, default_conf['timeout'])
        timeout = default_conf['timeout']
    pypi_config.timeout = timeout

    return pypi_config


def _parse_raw_html_conf(conf: Dict) -> PypiConfig:
    logger.debug('Loading raw_html configuration')

    default_conf = {
        'timeout': 10,
    }

    common_conf = conf.get('common', {'raw_html': default_conf})
    raw_html_conf = common_conf.get('raw_html', default_conf)
    raw_html_config = RawHtmlConfig()

    timeout = raw_html_conf.get('timeout', default_conf['timeout'])
    if not isinstance(timeout, (int, float)):
        logger.warning('timeout %s is not a number, falling back to %d',
                       timeout, default_conf['timeout'])
        timeout = default_conf['timeout']
    raw_html_config.timeout = timeout

    return raw_html_config


def _parse_sources_conf(conf: Dict) -> Sequence[source_manager.SourceConfig]:
    logger.debug('Loading sources configuration')
    sources_conf = []

    if 'sources' in conf and isinstance(conf['sources'], list):
        for source_conf in conf['sources']:
            try:
                sources_conf.append(_parse_one_source_conf(conf, source_conf))
            except Exception as e:
                logger.exception('Error configuring a source : %s', e)

    return sources_conf


def _parse_one_source_conf(global_conf: Dict,
                           source_conf: Dict) -> source_manager.SourceConfig:
    logger.debug(' - %s', source_conf)

    if 'type' in source_conf:
        source_type = source_manager.get_source_type(source_conf['type'])
        return source_type.parse_config(global_conf, source_conf)

    raise ValueError('Missing type property on source configuration')


def _parse_outputs_conf(conf: Dict) -> Sequence[output_manager.OutputConfig]:
    logger.debug('Loading outputs configuration')

    parsed_outputs_conf = []

    if 'outputs' in conf and isinstance(conf['outputs'], list):
        for output_conf in conf['outputs']:
            try:
                parsed_outputs_conf.append(
                    _parse_one_output_conf(conf, output_conf))
            except Exception as e:
                logger.exception('Error configuring an output : %s', e)

    return parsed_outputs_conf


def _parse_one_output_conf(global_conf: Dict, output_conf: Dict) -> output_manager.OutputConfig:
    logger.debug(' - %s', output_conf)

    if 'type' in output_conf:
        output_type = output_manager.get_output_type(output_conf['type'])
        return output_type.parse_config(global_conf, output_conf)

    raise ValueError('Missing type property on output configuration')
