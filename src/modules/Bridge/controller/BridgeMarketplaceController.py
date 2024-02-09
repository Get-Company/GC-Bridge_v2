from .BridgeAbstractController import BridgeAbstractController
from ..entities.BridgeMarketplaceEntity import BridgeMarketplaceEntity


class BridgeMarketplaceController(BridgeAbstractController):
    def __init__(self):
        self._bridge_entity = BridgeMarketplaceEntity()
        super().__init__(bridge_entity=self._bridge_entity)


