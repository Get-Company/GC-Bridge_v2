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
                unit_price=self.get_unit_price(sw6_json_data),
                total_price=self.get_total_price(sw6_json_data),
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

    def get_unit_price(self, sw6_json_data):
        """
        Calculate the net unit price of a product.

        This function calculates the net unit price based on the calculated taxes
        and tax rules if both are present in the product object.

        If the 'calculatedTaxes' field is not present in the product object,
        it will return the unit price directly.

        :param product: A JSON object which represents a product and potentially has the following fields:
                        - calculatedTaxes: A boolean field specifying whether the prices are calculated with taxes.
                        - taxRules: A list wherein the first element's 'taxRate' field is used to calculate net prices.
                        - unitPrice: The unit price of the product.
        :return: The net unit price if the required fields are present, otherwise, the unit price.
        B2B Customer Data:
        sw6_json_data = {
            'price': {
                'apiAlias': 'calculated_price',
                'calculatedTaxes': [],
                'extensions': [],
                'listPrice': {
                    'apiAlias': 'cart_list_price',
                    'discount': -5.976890756303,
                    'extensions': [],
                    'percentage': 8.89,
                    'price': 67.226890756303
                },
                'quantity': 100,
                'referencePrice': None,
                'regulationPrice': None,
                'taxRules': [],
                'totalPrice': 6125,
                'unitPrice': 61.25
            }
        }
        B2C Customer Data:
        sw6_json_data = {
            'price': {
                'apiAlias': 'calculated_price',
                'calculatedTaxes': [{
                    'apiAlias': 'cart_tax_calculated',
                    'extensions': [],
                    'price': 7551,
                    'tax': 1205.62,
                    'taxRate': 19
                }],
                'extensions': [],
                'listPrice': {
                    'apiAlias': 'cart_list_price',
                    'discount': -4.49,
                    'extensions': [],
                    'percentage': 5.61,
                    'price': 80
                },
                'quantity': 100,
                'referencePrice': None,
                'regulationPrice': None,
                'taxRules': [{
                    'apiAlias': 'cart_tax_rule',
                    'extensions': [],
                    'percentage': 100,
                    'taxRate': 19
                }],
                'totalPrice': 7551,
                'unitPrice': 75.51
            }
        }
        """
        try:
            # Check if 'calculatedTaxes' and 'taxRules' fields are in the Json data and are not empty
            if 'calculatedTaxes' in sw6_json_data and sw6_json_data['taxRules']:
                # Get the tax rate from the first element of the 'taxRules' field
                tax_rate = sw6_json_data['taxRules'][0]['taxRate']
                brutto_unit_price = sw6_json_data['unitPrice']
                # Calculate the net unit price based on the tax rate
                netto_unit_price = brutto_unit_price / (1 + tax_rate / 100)
                return round(netto_unit_price, 2)
            else:
                # Return the brutto unit price directly if 'calculatedTaxes' field is not present in the product object
                return sw6_json_data['unitPrice']
        except Exception as e:
            # Log the error and return None if there was an error during calculation
            self.logger.error(f"Error calculating price: {e}")
            return None

    def get_total_price(self, sw6_json_data):
        """
        Calculate the net total price of a product.

        This function calculates the net total price based on the calculated taxes,
        tax rules, unit price and quantity if all are present in the product object.

        If the 'calculatedTaxes' field is not present in the product object,
        it will return the total price directly.

        :param product: A JSON object which represents a product and has the following fields:
                        - calculatedTaxes: A boolean field specifying whether the prices are calculated with taxes.
                        - taxRules: A list wherein the first element's 'taxRate' field is used to calculate net prices.
                        - unitPrice: The unit price of the product.
                        - quantity: The quantity of the product.
                        - totalPrice: The total price of the product.
        :return: The net total price if the required fields are present, otherwise, the total price.

        B2B Customer Data:
        sw6_json_data = {
            'price': {
                'apiAlias': 'calculated_price',
                'calculatedTaxes': [],
                'extensions': [],
                'listPrice': {
                    'apiAlias': 'cart_list_price',
                    'discount': -5.976890756303,
                    'extensions': [],
                    'percentage': 8.89,
                    'price': 67.226890756303
                },
                'quantity': 100,
                'referencePrice': None,
                'regulationPrice': None,
                'taxRules': [],
                'totalPrice': 6125,
                'unitPrice': 61.25
            }
        }
        B2C Customer Data:
        sw6_json_data = {
            'price': {
                'apiAlias': 'calculated_price',
                'calculatedTaxes': [{
                    'apiAlias': 'cart_tax_calculated',
                    'extensions': [],
                    'price': 7551,
                    'tax': 1205.62,
                    'taxRate': 19
                }],
                'extensions': [],
                'listPrice': {
                    'apiAlias': 'cart_list_price',
                    'discount': -4.49,
                    'extensions': [],
                    'percentage': 5.61,
                    'price': 80
                },
                'quantity': 100,
                'referencePrice': None,
                'regulationPrice': None,
                'taxRules': [{
                    'apiAlias': 'cart_tax_rule',
                    'extensions': [],
                    'percentage': 100,
                    'taxRate': 19
                }],
                'totalPrice': 7551,
                'unitPrice': 75.51
            }
        }
        """

        try:
            # Check if there is 'calculatedTaxes' field in the 'price' field
            # and if it's not empty
            if 'calculatedTaxes' in sw6_json_data and sw6_json_data['taxRules']:
                # Calculate the net unit price
                netto_unit_price = self.get_unit_price(sw6_json_data=sw6_json_data)
                # Get the quantity from the product object
                quantity = sw6_json_data['quantity']
                # Calculate the net total price based on the net unit price and quantity
                netto_total_price = netto_unit_price * quantity
                return round(netto_total_price, 2)
            else:
                # Return the bruto total price directly if 'calculatedTaxes' is not present in the product object
                return sw6_json_data['totalPrice']
        except Exception as e:
            # Log the error and return None if there was an error during calculation
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
        """
        This function retrieves the tax amount based on the order line item data from Shopware 6.
        If the tax data is not found or is empty, the function will return None.

        :param sw6_json_data: dict, Order line item data from Shopware 6
        :return: float, the tax amount. None if the tax data was not found or an error occurred.

        #Example usage:

        sw6_json_data = {
            'price': {
                'calculatedTaxes': [{
                    'tax': 1205.62
                    # other fields...
                }]
                # other fields...
            }
            # other fields...
        }

        tax_amount = get_tax(sw6_json_data)
        print(tax_amount)  # prints: 1205.62
        """
        try:
            # Check if there is 'calculatedTaxes' field in the 'price' field
            # and if it's not empty
            if 'calculatedTaxes' in sw6_json_data['price'] and sw6_json_data['price']['calculatedTaxes']:
                # If it exists and not empty, get the first item's 'tax'
                tax_amount = sw6_json_data['price']['calculatedTaxes'][0]['tax']
            else:
                # If 'calculatedTaxes' does not exist or is empty,
                # There is no tax amount, returns None
                tax_amount = None
            return tax_amount
        except Exception as e:
            # Log the error and return None if there was an error
            self.logger.error(f"Error getting tax amount: {e}")
            return None

    def get_api_order_id(self, sw6_json_data):
        try:
            return sw6_json_data['orderId']
        except Exception as e:
            self.logger.error(f"Error getting order ID: {e}")
            return None
