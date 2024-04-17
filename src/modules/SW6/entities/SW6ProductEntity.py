from pprint import pprint
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
        # Delete the prices
        self.delete_all_prices(product_id=bridge_entity.get_sw6_id())

        sw6_tax_id = self.get_api_tax_id_by_value(bridge_entity.tax.get_key())
        sw6_currency_id = self.get_api_currency_id_by_short_name('EUR')
        payload = {
            "id": bridge_entity.get_sw6_id(),
            "active": True,
            "categories": [{"id": category.sw6_id} for category in bridge_entity.categories],
            "taxId": sw6_tax_id,
            "price": self._payload_add_price(bridge_entity, sw6_tax_id, sw6_currency_id),
            "prices": self._payload_add_prices(bridge_entity, sw6_tax_id, sw6_currency_id),
            "productNumber": str(bridge_entity.erp_nr),
            "stock": bridge_entity.get_stock(),
            "name": str(bridge_entity.get_translation().get_name()),
            "description": bridge_entity.get_translation().get_description(),
            "maxPurchase": bridge_entity.get_stock(),
            "minPurchase": bridge_entity.get_min_purchase(),
            "purchaseSteps": bridge_entity.get_purchase_unit(),
            "visibilities": self._payload_add_visibilities(bridge_entity),
            "deliveryTimeId": SW6Config.DELIVERY_TIME['1-2_business_days']
        }

        # Add factor
        # payload = self._payload_add_factor(bridge_entity, payload)

        return payload

    def _payload_add_price(self, bridge_entity, sw6_tax_id, sw6_currency_id):
        # Your existing code that generates a price based on bridge_entity, sw6_tax_id, and sw6_currency_id.
        # For example, it might look like this:
        sales_chanel_de_id = config.SW6Config.SALES_CHANNELS['DE']['id']
        association = BridgeProductMarketplacePriceAssoc.query.filter_by(
            product_id=bridge_entity.id,
            marketplace_id=sales_chanel_de_id
        ).one_or_none()

        return [
            {
                "currencyId": sw6_currency_id,
                "gross": round(association.price.price * bridge_entity.tax.get_key_to_calculate(), 2),
                "net": association.price.price,
                "linked": False,
                # "listPrice":
                #     {
                #         "currencyId": sw6_currency_id,
                #         "gross": round((association.price.price + 100) * bridge_entity.tax.get_key_to_calculate(), 2),
                #         "net": association.price.price + 100,
                #         "linked": False,
                #     }
            }
        ]

    def _payload_add_prices(self, bridge_entity, sw6_tax_id, sw6_currency_id):
        sw6_json_data = []

        for saleschanel in SW6Config.SALES_CHANNELS.values():
            bridge_saleschannel_entity = BridgeMarketplaceEntity.query.filter_by(api_id=saleschanel['id']).one_or_none()

            association = BridgeProductMarketplacePriceAssoc.query.filter_by(
                product_id=bridge_entity.id,
                marketplace_id=bridge_saleschannel_entity.id
            ).one_or_none()

            sw6_json_data.append({
                "id": association.sw6_price_id,
                "quantityStart": 1,
                "quantityEnd": association.price.rebate_quantity if association.price.rebate_quantity else None,
                "ruleId": saleschanel['ruleId'],
                "productId": bridge_entity.get_sw6_id(),
                "price": [
                    {
                        "currencyId": sw6_currency_id,
                        "gross": round(association.price.price * bridge_entity.tax.get_key_to_calculate(), 2),
                        "net": association.price.price,
                        "linked": True,
                        # "listPrice":
                        #     {
                        #         "currencyId": sw6_currency_id,
                        #         "gross": round(
                        #             (association.price.price + 100) * bridge_entity.tax.get_key_to_calculate(), 2),
                        #         "net": association.price.price + 100,
                        #         "linked": True,
                        #     }
                    }
                ]
            })
            if association.price.rebate_quantity:
                sw6_json_data.append({
                    "id": association.sw6_rebate_price_id,
                    "quantityStart": association.price.rebate_quantity + 1,
                    "quantityEnd": None,
                    "ruleId": saleschanel['ruleId'],
                    "productId": bridge_entity.get_sw6_id(),
                    "price": [
                        {
                            "currencyId": sw6_currency_id,
                            "gross": round(association.price.rebate_price * bridge_entity.tax.get_key_to_calculate(),
                                           2),
                            "net": association.price.rebate_price,
                            "linked": True,
                            # "listPrice":
                            #     {
                            #         "currencyId": sw6_currency_id,
                            #         "gross": round((
                            #             association.price.rebate_price + 100) * bridge_entity.tax.get_key_to_calculate(),
                            #             2),
                            #         "net": association.price.rebate_price + 100,
                            #         "linked": True,
                            #     }
                        }
                    ],
                })

        return sw6_json_data

    def _payload_add_factor(self, bridge_entity, payload):
        if bridge_entity.get_factor():
            payload["customFields"]["geco_price_factor_value"] = bridge_entity.get_factor()
            return payload

    def _payload_add_visibilities(self, bridge_entity):
        visibilities = []

        for saleschannel in SW6Config.SALES_CHANNELS.values():

            bridge_saleschannel_entity = BridgeMarketplaceEntity.query.filter_by(
                api_id=saleschannel['id']).one_or_none()

            if bridge_saleschannel_entity:
                bridge_marketplace_entity = BridgeProductMarketplacePriceAssoc.query.filter_by(
                    marketplace_id=bridge_saleschannel_entity.id,
                    product_id=bridge_entity.id
                ).one_or_none()

                if bridge_marketplace_entity:
                    visibilities.append({
                        "id": bridge_marketplace_entity.sw6_visibility_id,
                        "productId": bridge_entity.get_sw6_id(),
                        "salesChannelId": saleschannel['id'],
                        "visibility": 30,
                    })

        return visibilities

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

    def get_api_tax_id_by_value(self, value=19):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field="taxRate", value=value))
        result = self.sw6_client.request_post(f"/search/tax", payload=payload)
        if result['total'] == 0:
            self.logger.error(f"No tax rate of {value} was found!")
        elif result['total'] > 1:
            self.logger.error(
                f"There should only be one tax with a taxRate of {value}, but {result['total']} were found! Delete all other taxes")
        else:
            return result['data'][0]['id']

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

    def set_cover_media(self,bridge_entity, product_media_id):
        payload = {
            "coverId": product_media_id
        }
        self.endpoint_name = 'product'
        self.sw6_client.request_patch(request_url=f"/product/{bridge_entity.get_sw6_id()}", payload=payload)