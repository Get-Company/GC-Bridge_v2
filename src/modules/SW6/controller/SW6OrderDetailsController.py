from pprint3x import pprint

from ..controller.SW6AbstractController import SW6AbstractController
from ..entities.SW6OrderDetailsEntity import SW6OrderDetailsEntity
from src.modules.Bridge.controller.BridgeOrderDetailsController import BridgeOrderDetailsController
from src.modules.Bridge.entities.BridgeOrderDetailsEntity import BridgeOrderDetailsEntity
from src.modules.Bridge.entities.BridgeProductEntity import BridgeProductEntity


class SW6OrderDetailsController(SW6AbstractController):
    def __init__(self):

        self._bridge_controller = BridgeOrderDetailsController()

        super().__init__(
            sw6_entity=SW6OrderDetailsEntity(),
            bridge_controller=self._bridge_controller
        )

    def is_in_db(self, bridge_entity_new, sw6_json_data):
        bridge_order_detail_in_db = self._bridge_controller.get_entity().query.filter_by(api_id=bridge_entity_new.api_id).one_or_none()

        if bridge_order_detail_in_db:
            self.logger.info(f"Entity {bridge_entity_new.id} found in the db!")
            return bridge_order_detail_in_db
        else:
            self.logger.info(f"No Entity {bridge_entity_new.id} found in the db!")
            return None

    def set_relations(self, bridge_entity, sw6_json_data):
        # 1. Order relation is set from Order side
        # Product
        try:
            bridge_entity = self._set_product_relation(bridge_entity=bridge_entity, sw6_json_data=sw6_json_data)
        except Exception as e:
            self.logger.error(f"Failed relations: {e}")

        return bridge_entity

    def _set_product_relation(self, bridge_entity, sw6_json_data):
        try:
            bridge_product_entity = BridgeProductEntity().query.filter_by(
                erp_nr=SW6OrderDetailsEntity().get_erp_nr(sw6_json_data)).one_or_none()

            if bridge_product_entity:
                bridge_entity.product = bridge_product_entity

        except Exception as e:
            self.logger.error(f"Error in _set_product_relation: {e}")

        return bridge_entity

    def sync_all_to_bridge(self, sw6_json_data_list):
        for sw6_json_data in sw6_json_data_list:
            self.upsert(sw6_json_data)



