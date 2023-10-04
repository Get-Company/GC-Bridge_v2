from ..entities.SW6AbstractEntity import SW6AbstractEntity
from src.modules.Bridge.entities.BridgeProductEntity import BridgeProductEntity


class SW6ProductEntity(SW6AbstractEntity):
    def __init__(self):
        self.endpoint_name = "product"
        super().__init__(endpoint_name=self.endpoint_name)

    def map_sw6_to_bridge(self):
        """ No need to map the Product sw6 to hte bridge"""
        pass

    def map_bridge_to_sw6(self, bridge_ntt:BridgeProductEntity):
        pass
