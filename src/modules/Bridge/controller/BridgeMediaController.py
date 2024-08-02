import uuid
from pprint import pprint

from .BridgeAbstractController import BridgeAbstractController
from ..entities.BridgeMediaEntity import BridgeMediaEntity


class BridgeMediaController(BridgeAbstractController):
    def __init__(self):
        self._bridge_entity = BridgeMediaEntity()
        super().__init__(bridge_entity=self._bridge_entity)
