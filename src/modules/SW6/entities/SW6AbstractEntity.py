from pprint import pprint
from config import SW6Config

from ..SW6CoreController import SW6CoreController
from lib_shopware6_api_base import Shopware6AdminAPIClientBase, Criteria, EqualsFilter

from config import ConfShopware6ApiBase as SW6Config


class SW6AbstractEntity(SW6CoreController):

    def __init__(self, endpoint_name):
        super().__init__()
        # SW6Config is my config with the same Attributes
        self.sw6_client = Shopware6AdminAPIClientBase(config=SW6Config)
        self._endpoint_name = endpoint_name
        self._criteria = Criteria()
        self.config_sw6 = SW6Config()

    def get_api_(self, id):
        result = self.sw6_client.request_get(f"/{self._endpoint_name}/{id}")
        return result

    def get_api_list(self):
        result = self.sw6_client.request_get(f"/{self._endpoint_name}")
        return result

    def patch_customer_number_by_customer_id(self, customer_id, new_customer_nr):
        payload = {'customerNumber': new_customer_nr}
        result = self.sw6_client.request_patch(f"/{self._endpoint_name}/{customer_id}", payload=payload)
        return result

    def search_api_by_(self, index_field=None, search_value=None):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field=index_field, value=search_value))
        endpoint = self.sw6_client.request_post(f"/search/{self._endpoint_name}", payload=payload)
        return endpoint

    def search_api_ids_by_(self, index_field=None, search_value=None):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field=index_field, value=search_value))
        endpoint = self.sw6_client.request_post(f"search-ids/{self._endpoint_name}", payload=payload)
        return endpoint

    """
    Getter and Setter
    """
    def get_id(self, data):
        return data["id"]
