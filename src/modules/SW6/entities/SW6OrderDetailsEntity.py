from datetime import datetime
from pprint import pprint

from ..entities.SW6AbstractEntity import SW6AbstractEntity
from src.modules.Bridge.entities.BridgeOrderDetailsEntity import BridgeOrderDetailsEntity
from lib_shopware6_api_base import Criteria, EqualsFilter


class SW6OrderDetailsEntity(SW6AbstractEntity):

    def __init__(self):
        self.endpoint_name = "order-line-item"
        super().__init__(endpoint_name=self.endpoint_name)

    def map_sw6_to_bridge(self, sw6_json_data):
        try:
            bridge_order_detail_entity_new = BridgeOrderDetailsEntity(
                erp_nr=self.get_erp_nr(sw6_json_data),
                api_id=self.get_api_id(sw6_json_data),
                api_order_id=self.get_api_order_id(sw6_json_data),
                price=self.get_price(sw6_json_data),
                quantity=self.get_quantity(sw6_json_data),
                name=self.get_name(sw6_json_data),
                tax=self.get_tax(sw6_json_data)
            )
            return bridge_order_detail_entity_new
        except Exception as e:
            self.logger.error(f"SW6 OrderDetail could not be mapped to BridgeOrderDetailsEntity: {e}")

    def get_erp_nr(self, sw6_json_data):
        try:
            return sw6_json_data["payload"]['productNumber']
        except Exception as e:
            self.logger.error(f"Error getting ERP number: {e}")
            return None

    def get_api_id(self, sw6_json_data):
        try:
            return sw6_json_data['id']
        except Exception as e:
            self.logger.error(f"Error getting api_id (ID LineItem): {e}")
            return None

    def get_price(self, sw6_json_data):
        try:
            # Just return the net price - is it really net?
            calculated_price = sw6_json_data['price']['calculatedTaxes'][0]['price']
            calculated_tax = sw6_json_data['price']['calculatedTaxes'][0]['tax']
            net_price = calculated_price - calculated_tax
            return net_price
        except Exception as e:
            self.logger.error(f"Error calculating price: {e}")
            return None

    def get_quantity(self, sw6_json_data):
        try:
            return sw6_json_data['quantity']
        except Exception as e:
            self.logger.error(f"Error getting quantity: {e}")
            return None

    def get_name(self, sw6_json_data):
        try:
            return sw6_json_data['label']
        except Exception as e:
            self.logger.error(f"Error getting name: {e}")
            return None

    def get_tax(self, sw6_json_data):
        try:
            return sw6_json_data['price']['calculatedTaxes'][0]['taxRate']
        except Exception as e:
            self.logger.error(f"Error getting tax rate: {e}")
            return None

    def get_api_order_id(self, sw6_json_data):
        try:
            return sw6_json_data['orderId']
        except Exception as e:
            self.logger.error(f"Error getting order ID: {e}")
            return None




