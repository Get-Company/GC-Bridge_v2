from ..controller.SW6AbstractController import SW6AbstractController
from ..entities.SW6ProductEntity import SW6ProductEntity
from src.modules.Bridge.controller.BridgeProductController import BridgeProductController


class SW6ProductController(SW6AbstractController):

    def __init__(self):

        self._bridge_controller = BridgeProductController()

        super().__init__(
            sw6_entity=SW6ProductEntity,
            bridge_controller=self._bridge_controller
        )

    def is_in_db(self, bridge_entity_new, sw6_json_data):
        bridge_product_entity_in_db = self._bridge_controller.get_entity().query.filter_by(erp_nr=bridge_entity_new.erp_nr).one_or_nne()
        if bridge_product_entity_in_db:
            self.logger.info(f"Entity {bridge_entity_new.api_id} found in the db!")
            return bridge_product_entity_in_db
        else:
            self.logger.info(f"No Entity {bridge_entity_new.api_id} found in the db!")
            return None

    def set_relations(self, bridge_entity, sw6_json_data):
        pass
