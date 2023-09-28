import json

import requests

from ..SW6CoreController import SW6CoreController
from ..controller.SW6ConnectionController import SW6ConnectionController


class QueryCriteria:
    def __init__(self, filter=None, sort=None, limit=None):
        self.filter = filter or {}
        self.sort = sort or []
        self.limit = limit


class SW6AbstractEntity(SW6CoreController):
    def __init__(self, endpoint_name):
        super().__init__()
        self.sw6_api = SW6ConnectionController()
        self.config = self.sw6_api.config
        self.request = self.sw6_api.request
        self.endpoint_name = None
        self.set_endpoint_name(endpoint_name=endpoint_name)
        self.endpoint_name = endpoint_name
        # Filter
        self._filter = None

    def set_endpoint_name(self, endpoint_name):
        self.endpoint_name = endpoint_name

    def get_endpoint_name(self):
        if not self.endpoint_name:
            return False
        else:
            return self.endpoint_name

    def set_filter(self, type, field, value):
        self._filter = {
            "filter": [
                {
                    "type": type,
                    "fields": field,
                    "value": value
                }
            ]
        }

    def get(self, id):
        """Retrieves an entity by its ID from the specified endpoint.

        Args:
            id (str): The ID of the entity to retrieve.

        Returns:
            dict: The JSON response from the API.
        """
        method = "GET"
        url = f'{self.config.SHOP_URL}/api/{self.endpoint_name}/{id}'
        self.logger.info(f'Trying to "{method}" {self.endpoint_name} "{id}" from URL "{url}"')
        try:
            response = self.request(method, url)
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"Failed to {method} {self.endpoint_name}: {e}")
            raise
        return response.json()

    def get_list(self):
        """Retrieves an entity by its ID from the specified endpoint.

        Args:
            id (str): The ID of the entity to retrieve.

        Returns:
            dict: The JSON response from the API.
        """
        method = "POST"
        url = f'{self.config.SHOP_URL}/api/{self.endpoint_name}'
        self.logger.info(f'Trying to "{method}" {self.endpoint_name} List from URL "{url}"')
        try:
            response = self.request(method, url)
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"Failed to {method} {self.endpoint_name}: {e}")
            raise
        return response.json()

    def create(self, data):
        """Creates a new entity at the specified endpoint.

        Args:
            data (dict): The data for the new entity.

        Returns:
            dict: The JSON response from the API.
        """
        method = "POST"
        url = f'{self.config.SHOP_URL}/api/{self.endpoint_name}'
        self.logger.info(f'Trying to "{method}" {self.endpoint_name} with data "{data}" to URL "{url}"')
        try:
            response = self.request(method, url, json=data)
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"Failed to {method} {self.endpoint_name}: {e}")
            raise
        return response.json()

    def update(self, id, data):
        """Updates an existing entity by its ID at the specified endpoint.

        Args:
            id (str): The ID of the entity to update.
            data (dict): The updated data for the entity.

        Returns:
            dict: The JSON response from the API.
        """
        method = "PUT"
        url = f'{self.config.SHOP_URL}/api/{self.endpoint_name}/{id}'
        self.logger.info(f'Trying to "{method}" {self.endpoint_name} "{id}" with data "{data}" to URL "{url}"')
        try:
            response = self.session.request(method, url, json=data)
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"Failed to {method} {self.endpoint_name}: {e}")
            raise
        return response.json()

    def delete(self, id):
        """Deletes an existing entity by its ID from the specified endpoint.

        Args:
            id (str): The ID of the entity to delete.

        Returns:
            dict: The JSON response from the API.
        """
        method = "DELETE"
        url = f'{self.config.SHOP_URL}/api/{self.endpoint_name}/{id}'
        self.logger.info(f'Trying to "{method}" {self.endpoint_name} "{id}" from URL "{url}"')
        try:
            response = self.session.request(method, url)
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"Failed to {method} {self.endpoint_name}: {e}")
            raise
        return response.json()

    def search(self, filter=None, sort=None, post_filter=None, associations=None, aggregations=None):
        pass

    def get_categories_by_filter(self, filter_payload=None):
        """Retrieves categories based on the specified filter.

        Args:
            filter_payload (dict): The filter payload for the query.

        Returns:
            dict: The JSON response from the API.
        """
        # Construct the URL for the category endpoint
        url = f'{self.config.SHOP_URL}/api/{self.endpoint_name}'
        # Log the URL and the filter payload
        filter_payload = {
            "filter": [
                {
                    "type": "equals",
                    "field": "id",
                    "value": "e2f18bf14dd54320952d73a0af868dde"
                }
            ]
        }
        print(f'Trying to POST to {url} with filter: {json.dumps(filter_payload)}')
        try:
            # Send a POST request with the filter payload as the JSON body
            response = self.request(method="POST", url=url, json=filter_payload)
            print(response.json())
            # Check for HTTP errors
            response.raise_for_status()
        except requests.RequestException as e:
            print(f'Failed to POST to {url}: {e}')
            raise
        # Parse and return the JSON response
        return response.json()
