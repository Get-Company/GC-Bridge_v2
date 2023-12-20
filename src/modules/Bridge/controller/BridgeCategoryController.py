from .BridgeAbstractController import BridgeAbstractController
from ..entities.BridgeCategoryEntity import BridgeCategoryEntity
import json


class BridgeCategoryController(BridgeAbstractController):
    def __init__(self):
        self._bridge_entity = BridgeCategoryEntity()
        super().__init__(bridge_entity=self._bridge_entity)

    def get_entity(self):
        return BridgeCategoryEntity()

    def get_main_category(self, tree_path):
        tree_path_list = json.loads(tree_path)
        main_category_id = tree_path_list[0]
        main_category = self._bridge_entity.query.filter_by(erp_nr=main_category_id).one_or_none()
        if main_category:
            return main_category
        else:
            return None