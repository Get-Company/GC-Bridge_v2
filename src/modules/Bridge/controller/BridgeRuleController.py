from .BridgeAbstractController import BridgeAbstractController
from ..entities.BridgeRuleEntity import BridgeRuleEntity


class BridgeRuleController(BridgeAbstractController):
    def __init__(self):
        self._bridge_entity = BridgeRuleEntity()

        self._sw6_endpoints = [
            "product",
            "category"
        ]

        super().__init__(bridge_entity=self._bridge_entity)

    def sw6_get_endpoints(self):
        return self._sw6_endpoints

    def sw6_get_endpoint_fields(self, endpoint):
        pass
