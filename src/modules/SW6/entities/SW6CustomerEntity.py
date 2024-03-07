from datetime import datetime
from pprint import pprint

from ..entities.SW6AbstractEntity import SW6AbstractEntity
from src.modules.Bridge.entities.BridgeCustomerEntity import BridgeCustomerEntity, BridgeCustomerAddressEntity
from lib_shopware6_api_base import Criteria, EqualsFilter


class SW6CustomerEntity(SW6AbstractEntity):

    def __init__(self):
        self._endpoint_name = 'customer'
        super().__init__(endpoint_name=self._endpoint_name)

    def map_sw6_to_bridge(self, sw6_json_data):
        # Check if sw6_json_data is None or not a dictionary
        if sw6_json_data is None or not isinstance(sw6_json_data, dict):
            self.logger.error("Invalid data passed to map_sw6_to_bridge: sw6_json_data is None or not a dictionary")
            return None
        try:
            bridge_customer_entity_new = BridgeCustomerEntity(
                email=self.get_email(sw6_json_data),
                erp_nr=self.get_customer_nr(sw6_json_data),
                vat_id=self.get_vat_id(sw6_json_data),
                created_at=datetime.now(),
                edited_at=datetime.now()
            )
            return bridge_customer_entity_new
        except Exception as e:
            self.logger.error(
                f"SW6 {sw6_json_data['customerNumber']} Customer could not be mapped to BridgeCustomerEntity: {e}")

    def map_bridge_to_sw6(self, bridge_entity):
        # Todo: Is it neccessary to upfate the customer to sw6?
        pass

    def get_api_customer_address_details_by_customer_id(self, id):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field='id', value=id))

        payload.associations["defaultShippingAddress"] = Criteria()
        payload.associations["defaultBillingAddress"] = Criteria()

        payload.associations["addresses"] = Criteria()

        endpoint = self.sw6_client.request_post(f"/search/{self._endpoint_name}", payload=payload)
        return endpoint

    def get_api_customer_by_customer_number(self, customer_nr):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field='customerNumber', value=customer_nr))

        result = self.sw6_client.request_post(f"/search/{self._endpoint_name}", payload=payload)
        return result

    def get_customer_nr(self, sw6_json_data):
        try:
            return sw6_json_data['customerNumber']
        except Exception as e:
            self.logger.error(f"Error retrieving customer number: {e}")
            return None

    def get_email(self, sw6_json_data):
        try:
            return sw6_json_data['email']
        except Exception as e:
            self.logger.error(f"Error retrieving email: {e}")
            return None

    def get_vat_id(self, sw6_json_data):
        try:
            vat_ids = sw6_json_data.get('vatIds')
            if vat_ids and isinstance(vat_ids, list) and len(vat_ids) > 0:
                return vat_ids[0]
            else:

                return None
        except Exception as e:
            self.logger.error(f"Error Customer:{sw6_json_data.get('customerNumber')} retrieving VAT ID: {e}")
            return None

    def get_group_id(self, bridge_entity):
        business_type = 'B2B' if bridge_entity.get_vat_id() else 'B2C'
        return self.config_sw6.CUSTOMER_GROUPS.get(())

    def patch_api_change_customer_nr(self, customer_id, new_customer_nr):
        if not new_customer_nr and not customer_id:
            self.logger.error("Ein 'customer_id' oder 'customer_nr' muss angegeben werden.")
            return

        customer_in_sw6 = self.get_api_(id=customer_id)
        if customer_in_sw6:
            payload = {'customerNumber': new_customer_nr}
            endpoint = self.sw6_client.request_patch(f"/{self._endpoint_name}", payload=payload)
            return endpoint
        else:
            self.logger.error(f"Customer with id: {customer_id} not found. Could not patch 'customerNumber' to {new_customer_nr}.")


