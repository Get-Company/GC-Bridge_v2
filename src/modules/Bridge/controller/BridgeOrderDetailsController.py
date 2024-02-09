from .BridgeAbstractController import BridgeAbstractController
from ..entities.BridgeOrderDetailsEntity import BridgeOrderDetailsEntity


class BridgeOrderDetailsController(BridgeAbstractController):
    def __init__(self):
        self._bridge_entity = BridgeOrderDetailsEntity()
        super().__init__(bridge_entity=self._bridge_entity)