from datetime import datetime

from ..entities.SW6AbstractEntity import SW6AbstractEntity
from src.modules.Bridge.entities.BridgeMarketplaceEntity import BridgeMarketplaceEntity
from lib_shopware6_api_base import Criteria, EqualsFilter


class SW6MarketplaceEntity(SW6AbstractEntity):

    def __init__(self):
        self.endpoint_name = "sales-channel"
        super().__init__(endpoint_name=self.endpoint_name)

    def map_sw6_to_bridge(self, sw6_json_data):
        try:
            bridge_marketplace_entity_new = BridgeMarketplaceEntity(
                name=self.get_name(sw6_json_data),
                description=self.get_description(sw6_json_data),
                url=self.get_url(sw6_json_data),
                api_key=self.get_api_key(sw6_json_data),
                api_id=self.get_api_id(sw6_json_data),
                config=self.get_config(sw6_json_data),
                factor=self.get_factor(sw6_json_data),
                created_at=datetime.now(),
                edited_at=datetime.now(),
            )

            return bridge_marketplace_entity_new
        except Exception as e:
            self.logger.error(f"SW6 Order could not be mapped to BridgeOrderEntity: {e}")

    def get_api_saleschannel_details_by_saleschannel_id(self, id):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field='id', value=id))

        endpoint = self.sw6_client.request_post(f"/search/{self._endpoint_name}", payload=payload)
        return endpoint

    def get_api_marketplace_details_by_marketplace_id(self, id):
        """
        Just in case i mixe up the titles marketplace and saleschannel
        Why not have alternate name for the same method.
        """
        return self.get_api_saleschannel_details_by_saleschannel_id(id)

    def get_name(self, sw6_json_data):
        return sw6_json_data['name']

    def get_description(self, sw6_json_data):
        return sw6_json_data['homeMetaDescription']

    def get_url(self, sw6_json_data):
        if sw6_json_data['seoUrls']:
            return sw6_json_data['seoUrls'][0]

    def get_api_key(self, sw6_json_data):
        return sw6_json_data["accessKey"]

    def get_api_id(self, sw6_json_data):
        return sw6_json_data["id"]

    def get_config(self, sw6_json_data):
        # Config is set manually
        return None

    def get_factor(self, sw6_json_data):
        # Factor is set manually
        return None