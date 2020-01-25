import logging
import requests
from bs4 import BeautifulSoup, Tag
import dateutil.parser
from typing import Dict, Sequence
from release_watcher.watchers.watcher_models \
    import Release, WatchError, WatchResult
from release_watcher.watchers.watcher_manager \
    import Watcher, WatcherConfig, WatcherType

logger = logging.getLogger(__name__)

WATCHER_TYPE_NAME = 'raw_html'


class RawHtmlWatcherConfig(WatcherConfig):
    """Class to store the configuration for a RawHtmlWatcher"""

    page_url: str = None
    container_selector: str = None
    item_selector: str = None
    id_selector: str = None
    id_attribute: str = None
    date_selector: str = None
    date_attribute: str = None
    reverse: bool = False
    basic_auth: Dict = None
    id: str = None

    def __init__(self, name: str, page_url: str, id: str):
        super().__init__(WATCHER_TYPE_NAME, name)
        self.page_url = page_url
        self.id = id

    def __str__(self) -> str:
        return '%s' % (self.page_url)


class RawHtmlWatcher(Watcher):
    """Implementation of a Watcher that checks for new commits in a GitHub
    repository"""

    def __init__(self, config: RawHtmlWatcherConfig):
        super().__init__(config)

    def _do_watch(self) -> WatchResult:
        logger.debug("Watching raw html %s" % self.config)
        item_elements = self._call_raw_page()
        current_id = self.config.id
        current_release = None
        missed_items = []

        for item_element in item_elements:
            item_id = self._extractValue(item_element,
                                         self.config.id_selector,
                                         self.config.id_attribute)
            item_date_string = self._extractValue(item_element,
                                                  self.config.date_selector,
                                                  self.config.date_attribute)
            item_date = dateutil.parser.parse(item_date_string)

            item = Release(item_id, item_date)

            if item_id == current_id:
                logger.debug("Current item '%s' found" % current_id)
                current_release = item
                break

            missed_items.append(item)

        if not current_release:
            logger.warning("Current item '%s' not found !", current_id)

        logger.debug('Missed items : %s', missed_items)
        return WatchResult(self.config, current_release, missed_items)

    def _call_raw_page(self) -> Sequence[Tag]:
        if self.config.basic_auth:
            auth = (self.config.basic_auth['username'], self.config.basic_auth['password'])
        else:
            auth = None
        response = requests.get(self.config.page_url, auth=auth)

        if response.status_code == 200:
            response_content = response.content.decode('utf-8')
            soup = BeautifulSoup(response_content, 'html.parser')

            if self.config.container_selector:
                container_element = soup.select_one(self.config.container_selector)
            else:
                container_element = soup

            if not container_element:
                raise WatchError("Error extracting container element")

            item_elements = container_element.select(self.config.item_selector)

            if not item_elements:
                raise WatchError("Error extracting elements")

            if self.config.reverse:
                item_elements.reverse()

            return item_elements
        else:
            logger.debug('Github api call failed : code = %s, content = %s' %
                         (response.status_code, response.content))
            raise WatchError("Github api call failed : %s" % response)

    def _extractValue(self, item_element, attr_selector, attr_property):
        value_element = item_element.select_one(attr_selector)

        if attr_property:
            value = value_element[attr_property]
        else:
            if value_element.text:
                value = value_element.text
            else:
                value = value_element

        return value


class RawHtmlWatcherType(WatcherType):
    """Class to represent the RawHtmlWatcher type of Watcher"""

    def __init__(self):
        super().__init__(WATCHER_TYPE_NAME)

    def parse_config(self, watcher_config: Dict):
        page_url = watcher_config['page_url']
        id = str(watcher_config['id'])
        name = watcher_config.get('name', page_url)

        config = RawHtmlWatcherConfig(name, page_url, id)

        if 'container_selector' in watcher_config:
            config.container_selector = watcher_config['container_selector']
        if 'item_selector' in watcher_config:
            config.item_selector = watcher_config['item_selector']
        if 'id_selector' in watcher_config:
            config.id_selector = watcher_config['id_selector']
        if 'id_attribute' in watcher_config:
            config.id_attribute = watcher_config['id_attribute']
        if 'date_selector' in watcher_config:
            config.date_selector = watcher_config['date_selector']
        if 'date_attribute' in watcher_config:
            config.date_attribute = watcher_config['date_attribute']
        if 'reverse' in watcher_config:
            config.reverse = watcher_config['reverse']
        if 'basic_auth' in watcher_config:
            config.basic_auth = watcher_config['basic_auth']

        return config

    def create_watcher(self, watcher_config: RawHtmlWatcherConfig
                       ) -> RawHtmlWatcher:
        return RawHtmlWatcher(watcher_config)
