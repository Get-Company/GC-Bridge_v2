from datetime import datetime
from pprint import pprint

import requests
from lib_shopware6_api_base import Criteria, EqualsFilter

import config
from config import SW6Config

from ..entities.SW6AbstractEntity import SW6AbstractEntity
from ..entities.SW6CategoryEntity import SW6CategoryEntity
from src.modules.Bridge.entities.BridgeProductEntity import BridgeProductEntity
from src.modules.Bridge.entities.BridgeMarketplaceEntity import BridgeMarketplaceEntity, \
    BridgeProductMarketplacePriceAssoc


class SW6ProductEntity(SW6AbstractEntity):
    def __init__(self):
        self.endpoint_name = "product"
        super().__init__(endpoint_name=self.endpoint_name)

    def map_sw6_to_bridge(self):
        """ No need to map the Product sw6 to hte bridge"""
        pass

    def map_bridge_to_sw6(self, bridge_entity):
        """
        Maps a bridge entity to SW6 with the relevant attributes such as price, name, description and more.
        This includes deleting the prices, getting currency ID, tax ID and preparing the payload accordingly.

        Parameters:
        bridge_entity (class): A Bridge Entity that would be used to form the payload.

        Returns:
        payload (dict): Returns a dictionary which contains the payload structured according to SW6 requirements
        """
        # Initialize payload
        payload = {}
        try:
            try:
                # Get ID details from SW6 Instance
                sw6_tax_id = self.get_tax_id_by_value(bridge_entity.tax.get_key())
            except Exception as e:
                self.logger.error("An error occurred while getting tax ID: %s", str(e))
                raise

            try:
                sw6_currency_id = self.get_api_currency_id_by_short_name('EUR')
            except Exception as e:
                self.logger.error("An error occurred while getting currency ID: %s", str(e))
                raise

            try:
                # Prepare payload dictionary
                payload = {
                    "id": bridge_entity.get_sw6_id(),
                    "active": bridge_entity.get_is_active(),
                    "categories": [{"id": category.sw6_id} for category in bridge_entity.categories],
                    "customFields": self._add_custom_fields(bridge_entity),
                    "taxId": sw6_tax_id,
                    "price": self._payload_add_price(bridge_entity, sw6_tax_id, sw6_currency_id),
                    "prices": self._payload_add_prices(bridge_entity, sw6_tax_id, sw6_currency_id),
                    "productNumber": str(bridge_entity.erp_nr),
                    "stock": bridge_entity.get_stock(),
                    "name": str(bridge_entity.get_translation().get_name()),
                    "description": str(bridge_entity.get_translation().get_description()),
                    "maxPurchase": bridge_entity.get_stock(),
                    "minPurchase": bridge_entity.get_min_purchase(),
                    "purchaseSteps": bridge_entity.get_purchase_unit(),
                    "visibilities": self._payload_add_visibilities(bridge_entity),
                    "deliveryTimeId": SW6Config.DELIVERY_TIME['1-2_business_days']
                }
            except Exception as e:
                self.logger.error("An error occurred while preparing payload: %s", str(e))
                raise

            try:
                # Remove previous prices
                self.delete_all_prices(product_id=bridge_entity.get_sw6_id())
            except Exception as e:
                self.logger.error("An error occurred while deleting all prices: %s", str(e))
                raise

        except Exception as e:
            self.logger.error("An error occurred in map_bridge_to_sw6: %s", str(e))

        return payload

    def _payload_add_price(self, bridge_entity, sw6_tax_id, sw6_currency_id):
        sales_chanel_de_id = config.SW6Config.SALES_CHANNELS['DE']['id']
        association = BridgeProductMarketplacePriceAssoc.query.filter_by(
            product_id=bridge_entity.id,
            marketplace_id=sales_chanel_de_id
        ).one_or_none()

        if association.price.is_special_price_active():
            # If special price is active, set the listPrice as the original price,
            # and the new 'price' as the special price
            price_payload = {
                "currencyId": sw6_currency_id,
                "gross": round(association.price.special_price * bridge_entity.tax.get_key_to_calculate(), 2),
                "net": association.price.special_price,
                "linked": False,
                "listPrice": {
                    "currencyId": sw6_currency_id,
                    "gross": round(association.price.price * bridge_entity.tax.get_key_to_calculate(), 2),
                    "net": association.price.price,
                    "linked": False,
                }
            }
        else:
            # If special price is not active, set the 'price' as the original price
            price_payload = {
                "currencyId": sw6_currency_id,
                "gross": round(association.price.price * bridge_entity.tax.get_key_to_calculate(), 2),
                "net": association.price.price,
                "linked": False
            }

        return [price_payload]

    def _payload_add_prices(self, bridge_entity, sw6_tax_id, sw6_currency_id):
        """
        This method generates and returns a payload containing prices for each sales channel of a product.
        The payload includes consideration for special prices and rebate prices.

        Args:
            bridge_entity (BridgeEntity): The entity that holds the product details.
            sw6_tax_id (str): The tax ID related to the product.
            sw6_currency_id (str): The currency ID related to the product.

        Returns:
            list: A list consisting of dictionaries. Each dictionary corresponds to a sales channel and contains
            the price details for that sales channel.
        """

        # Initialize an empty list where each dictionary will contain price details for a sales channel
        sw6_json_data = []

        # Iterate over each sales channel
        for saleschannel in SW6Config.SALES_CHANNELS.values():
            try:
                # Retrieve the BridgeMarketplaceEntity associated with the current sales channel for the current product
                bridge_saleschannel_entity = BridgeMarketplaceEntity.query.filter_by(
                    api_id=saleschannel['id']).one_or_none()

                # Retrieve the BridgeProductMarketplacePriceAssoc association for the current product and marketplace
                association = BridgeProductMarketplacePriceAssoc.query.filter_by(
                    product_id=bridge_entity.id,
                    marketplace_id=bridge_saleschannel_entity.id
                ).one_or_none()

                # Calculate the current price and gross price
                current_price = association.price.price
                current_price_gross = round(association.price.price * bridge_entity.tax.get_key_to_calculate(), 2)

                # By default, listPrice is not set, and special price status is inactive
                listPrice = None
                special_price_active = False

                # Get the current date
                today = datetime.date(datetime.now())

                # Check for valid special price and date range
                if association.price.special_price is not None and \
                        association.price.special_start_date.date() <= today <= association.price.special_end_date.date():
                    # If valid, update current price and gross price based on special price; update listPrice and mark special price as active
                    current_price = association.price.special_price
                    current_price_gross = round(current_price * bridge_entity.tax.get_key_to_calculate(), 2)
                    listPrice = {
                        "currencyId": sw6_currency_id,
                        "gross": round(association.price.price * bridge_entity.tax.get_key_to_calculate(), 2),
                        "net": association.price.price,
                        "linked": True,
                    }
                    special_price_active = True

                # Prepare the price payload for the current sales channel
                each_channel = {
                    "id": association.sw6_price_id,
                    "productId": bridge_entity.get_sw6_id(),
                    "ruleId": saleschannel['ruleId'],
                    "quantityStart": 1,
                    "quantityEnd": association.price.rebate_quantity if association.price.rebate_quantity else None,
                    "price": [
                        {
                            "currencyId": sw6_currency_id,
                            "gross": current_price_gross,
                            "net": current_price,
                            "linked": True,
                        }
                    ]
                }

                # If a listPrice exists (indicating a special price is active), append it to the 'price' list in the dictionary
                if listPrice is not None:
                    each_channel['price'][0].update({"listPrice": listPrice})

                # Add the dictionary to the sw6_json_data list
                sw6_json_data.append(each_channel)

                # If a rebate quantity exists and special price is not active, generate a price payload for the rebate price and add it to sw6_json_data
                if association.price.rebate_quantity and not special_price_active:
                    sw6_json_data.append({
                        "id": association.sw6_rebate_price_id,
                        "productId": bridge_entity.get_sw6_id(),
                        "ruleId": saleschannel['ruleId'],
                        "quantityStart": association.price.rebate_quantity + 1,
                        "quantityEnd": None,
                        "price": [
                            {
                                "currencyId": sw6_currency_id,
                                "gross": round(
                                    association.price.rebate_price * bridge_entity.tax.get_key_to_calculate(),
                                    2),
                                "net": association.price.rebate_price,
                                "linked": True
                            }
                        ]
                    })

            except Exception as e:
                # Log exceptions with a helpful message
                self.logger.error(
                    f"Error occurred while generating price payload for sales channel {saleschannel['id']}: {str(e)}")

        return sw6_json_data

    def _payload_add_visibilities(self, bridge_entity):
        """
        Method to add visibilities to the payload.

        This method traverses through the SALES_CHANNELS from SW6Config. It then constructs a visibility object
        for every matching bridge entity found in the marketplace, and appends it to a list.

        Args:
            bridge_entity (bridge_entity): Bridge entity to be used in filter condition.

        Returns:
            list: List of visibility objects.
        """
        visibilities = []
        try:
            for saleschannel in SW6Config.SALES_CHANNELS.values():  # for each sales channel

                # querying BridgeMarketplaceEntity for matching API ID
                bridge_saleschannel_entity = BridgeMarketplaceEntity.query.filter_by(
                    api_id=saleschannel['id']).one_or_none()

                if bridge_saleschannel_entity:  # if entity exists

                    # query BridgeProductMarketplacePriceAssoc for matching marketplace ID and product ID
                    bridge_marketplace_entity = BridgeProductMarketplacePriceAssoc.query.filter_by(
                        marketplace_id=bridge_saleschannel_entity.id,
                        product_id=bridge_entity.id
                    ).one_or_none()

                    if bridge_marketplace_entity and bridge_marketplace_entity.get_is_active() == 1:  # if marketplace entity exists
                        # append visibility object to visibilities list
                        visibilities.append({
                            "id": bridge_marketplace_entity.sw6_visibility_id,
                            "productId": bridge_entity.get_sw6_id(),
                            "salesChannelId": saleschannel['id'],
                            "visibility": 30,
                        })
            return visibilities
        except Exception as e:  # catch exceptions
            self.logger.error(f'Error in _payload_add_visibilities: {e}')  # log error

    def _payload_add_medias(self, bridge_entity):
        medias = []

        if bridge_entity.media_assocs:
            for index, media_assoc in enumerate(bridge_entity.media_assocs):
                media = media_assoc.media
                media_dict = {
                    "id": bridge_entity.get_sw6_media_id(),
                    "media": {
                        "id": media.get_sw6_id(),
                        "position": media_assoc.sort * 10
                    }
                }
                medias.append(media_dict)

        return medias

    def _add_custom_fields(self, bridge_entity):
        """
        Add all custom fields to the payload for the SW6 entity.

        :param bridge_entity: The bridge_entity object that needs custom fields
        :returns: A dictionary of custom fields for the SW6 entity
        """

        # Create the customFields dictionary
        custom_fields_payload = {}

        # Try to add specific fields
        try:
            custom_fields_payload.update(self._payload_add_custom_fields_factor(bridge_entity))
            custom_fields_payload.update(self._payload_add_custom_fields_attr18(bridge_entity))
        except Exception as e:
            self.logger.error(f"Error while adding factor-based custom field: {str(e)}")

        # TODO: Add more custom fields here as needed...

        return custom_fields_payload

    def _payload_add_custom_fields_factor(self, bridge_entity):
        """
        Add a factor-based custom field to the SW6 entity's custom fields.

        :param bridge_entity: The bridge_entity object which provides factor information
        :returns: A dictionary of a factor-based custom field for the SW6 entity
        """

        # Create the customFields dictionary
        custom_field = {}

        # Add the factor value
        try:
            custom_field['geco_price_factor_value'] = 1
            if bridge_entity.get_factor():
                custom_field['geco_price_factor_value'] = bridge_entity.get_factor()

        except Exception as e:
            self.logger.error(f"Error while extracting factor value from bridge entity: {str(e)}")

        return custom_field

    def _payload_add_custom_fields_attr18(self, bridge_entity):
        """
        Add the sort/position based custom field 'attr18' to the SW6 entity's custom fields.

        :param bridge_entity: The bridge_entity object which provides sort/position information.
        :returns: A dictionary containing the 'attr18' custom field for the SW6 entity.
        """

        # Create the customFields dictionary
        custom_fields = {}

        try:
            # Add the attr18 value if available in bridge_entity
            if bridge_entity.get_sort():
                custom_fields['attr18'] = bridge_entity.get_sort()
            else:
                custom_fields['attr18'] = 0  # Default value if sort is not available
        except Exception as e:
            self.logger.error(f"Error while extracting attr18 value from bridge entity: {str(e)}")

        return custom_fields

    def get_tax_id_by_value(self, value=19):
        """
        Returns the tax id related to the provided value from the SW6Config class.

        Args:
            value (int): The value to get the tax id for. Defaults to 19.

        Returns:
            str: The tax id related to the provided value or default tax id if the value tax id is not found.
        """
        try:
            # Fetch the tax id from the SW6Config class. If not found, return the default tax id
            return SW6Config.TAX.get(value, SW6Config.TAX[value])

        except Exception as e:
            # Logs any encountered error
            print(f"An error occurred while getting tax id: {str(e)}. Standard ID will be used: {SW6Config.TAX[19]}")

            # Return default tax id if exception occurs
            return SW6Config.TAX[19]

    def get_api_currency_id_by_short_name(self, short_name='EUR'):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field="shortName", value=short_name))
        result = self.sw6_client.request_post(f"/search/currency", payload=payload)
        if result['total'] == 0:
            pprint(f"No currency with short name of '{short_name}' was found!")
        elif result['total'] > 1:
            pprint(
                f"There should only be one currency with a short name of '{short_name}', but {result['total']} were found! Delete all other currencies")
        else:
            return result['data'][0]['id']

    def get_details(self, id):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field='id', value=id))

        payload.associations["prices"] = Criteria()
        payload.associations["customFieldSets"] = Criteria()
        payload.associations["media"] = Criteria()

        result = self.sw6_client.request_post(f"/search/{self.endpoint_name}", payload=payload)

        return result

    def get_visibilities(self, product_id):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field='productId', value=product_id))

        result = self.sw6_client.request_post(f"/search/product-visibility", payload=payload)

        return result

    def delete_visibility(self, visibility_id):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field='id', value=visibility_id))

        result = self.sw6_client.request_post(f"/search-ids/product-visibility", payload=payload)
        pprint(result)
        if result['total'] > 0:
            for visibility_id in result['data']:
                print(f"Deleting {visibility_id}")
                delete_result = self.sw6_client.request_delete(f"product-visibility/{visibility_id}")
                pprint(delete_result)

        return True

    def get_customfield(self, custom_field_id):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field='id', value=custom_field_id))

        result = self.sw6_client.request_post(f"/search/custom-field", payload=payload)

        return result

    def delete_price(self, price_id):
        try:
            payload = Criteria()
            payload.filter.append(EqualsFilter(field='id', value=price_id))
            found = self.sw6_client.request_post(f"/search/product-price", payload=payload)
            if found['total'] == 1:
                result = self.sw6_client.request_delete(f"/product-price/{price_id}")
            elif found['total'] == 0:
                self.logger.warning(
                    f"No corresponding price found for id: {price_id}. If this is the init of a new product - no problem. No price in db.")
            else:
                self.logger.error(f"Multiple prices found for a single id: {price_id}. Indicates an error in SW6.")
                raise Exception("Multiple prices found for a single id")
        except Exception as e:
            self.logger.warning(f"Error while finding/deleting price: {e}")

    def delete_all_prices(self, product_id):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field='productId', value=product_id))

        result_search = self.sw6_client.request_post(f"/search-ids/product-price", payload=payload)
        # pprint(result_search)

        if result_search['total'] > 0:
            for price_id in result_search['data']:
                result_delete = self.sw6_client.request_delete(f"/product-price/{price_id}")
                # pprint(result_delete)

    def set_cover_media(self, bridge_entity, product_media_id):
        payload = {
            "coverId": product_media_id
        }
        self.endpoint_name = 'product'
        self.sw6_client.request_patch(request_url=f"/product/{bridge_entity.get_sw6_id()}", payload=payload)

    def set_status(self, bridge_entity):
        payload = {
            "active": bridge_entity.get_is_active()
        }

        result = self.sw6_client.request_patch(
            f"/{self.endpoint_name}/{bridge_entity.get_sw6_id()}",
            payload=payload,
            additional_query_params={"_response": "detail"})
        return result
