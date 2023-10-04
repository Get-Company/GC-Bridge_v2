from pprint import pprint

from ..SW6CoreController import SW6CoreController
from lib_shopware6_api_base import Shopware6AdminAPIClientBase, Criteria, EqualsFilter
from config import ConfShopware6ApiBase as SW6Config


class SW6AbstractEntity(SW6CoreController):

    def __init__(self, endpoint_name):
        super().__init__()
        # SW6Config is my config with the same Attributes
        self.sw6_client = Shopware6AdminAPIClientBase(config=SW6Config)
        self._endpoint_name = endpoint_name

    def request(self):
        id = 'e2f18bf14dd54320952d73a0af868dde'
        category = self.sw6_client.request_get(f"/category/{id}")
        pprint(category)

    def get_(self, id):
        endpoint = self.sw6_client.request_get(f"/{self._endpoint_name}/{id}")
        return endpoint

    def search_by_(self, index_field=None, search_value=None):
        payload = Criteria()
        payload.filter.append(EqualsFilter(index_field, search_value))
        endpoint = self.sw6_client.request_post(f"/search/{self._endpoint_name}", payload=payload)
        return endpoint






    """     
    Abstract Methods, defined in ModulesCoreController
    These Methods must be overwritten. If there is no use of it simply do a pass!
    """
    def sync_all_to_bridge(self):
        pass

    def sync_all_from_bridge(self):
        pass

    def sync_one_to_bridge(self):
        pass

    def sync_one_from_bridge(self):
        pass

    def sync_changed_to_bridge(self):
        pass

    def sync_changed_from_bridge(self):
        pass