class SW6CustomerAddressEntity(SW6AbstractEntity):

    def __init__(self):
        self._endpoint_name = 'customer-address'
        super().__init__(endpoint_name=self._endpoint_name)

    def map_sw6_to_bridge(self, sw6_json_data):
        try:
            bridge_customer_address_entity_new = BridgeCustomerAddressEntity(
                sw6_id=self.get_sw6_id(sw6_json_data),
                name1=self.get_name_1(sw6_json_data),
                name2=self.get_name_2(sw6_json_data),
                name3=self.get_name_3(sw6_json_data),
                department=self.get_department(sw6_json_data),
                street=self.get_street(sw6_json_data),
                postal_code=self.get_postal_code(sw6_json_data),
                city=self.get_city(sw6_json_data),
                land=self.get_land(sw6_json_data),
                email=self.get_email(sw6_json_data),
                title=self.get_title(sw6_json_data),
                first_name=self.get_first_name(sw6_json_data),
                last_name=self.get_last_name(sw6_json_data),
                created_at=datetime.now(),
                edited_at=datetime.now()
            )
            return bridge_customer_address_entity_new
        except Exception as e:
            self.logger.error(f"SW6 Customer Address could not be mapped to BridgeCustomerAddressEntity: {e}")

    def get_api_customer_address_details(self, id):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field='id', value=id))

        payload.associations["salutation"] = Criteria()
        payload.associations["country"] = Criteria()
        payload.associations["countryState"] = Criteria()
        payload.associations["customer"] = Criteria()

        endpoint = self.sw6_client.request_post(f"/search/{self._endpoint_name}", payload=payload)
        return endpoint

    def get_sw6_id(self, sw6_json_data):
        try:
            return sw6_json_data['id']
        except Exception as e:
            self.logger.error(f"Error retrieving id: {e}")
            return None

    def get_name_1(self, sw6_json_data):
        try:
            if sw6_json_data['company']:
                return 'Firma'
            else:
                return sw6_json_data['salutation']['displayName']
        except Exception as e:
            self.logger.error(f"Error retrieving name_1: {e}")
            return None

    def get_name_2(self, sw6_json_data):
        try:
            if self.get_name_1(sw6_json_data) == 'Firma':
                return sw6_json_data['company']
            else:
                first_name = self.get_first_name(sw6_json_data)
                last_name = self.get_last_name(sw6_json_data)
                return f"{first_name} {last_name}"
        except Exception as e:
            self.logger.error(f"Error retrieving name_2: {e}")
            return None

    def get_name_3(self, sw6_json_data):
        # Considering this method is intentionally returning None, no exception handling needed.
        return None

    def get_department(self, sw6_json_data):
        try:
            return sw6_json_data['department']
        except Exception as e:
            self.logger.error(f"Error retrieving department: {e}")
            return None

    def get_street(self, sw6_json_data):
        try:
            return sw6_json_data['street']
        except Exception as e:
            self.logger.error(f"Error retrieving street: {e}")
            return None

    def get_postal_code(self, sw6_json_data):
        try:
            return sw6_json_data['zipcode']
        except Exception as e:
            self.logger.error(f"Error retrieving postal code: {e}")
            return None

    def get_city(self, sw6_json_data):
        try:
            return sw6_json_data['city']
        except Exception as e:
            self.logger.error(f"Error retrieving city: {e}")
            return None

    def get_land(self, sw6_json_data):
        try:
            return sw6_json_data['country']['iso']
        except Exception as e:
            self.logger.error(f"Error retrieving land: {e}")
            return None

    def get_email(self, sw6_json_data):
        try:
            return sw6_json_data['customer']['email']
        except Exception as e:
            self.logger.error(f"Error retrieving email: {e}")
            return None

    def get_title(self, sw6_json_data):
        try:
            return sw6_json_data['salutation']['displayName']
        except Exception as e:
            self.logger.error(f"Error retrieving title: {e}")
            return None

    def get_first_name(self, sw6_json_data):
        try:
            return sw6_json_data['firstName']
        except Exception as e:
            self.logger.error(f"Error retrieving first name: {e}")
            return None

    def get_last_name(self, sw6_json_data):
        try:
            return sw6_json_data['lastName']
        except Exception as e:
            self.logger.error(f"Error retrieving last name: {e}")
            return None
