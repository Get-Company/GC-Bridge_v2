from .BridgeAbstractController import BridgeAbstractController
from ..entities.BridgeCustomerEntity import BridgeCustomerEntity


class BridgeCustomerController(BridgeAbstractController):
    def __init__(self):
        self._bridge_entity = BridgeCustomerEntity()
        super().__init__(bridge_entity=self._bridge_entity)

