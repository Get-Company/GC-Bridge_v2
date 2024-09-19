from pprint import pprint

from ..controller.SW6AbstractController import SW6AbstractController
from ..controller.SW6CustomerController import SW6CustomerController
from ..controller.SW6MarketplaceController import SW6MarketplaceController
from ..controller.SW6OrderDetailsController import SW6OrderDetailsController
from src.modules.Bridge.controller.BridgeCustomerController import BridgeCustomerController
from src.modules.Bridge.controller.BridgeMarketplaceController import BridgeMarketplaceController
from src.modules.Bridge.controller.BridgeOrderController import BridgeOrderController
from src.modules.Bridge.controller.BridgeOrderDetailsController import BridgeOrderDetailsController
from ..entities.SW6OrderEntity import SW6OrderEntity
from src.modules.Bridge.entities.BridgeMarketplaceEntity import BridgeMarketplaceEntity, BridgeCustomerMarketplaceAssoc
from src.modules.Bridge.entities.BridgeCustomerEntity import BridgeCustomerEntity
from src.modules.Bridge.entities.BridgeOrderDetailsEntity import BridgeOrderDetailsEntity


class SW6OrderController(SW6AbstractController):
    def __init__(self):

        self._bridge_controller = BridgeOrderController()

        super().__init__(
            sw6_entity=SW6OrderEntity(),
            bridge_controller=self._bridge_controller
        )

    def sync_all_to_bridge(self, sw6_json_list):
        for sw6_json_data in sw6_json_list["data"]:
            self.upsert(sw6_json_data=sw6_json_data)

    def sync_one_to_bridge(self, sw6_json_data=None, sw6_entity_id=None):
        """ Changed from get_api to get_api_order_details_by_order_id"""
        if sw6_json_data:
            bridge_entity_id = self.upsert(sw6_json_data=sw6_json_data)
            if bridge_entity_id:
                return bridge_entity_id

        if sw6_entity_id:
            sw6_json_data = self.get_entity().get_api_order_details_by_order_id(id=sw6_entity_id)
            # Sometimes, when using /search we get back a list not just one element
            # Even though the list contains one element!!
            if isinstance(sw6_json_data['data'], list):
                bridge_entity_id = self.upsert(sw6_json_data=sw6_json_data['data'][0])
            else:
                bridge_entity_id = self.upsert(sw6_json_data=sw6_json_data['data'])
            if bridge_entity_id:
                return bridge_entity_id

        if not sw6_json_data and not sw6_entity_id:
            self.logger.error("Neither sw6_json_data nor sw6_entity_id are set. Set at least 1 of them")
            return

    def is_in_db(self, bridge_entity_new, sw6_json_data):
        bridge_order_entity_in_db = self._bridge_controller.get_entity().query.filter_by(api_id=bridge_entity_new.api_id).one_or_none()
        if bridge_order_entity_in_db:
            self.logger.info(f"Entity {bridge_entity_new.api_id} found in the db!")
            return bridge_order_entity_in_db
        else:
            self.logger.info(f"No Entity {bridge_entity_new.api_id} found in the db!")
            return None

    def set_relations(self, bridge_entity, sw6_json_data):
        # 1. Marketplace
        bridge_entity = self._set_marketplace_relation(bridge_entity=bridge_entity, sw6_json_data=sw6_json_data)
        # 2. OrderDetails
        bridge_entity = self._set_order_details_relation(bridge_entity=bridge_entity, sw6_json_data=sw6_json_data)
        # 3. Customers
        bridge_entity = self._set_customer_relation(bridge_entity=bridge_entity, sw6_json_data=sw6_json_data)

        return bridge_entity

    def _set_marketplace_relation(self, bridge_entity, sw6_json_data):
        """
        This function establishes a marketplace relation between the bridge entity and the given sw6_json_data

        Args:
            bridge_entity : The bridge_entity object to which the relation is being set
            sw6_json_data : The Salesway 6 data in JSON format

        Returns:
            The updated bridge_entity object with established marketplace relation
        """

        try:

            # Upserting the marketplace
            SW6MarketplaceController().sync_one_to_bridge(sw6_entity_id=sw6_json_data['salesChannel']['id'])

            # Getting the bridge_marketplace_entity
            bridge_marketplace_entity = BridgeMarketplaceController().get_entity().query \
                .filter_by(api_id=sw6_json_data['salesChannel']['id']) \
                .one_or_none()

            if bridge_marketplace_entity:
                # Relating the bridge_marketplace_entity to the bridge_entity
                bridge_entity.marketplace = bridge_marketplace_entity

            return bridge_entity

        except Exception as e:
            self.logger.error(f"Error in _set_marketplace_relation: {e}")
            raise

    def _set_order_details_relation(self, bridge_entity, sw6_json_data):
        # Upsert
        SW6OrderDetailsController().sync_all_to_bridge(sw6_json_data_list=sw6_json_data['lineItems'])
        # Relate
        bridge_order_details_entities = BridgeOrderDetailsController().get_entity().query.filter_by(api_order_id=bridge_entity.get_api_id()).all()
        if bridge_order_details_entities:
            for orderdetail in bridge_order_details_entities:
                bridge_entity.order_details.append(orderdetail)
        return bridge_entity

    def _set_customer_relation(self, bridge_entity, sw6_json_data):
        # 1. Upsert
        sw6_json_customer_details = SW6CustomerController().get_entity().get_api_(id=sw6_json_data['orderCustomer']['customerId'])
        SW6CustomerController().sync_one_to_bridge(sw6_json_data=sw6_json_customer_details['data'])

        # 2. Set Relation
        bridge_customer = BridgeCustomerEntity.query.filter_by(erp_nr=sw6_json_customer_details['data']['customerNumber']).one_or_none()
        if bridge_customer:
            bridge_entity.customer = bridge_customer
        return bridge_entity

    def get_api_state_machines_list_for_config(self):
        search_values = ["order.state", "order_transaction.state", "order_transaction.state"]
        states = []
        for search_value in search_values:
            results = self.get_entity().search_api_state_machine_by_(
                index_field="technicalName",
                search_value=search_value
            )
            if results['total'] >= 0:
                states.append(results['data'][0])

        pprint(states)

    def sync_all_open_orders_to_bridge(self):
        pass

    """
    SW5
    """

    def sw5_sync_one_to_sw6(self, sw5_json_order_data):
        pass
