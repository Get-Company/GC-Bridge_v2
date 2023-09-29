from ..ModulesCoreController import ModulesCoreController
from abc import abstractmethod


class SW6CoreController(ModulesCoreController):
    def __init__(self):

        super().__init__()

    """     
    Abstract Methods, defined in ModulesCoreController
    These Methods must bes overwritten. If there is no use of it simply do a pass!
    """

    @abstractmethod
    def sync_all_to_bridge(self):
        pass

    @abstractmethod
    def sync_all_from_bridge(self):
        pass

    @abstractmethod
    def sync_one_to_bridge(self):
        pass

    @abstractmethod
    def sync_one_from_bridge(self):
        pass

    @abstractmethod
    def sync_changed_to_bridge(self):
        pass

    @abstractmethod
    def sync_changed_from_bridge(self):
        pass