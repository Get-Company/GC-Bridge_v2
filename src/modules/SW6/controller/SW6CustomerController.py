from pprint import pprint

from ..controller.SW6AbstractController import SW6AbstractController
from src.modules.Bridge.controller.BridgeCustomerController import BridgeCustomerController, BridgeCustomerAddressController
from ..entities.SW6CustomerEntity import SW6CustomerEntity, SW6CustomerAddressEntity
from src.modules.Bridge.entities.BridgeMarketplaceEntity import BridgeCustomerMarketplaceAssoc, BridgeMarketplaceEntity
from ...Bridge.entities.BridgeCustomerEntity import BridgeCustomerEntity
from .SW6MarketplaceController import SW6MarketplaceController


class SW6CustomerController(SW6AbstractController):
    def __init__(self):

        self._bridge_controller = BridgeCustomerController()

        super().__init__(
            sw6_entity=SW6CustomerEntity(),
            bridge_controller=self._bridge_controller
        )

    def is_in_db(self, bridge_entity_new, sw6_json_data):
        bridge_customer_entity_in_db = self._bridge_controller.get_entity().query. \
            filter_by(email=bridge_entity_new.get_email()). \
            one_or_none()
        if bridge_customer_entity_in_db:
            self.logger.info(f"Entity {bridge_entity_new.id} found in the db!")
            return bridge_customer_entity_in_db
        else:
            self.logger.info(f"No Entity {bridge_entity_new.id} found in the db!")
            return None

    def upsert(self, sw6_json_data):
        """
        Upsert a customer entity and set its default billing and shipping addresses.

        Args:
            sw6_json_data (dict): JSON data from SW6 containing customer and address information.

        Returns:
            int: The ID of the upserted customer entity.
        """
        # Upsert the customer entity and get its ID
        customer_id = super().upsert(sw6_json_data=sw6_json_data)

        # Retrieve the upserted customer entity
        bridge_customer = self._bridge_controller.get_entity().query.get(customer_id)

        if bridge_customer:
            # Retrieve and set the default billing address
            default_billing_address_id = sw6_json_data.get('defaultBillingAddressId')
            billing_address = BridgeCustomerAddressController().get_entity().query.filter_by(
                sw6_id=default_billing_address_id
            ).one_or_none()

            bridge_customer.standard_billing_address = billing_address if billing_address else BridgeCustomerAddressController().get_entity().queryfilter_by(customer_id=customer_id).first()

            # Retrieve and set the default shipping address
            default_shipping_address_id = sw6_json_data.get('defaultShippingAddressId')
            shipping_address = BridgeCustomerAddressController().get_entity().query.filter_by(
                sw6_id=default_shipping_address_id
            ).one_or_none()

            bridge_customer.standard_shipping_address = shipping_address if shipping_address else BridgeCustomerAddressController().get_entity().queryfilter_by(customer_id=customer_id).first()

            # Merge the updated customer entity and commit the changes
            try:
                self.db.session.merge(bridge_customer)
                self.db.session.commit()
            except Exception as e:
                # Log the error and possibly re-raise or handle it
                self.logger.error(f"Failed to merge and commit customer entity: {e}")

        return customer_id


    def set_relations(self, bridge_entity, sw6_json_data):
        # 1. Marketplace
        bridge_entity = self._set_marketplace_relation(bridge_entity, sw6_json_data)
        # 2. Orders are set in the SW6OrderController
        # 3. Addresses
        bridge_entity = self._set_address_relation(bridge_entity, sw6_json_data)
        # 4.1 Standard billing and shipping
        # bridge_entity = self._set_standard_addresses(bridge_entity=bridge_entity, sw6_json_data=sw6_json_data)
        return bridge_entity

    def _set_marketplace_relation(self, bridge_entity, sw6_json_data):
        """
        Establishes or updates a relationship between a customer and a marketplace based on SW6 data.

        This method first ensures that the marketplace corresponding to the provided SW6 data exists
        (or creates it if it doesn't). It then either establishes a new relationship between the customer
        and the marketplace or updates the existing one.

        Parameters:
        bridge_entity (BridgeCustomerEntity): The customer entity to associate with a marketplace.
        sw6_json_data (dict): The SW6 data containing marketplace and customer association information.

        Returns:
        bridge_entity (BridgeCustomerEntity): The updated customer entity with marketplace association.
        """
        try:
            # Upsert marketplace based on SW6 data
            SW6MarketplaceController().sync_one_to_bridge(sw6_entity_id=sw6_json_data["salesChannelId"])

            # Retrieve the corresponding marketplace entity
            bridge_marketplace_entity = BridgeMarketplaceEntity.query.filter_by(
                api_id=sw6_json_data["salesChannelId"]
            ).one_or_none()

            if bridge_marketplace_entity is None:
                self.logger.error("Marketplace entity not found for API ID: " + sw6_json_data["salesChannelId"])
                return bridge_entity

            # Check if the customer-marketplace association already exists
            assoc = BridgeCustomerMarketplaceAssoc.query.filter_by(
                customer_id=bridge_entity.id,
                marketplace_id=bridge_marketplace_entity.id
            ).one_or_none()

            if assoc:
                self.logger.info("Updating existing customer-marketplace association.")
            else:
                self.logger.info("Creating new customer-marketplace association.")
                assoc = BridgeCustomerMarketplaceAssoc(
                    customer=bridge_entity,
                    marketplace=bridge_marketplace_entity
                )

            # Set or update the customer_marketplace_id
            assoc.customer_marketplace_id = sw6_json_data["id"]
            self.db.session.add(assoc)
            self.db.session.commit()

        except Exception as e:
            self.logger.error("Error in _set_marketplace_relation: " + str(e))
            # Optionally, re-raise the exception if you want to handle it upstream
            # raise

        return bridge_entity

    def _set_address_relation(self, bridge_entity, sw6_json_data):
        # 1. Upsert
        sw6_customer_details = self.get_entity().get_api_customer_address_details_by_customer_id(sw6_json_data["id"])
        for sw6_customer_detail in sw6_customer_details['data']:
            for sw6_customer_address in sw6_customer_detail['addresses']:
                sw6_customer_address_details = SW6CustomerAddressEntity().get_api_customer_address_details(id=sw6_customer_address['id'])
                SW6CustomerAddressController().sync_one_to_bridge(sw6_json_data=sw6_customer_address_details['data'][0])

                # 2 Set Relation
                bridge_address = BridgeCustomerAddressController().get_entity().query.filter_by(sw6_id=sw6_customer_address['id']).one_or_none()
                if bridge_address:
                    bridge_entity.addresses.append(bridge_address)

        return bridge_entity

    def _set_standard_addresses(self, bridge_entity, sw6_json_data):

        return bridge_entity


class SW6CustomerAddressController(SW6AbstractController):

    def __init__(self):

        self._bridge_controller = BridgeCustomerAddressController()
        super().__init__(
            sw6_entity=SW6CustomerAddressEntity(),
            bridge_controller=self._bridge_controller
        )

    def is_in_db(self, bridge_entity_new, sw6_json_data):
        bridge_customer_address_entity_in_db = (self._bridge_controller.get_entity().query.
                                                filter_by(sw6_id=bridge_entity_new.get_sw6_id()).one_or_none())
        if bridge_customer_address_entity_in_db:
            self.logger.info(f"Entity {bridge_entity_new.id} found in the db!")
            return bridge_customer_address_entity_in_db
        else:
            self.logger.info(f"No Entity {bridge_entity_new.id} found in the db!")
            return None

    def set_relations(self, bridge_entity, sw6_json_data):
        return bridge_entity



