from ..entities.SW6AbstractEntity import SW6AbstractEntity
from src.modules.Bridge.entities.BridgeCategoryEntity import BridgeCategoryEntity


class SW6CategoryEntity(SW6AbstractEntity):
    def __init__(self):
        self.endpoint_name = "category"
        super().__init__(endpoint_name=self.endpoint_name)

