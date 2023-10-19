from .BridgeAbstractController import BridgeAbstractController
from ..entities.BridgeCategoryEntity import BridgeCategoryEntity


class BridgeCategoryController(BridgeAbstractController):
    def __init__(self):
        self._bridge_entity = BridgeCategoryEntity()
        super().__init__(bridge_entity=self._bridge_entity)

    def get_entity(self):
        return BridgeCategoryEntity()





