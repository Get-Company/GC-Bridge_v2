from pprint import pprint

import requests

import config
from config import SW6Config
from abc import abstractmethod
import json

from ..SW6CoreController import SW6CoreController
from lib_shopware6_api_base import Shopware6AdminAPIClientBase, Criteria, EqualsFilter

from config import ConfShopware6ApiBase


class SW6AbstractEntity(SW6CoreController):

    def __init__(self, endpoint_name):
        super().__init__()
        # SW6Config is my config with the same Attributes
        self.sw6_client = Shopware6AdminAPIClientBase(config=ConfShopware6ApiBase)
        self._endpoint_name = endpoint_name
        self._criteria = Criteria()
        self.config_sw6 = config.SW6Config

    def get_api_(self, id):
        try:
            result = self.sw6_client.request_get(f"/{self._endpoint_name}/{id}")
            return result
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 404:
                return None
            else:
                raise

    def get_api_list(self):
        result = self.sw6_client.request_get(f"/{self._endpoint_name}")
        return result

    def search_api_by_(self, index_field=None, search_value=None, endpoint_name=None):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field=index_field, value=search_value))
        # Use endpoint_name parameter if it is provided, otherwise, stick to self._endpoint_name
        endpoint = endpoint_name if endpoint_name else self._endpoint_name
        result = self.sw6_client.request_post(f"/search/{self._endpoint_name}", payload=payload)
        return result

    def search_api_ids_by_(self, index_field=None, search_value=None, endpoint_name=None):
        """
        This method searches API by given index_field and search_value.
        Parameters:
        index_field (str/list): The field(s) to be searched.
        search_value (str/list): The value(s) of the field(s) to be searched.
        Returns:
        Object: API endpoint.
        """
        # Use endpoint_name parameter if it is provided, otherwise, stick to self._endpoint_name
        endpoint = endpoint_name if endpoint_name else self._endpoint_name
        payload = None
        if search_value is not None and index_field is not None:
            try:
                # Create instance of Criteria
                payload = Criteria()
                # If both index_field and search_value are lists of the same length
                if isinstance(index_field, list) and isinstance(search_value, list) and len(index_field) == len(
                        search_value):
                    for idx, val in zip(index_field, search_value):
                        # Append the required filter
                        payload.filter.append(EqualsFilter(field=idx, value=val))
                else:
                    # Append the required filter
                    payload.filter.append(EqualsFilter(field=index_field, value=search_value))
            except Exception as e:
                self.logger.error(f"Error in creating payload: {str(e)}")
                raise e
        try:
            if payload is not None:
                endpoint = self.sw6_client.request_post(f"/search-ids/{endpoint}", payload=payload)
            else:
                endpoint = self.sw6_client.request_post(f"/search-ids/{endpoint}")
        except Exception as e:
            self.logger.error(f"Error in making Post request: {str(e)}")
            raise e
        # Return the requested endpoint
        return endpoint

    def delete(self, api_id, endpoint_name=None):
        """
        Delete an entity by ID from the given endpoint.
    
        Args:
            api_id (str): The ID of the entity to be deleted.
            endpoint_name (Optional[str]): The name of the endpoint from which the entity is to be deleted.
                                        If not provided, the default endpoint name is used.
    
        Returns:
            None.
    
        Raises:
            Exception: If the delete request fails.
        """

        # Set endpoint if provided
        if not endpoint_name:
            endpoint_name = self._endpoint_name

        try:
            # Send DELETE request for provided sw6_id at defined endpoint
            self.sw6_client.request_delete(f"/{endpoint_name}/{api_id}")
        except Exception as e:
            # Log any errors encountered during delete process
            self.logger.error(
                f'Error encountered during delete process of sw6_id {api_id} at endpoint {self._endpoint_name}: {str(e)}')
            raise

    def post_(self, sw6_json_data, detailed_response=False, endpoint_name=None):
        if not endpoint_name:
            endpoint_name = self._endpoint_name
        request_args = {
            "request_url": f"/{endpoint_name}",
            "payload": sw6_json_data,
        }

        if detailed_response:
            request_args["additional_query_params"] = {"_response": "detail"}

        response = self.sw6_client.request_post(**request_args)

        return response

    def patch_(self, sw6_json_data, endpoint_name=None):
        if not endpoint_name:
            endpoint_name = self._endpoint_name
        response = self.sw6_client.request_patch(
            request_url=f"/{endpoint_name}/{sw6_json_data['id']}",
            payload=sw6_json_data,
            additional_query_params={"_response": "detail"}
        )
        return response

    def bulk_uploads(self, sw6_json_data, endpoint_name=None):
        """
        Performs bulk uploads to the SWC server.

       .. note::

            This function sends an array of payloads for each respective entity operation captured as JSON.
            Action execution is deferred until server side processing begins and will have its outcome
            logged along with its respective `syncId`.

        Args:
            sw6_json_data: JSON formatted dictionary data containing application's state

        Returns:
            The server's response after processing each respective entity operation

        Raises:
            Exception: If the request post fails
        """

        # Initialize a list containing the payload information
        if not endpoint_name:
            endpoint_name = self._endpoint_name
        payload = {
            "write-a-bulk": {
                "entity": endpoint_name,
                "action": "upsert",
                "payload": [sw6_json_data]
            }
        }

        # Try block intended to catch any exception that might arise while executing POST request.
        try:
            response = self.sw6_client.request_post(
                request_url=f"/_action/sync", payload=payload
            )
        except Exception as e:
            # Log any errors encountered during the overall upload process
            self.logger.error(f'Error encountered during bulk uploads process: {str(e)}')
            # raise

        # Return server response
        return response

    @abstractmethod
    def map_bridge_to_sw6(self, bridge_entity):
        pass

    def update(self, sw6_json_data, bridge_entity):
        payload = self.map_bridge_to_sw6(bridge_entity=bridge_entity)
        # payload['id'] = sw6_json_data['id']
        return payload

    """
    Getter and Setter
    """
    def get_id(self, data):
        return data["id"]

    def delete_all(self):
        list = self.get_api_list()
        for id in list["data"]:
            self.sw6_client.request_delete(f"/{self._endpoint_name}/{id['id']}")

    def get_endpoints_list(self):
        endpoint = self.sw6_client.request_get(request_url="")
        pprint(endpoint)

    def get_api_country_details_by_iso3(self, iso3):
        """
        This function takes an iso3 code as an argument. It uses the code to create
        a payload and sends a post request to the "/search/country" endpoint of the sw6_client.
        It returns the response from the server which contains the country details from the api.

        :param iso3: ISO3 code of a country.
        :return: response from the server containing country details.
        :rtype: dict
        """

        # Initialize the Criteria for filtering
        payload = Criteria()

        # Create a filter with the field as 'iso3' and the provided iso3 code as the value
        payload.filter.append(EqualsFilter(field='iso3', value=iso3))

        try:
            # Send a POST request with the payload, and capture the response
            result = self.sw6_client.request_post(f"/search/country", payload=payload)
            return result

        except Exception as e:
            # If an exception is encountered, log the error with exception details and continue
            self.logger.error(f"Exception Occurred while fetching API Country details by ISO3: {str(e)}")
            return None
