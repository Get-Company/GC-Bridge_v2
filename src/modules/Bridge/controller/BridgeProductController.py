from .BridgeAbstractController import BridgeAbstractController
from ..entities.BridgeProductEntity import BridgeProductEntity


class BridgeProductController(BridgeAbstractController):
    def __init__(self):
        self._bridge_entity = BridgeProductEntity()
        super().__init__(bridge_entity=self._bridge_entity)



