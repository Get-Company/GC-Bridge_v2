import re

from ..ModulesCoreController import ModulesCoreController


class BridgeCoreController(ModulesCoreController):
    def __init__(self):

        super().__init__()

    """     
    Abstract Methods, defined in ModulesCoreController
    These Methods must be overwritten. If there is no use of it simply do a pass!
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
