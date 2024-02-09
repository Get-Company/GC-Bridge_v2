from pprint import pprint

from ..controller.SW6AbstractController import SW6AbstractController
from src.modules.Bridge.controller.BridgeMarketplaceController import BridgeMarketplaceController
from ..entities.SW6MarketplaceEntity import SW6MarketplaceEntity


class SW6MarketplaceController(SW6AbstractController):
    def __init__(self):

        self._bridge_controller = BridgeMarketplaceController()

        super().__init__(
            sw6_entity=SW6MarketplaceEntity(),
            bridge_controller=self._bridge_controller
        )

    def is_in_db(self, bridge_entity_new, sw6_json_data):
        bridge_marketplace_entity_in_db = self._bridge_controller.get_entity().query.filter_by(api_id=bridge_entity_new.api_id).one_or_none()
        if bridge_marketplace_entity_in_db:
            self.logger.info(f"Entity {bridge_entity_new.api_id} found in the db!")
            return bridge_marketplace_entity_in_db
        else:
            self.logger.info(f"No Entity {bridge_entity_new.api_id} found in the db!")
            return None

    def set_relations(self, bridge_entity, sw6_json_data):
        """
        All the relations like:
            Product
            Price
            Orders
            Customers
        are set by themselves.
        :param bridge_entity:
        :param sw6_json_data:
        :return:
        """
        self.logger.info("No relations to set.")
        return bridge_entity






