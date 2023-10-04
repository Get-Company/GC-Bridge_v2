from ..ModulesCoreController import ModulesCoreController
from ..Bridge.entities.BridgeAbstractEntity import BridgeAbstractEntity
from abc import abstractmethod


class SW6CoreController(ModulesCoreController):
    def __init__(self):

        super().__init__()

    """     
    Abstract Methods, defined in ModulesCoreController
    These Methods must bes overwritten. If there is no use of it simply do a pass!
    """

    def sync_all_to_bridge(self):
        pass

    def sync_all_from_bridge(self):
        pass

    def sync_one_to_bridge(self):
        pass

    def sync_one_from_bridge(self):
        pass

    def sync_changed_to_bridge(self):
        pass

    def sync_changed_from_bridge(self):
        pass

    @abstractmethod
    def map_sw6_to_bridge(self):
        pass

    @abstractmethod
    def map_bridge_to_sw6(self, bridge_ntt:BridgeAbstractEntity):
        pass