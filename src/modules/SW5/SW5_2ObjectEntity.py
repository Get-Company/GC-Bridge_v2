import requests
from requests.adapters import HTTPAdapter
from requests.auth import HTTPDigestAuth
from urllib3 import Retry


class APIRequestException(Exception):
    def __init__(self, status_code, error_message, response_text):
        self.status_code = status_code
        self.error_message = error_message
        self.response_text = response_text
        super().__init__(self.error_message)


class SW5_2ObjectEntity:
    def __init__(self):

        self.base_url = "https://www.classei-shop.com/api"
        self.session = requests.Session()
        secret = 'vx26pLIhqpyfCAVii3nvS9DFxUWt1cD47G43HFEB'
        self.session.auth = HTTPDigestAuth('geco_bot', secret)
        # Set up automatic retries on certain HTTP codes
        # retry = Retry(
        #     total=5,
        #     backoff_factor=0.3,
        #     status_forcelist=[500, 502, 503, 504],
        # )
        adapter = HTTPAdapter(max_retries=Retry(total=3))
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def _make_request(self, method, url, payload=None):
        full_url = self.base_url + url

        response = self.session.request(method, full_url, json=payload)

        return response.json()

    def get(self, url, data=None):
        response = self._make_request('get', url, payload=data)
        return response

    def post(self, url, data):
        try:
            return self._make_request('post', url, payload=data)
        except Exception as e:
            raise Exception(f"Error in POST request to {url}: {e}")

    def put(self, url, data):
        response = self._make_request('put', url, payload=data)
        return response

    def delete(self, url, data=None):
        try:
            return self._make_request('delete', url, payload=data)
        except Exception as e:
            raise Exception(f"Error in DELETE request to {url}: {e}")

    def get_country(self, country_id):
        url = f"/countries/{country_id}"
        response = self.get(url)
        return response

    def get_customer(self, customer_id, is_number_not_id=False):

        url = f"/customers/{customer_id}"
        if is_number_not_id:
            url += '?useNumberAsId=true'
        response = self.get(url)
        return response
