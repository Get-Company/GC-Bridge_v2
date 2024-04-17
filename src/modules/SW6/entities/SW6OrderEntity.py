from datetime import datetime
from pprint import pprint

from ..entities.SW6AbstractEntity import SW6AbstractEntity
from src.modules.Bridge.entities.BridgeOrderEntity import BridgeOrderEntity
from lib_shopware6_api_base import Criteria, EqualsFilter

from config import SW6Config

class SW6OrderEntity(SW6AbstractEntity):

    def __init__(self):
        self.endpoint_name = "order"
        super().__init__(endpoint_name=self.endpoint_name)

    def map_sw6_to_bridge(self, sw6_json_data):
        try:
            bridge_order_entity_new = BridgeOrderEntity(
                api_id=self.get_api_id(sw6_json_data),
                description=self.get_description(sw6_json_data),
                total_price=self.get_total_price(sw6_json_data),
                shipping_costs=self.get_shipping_costs(sw6_json_data),
                payment_method=self.get_payment_method(sw6_json_data),
                shipping_method=self.get_shipping_method(sw6_json_data),
                order_number=self.get_order_number(sw6_json_data),
                # States
                order_state=self.get_order_state(sw6_json_data),
                shipping_state=self.get_shipping_state(sw6_json_data),
                payment_state=self.get_payment_state(sw6_json_data),
                # Datetimes
                purchase_date=self.get_purchase_date(sw6_json_data),
                created_at=datetime.now(),
                edited_at=datetime.now(),
            )
            return bridge_order_entity_new
        except Exception as e:
            self.logger.error(f"SW6 Order could not be mapped to BridgeOrderEntity: {e}")

    def map_bridge_to_sw6(self, bridge_entity):
        pass

    """
    API
    """

    def get_api_order_details_by_order_id(self, id):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field='id', value=id))

        payload.associations["salesChannel"] = Criteria()

        shipping_assoc = Criteria()
        shipping_assoc.associations["shippingMethod"] = Criteria()
        payload.associations["deliveries"] = shipping_assoc

        payment_assoc = Criteria()
        payment_assoc.associations["paymentMethod"] = Criteria()
        payload.associations["transactions"] = payment_assoc

        payload.associations["lineItems"] = Criteria()

        endpoint = self.sw6_client.request_post(f"/search/{self._endpoint_name}", payload=payload)

        return endpoint

    def get_api_order_details_transactions_and_deliveries_by_order_id(self, id):
        payload = Criteria()
        payload.associations["transactions"] = Criteria()
        payload.associations["deliveries"] = Criteria()

        payload.includes["order"] = ['id', "transactions", "deliveries"]

        payload.limit = 1

        result = self.sw6_client.request_post(f"/search/{self._endpoint_name}", payload=payload)
        return result

    def get_api_order_states_by_order_id(self, id):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field='id', value=id))

        payload.associations['stateMachineState'] = Criteria()

        from_state_assoc = Criteria()
        from_state_assoc.associations["fromStateMachineTransitions"] = Criteria()
        payload.associations['stateMachineState'] = from_state_assoc

        to_state_assoc = Criteria()
        to_state_assoc.associations["toStateMachineTransitions"] = Criteria()
        payload.associations['stateMachineState'] = to_state_assoc

        endpoint = self.sw6_client.request_post(f"/search/{self._endpoint_name}", payload=payload)

        return endpoint

    def get_api_order_ids_by_state(self, state="open"):
        """
        Get orders ids by state.
        States:
        open
        in_progress
        :return: int ids json
        """
        results = self.search_api_ids_by_(index_field="stateMachineState.technicalName", search_value=state)

        return results

    # States

    def get_api_state_machine_state_by_(self, field, value, state_machine_id):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field=field, value=value))
        payload.filter.append(EqualsFilter(field='stateMachineId', value=state_machine_id))

        payload.associations['fromStateMachineTransitions'] = Criteria()
        payload.associations['fromStateMachineTransitions'] = Criteria()

        result_list = self.sw6_client.request_post("search/state-machine-state", payload=payload)
    
        return result_list

    def get_api_state_machine_transition_by_(self, state_machine_state_id, state_machine_id):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field="fromStateId", value=state_machine_state_id))
        payload.filter.append(EqualsFilter(field='stateMachineId', value=state_machine_id))

        payload.associations['fromStateMachineState'] = Criteria()
        payload.associations['toStateMachineState'] = Criteria()

        result_list = self.sw6_client.request_post("search/state-machine-transition", payload=payload)
        return result_list

    def get_api_state_machine_list(self):
        results = self.sw6_client.request_get("/state-machine")
        return results

    def search_api_state_machine_by_(self, index_field, search_value):
        payload = Criteria()

        payload.filter.append(EqualsFilter(field=index_field, value=search_value))
        results = self.sw6_client.request_post("search/state-machine", payload=payload)

        return results

    def patch_api_change_order_state(self, order_id, action_name):
        results = self.sw6_client.request_post(f"_action/order/{order_id}/state/{action_name}")
        return results

    def patch_api_change_order_transaction_state(self, order_id, action_name):
        # Todo: On change to in progress, the address of the customer vanishes?!
        result_states = self.get_api_order_details_transactions_and_deliveries_by_order_id(id=order_id)
        order_transaction_id = result_states['data'][0]['transactions'][0]['id']
        results = self.sw6_client.request_post(f"_action/order_transaction/{order_transaction_id}/state/{action_name}")
        return results

    def patch_api_change_order_delivery_state(self, order_id, action_name):
        result_states = self.get_api_order_details_transactions_and_deliveries_by_order_id(id=order_id)
        order_delivery_id = result_states['data'][0]['deliveries'][0]['id']
        results = self.sw6_client.request_post(f"_action/order_delivery/{order_delivery_id}/state/{action_name}")
        return results


    """ 
    Getter and Setter
    """
    def get_api_id(self, sw6_json_data):
        try:
            return sw6_json_data["id"]
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der API-ID: {e}")
            return None

    def get_description(self, sw6_json_data):
        try:
            return sw6_json_data["customerComment"]
        except Exception as e:
            self.log(f"Fehler beim Abrufen der Beschreibung: {e}")
            return None

    def get_total_price(self, sw6_json_data):
        try:
            return sw6_json_data["price"]["totalPrice"]
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen des Gesamtpreises: {e}")
            return None

    def get_total_tax(self, sw6_json_data):
        try:
            return sw6_json_data["price"]["calculatedTaxes"]["tax"]
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Gesamtsteuer: {e}")
            return None

    def get_shipping_costs(self, sw6_json_data):
        try:
            return sw6_json_data["shippingCosts"]["totalPrice"]
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Versandkosten: {e}")
            return None

    def get_payment_method(self, sw6_json_data):
        try:
            return sw6_json_data["transactions"][0]["paymentMethod"]["distinguishableName"]
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Zahlungsmethode: {e}")
            return None

    def get_shipping_method(self, sw6_json_data):
        try:
            return sw6_json_data["deliveries"][0]["shippingMethod"]["name"]
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Versandmethode: {e}")
            return None

    def get_order_number(self, sw6_json_data):
        try:
            return sw6_json_data["orderNumber"]
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Bestellnummer: {e}")
            return None

    def get_order_state(self, sw6_json_data):
        try:
            return sw6_json_data["stateMachineState"]["technicalName"]
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen des Bestellstatus: {e}")
            return None

    def get_shipping_state(self, sw6_json_data):
        try:
            return sw6_json_data["deliveries"][0]["stateMachineState"]["technicalName"]
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen des Versandstatus: {e}")
            return None

    def get_payment_state(self, sw6_json_data):
        try:
            return sw6_json_data["transactions"][0]["stateMachineState"]["technicalName"]
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen des Zahlungsstatus: {e}")
            return None

    def get_purchase_date(self, sw6_json_data):
        try:
            date_string = sw6_json_data["orderDateTime"]
            date_object = datetime.fromisoformat(date_string)
            return date_object
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen des Kaufdatums: {e}")
            return None

