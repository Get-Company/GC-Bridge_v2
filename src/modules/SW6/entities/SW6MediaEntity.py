from pprint import pprint
from lib_shopware6_api_base import Criteria, EqualsFilter
import config
from ..entities.SW6AbstractEntity import SW6AbstractEntity


class SW6MediaEntity(SW6AbstractEntity):
    def __init__(self):
        self.endpoint_name = "media"
        super().__init__(endpoint_name=self.endpoint_name)

    def map_sw6_to_bridge(self):
        """ No need to map the Media sw6 to the bridge """
        pass

    def map_bridge_to_sw6(self, bridge_entity):
        """ No need to map Media from bridge to sw6 """
        pass









