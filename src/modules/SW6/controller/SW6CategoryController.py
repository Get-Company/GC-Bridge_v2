from pprint import pprint

from sqlalchemy import asc

from ..controller.SW6AbstractController import SW6AbstractController
from ..entities.SW6CategoryEntity import SW6CategoryEntity
from src.modules.Bridge.controller.BridgeCategoryController import BridgeCategoryController
from src.modules.Bridge.entities.BridgeCategoryEntity import BridgeCategoryEntity

class SW6CategoryController(SW6AbstractController):

    def __init__(self):

        self._bridge_controller = BridgeCategoryController()

        super().__init__(
            sw6_entity=SW6CategoryEntity(),
            bridge_controller=self._bridge_controller
        )

    def is_in_db(self, bridge_entity, sw6_json_data):
        bridge_product_entity_in_db = self._bridge_controller.get_entity().query.filter_by(erp_nr=bridge_entity.erp_nr).one_or_nne()
        if bridge_product_entity_in_db:
            self.logger.info(f"Entity {bridge_entity.api_id} found in the db!")
            return bridge_product_entity_in_db
        else:
            self.logger.info(f"No Entity {bridge_entity.api_id} found in the db!")
            return None

    def set_relations(self, bridge_entity, sw6_json_data):
        pass

    def sync_all_from_bridge(self):
        # Overwrite, since we need a special order (cat_nr)
        categories = BridgeCategoryEntity.query.order_by(BridgeCategoryEntity.cat_nr.asc()).all()
        # pprint(categories)
        for category in categories:
            print(f"Upsert Category: {category.get_translation().get_name()} id. {category.get_cat_nr()}")
            self.sync_one_from_bridge(bridge_entity=category)



