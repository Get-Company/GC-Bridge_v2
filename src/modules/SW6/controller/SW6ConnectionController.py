from ..SW6CoreController import SW6CoreController
from config import SW6Config
import time
import requests


class SW6ConnectionController(SW6CoreController):
    def __init__(self):
        """Initializes the SW6ConnectionController with necessary configurations."""
        super().__init__()
        self.config = SW6Config
        self.access_token = None
        self.expiry_time = None  # Zeitpunkt, zu dem das Token abläuft
        self.session = requests.Session()

    def connect(self):
        """
        Establishes a connection to the Shopware 6 API and retrieves an access token.
        Updates the expiry time based on the token's lifespan.
        """
        url = f"{self.config.SHOP_URL}/api/oauth/token"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.config.ID,
            "client_secret": self.config.SECRET,
        }
        try:
            response = self.session.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx and 5xx)
        except requests.RequestException as e:
            self.logger.error(f"Failed to connect to Shopware 6 API: {e}")
            self.logger.error(f"URL: {url}")
            self.logger.error(f"Headers: {headers}")
            raise

        try:
            response_data = response.json()
        except ValueError as e:
            self.logger.error(f"Failed to decode JSON response: {e}")
            raise

        self.access_token = response_data.get('access_token')
        if self.access_token:
            self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
            self.expiry_time = time.time() + response_data.get('expires_in', 0)  # Setzen des Ablaufzeitpunkts
            self.logger.info("Successfully connected to Shopware 6 API.")
        else:
            self.logger.error("Failed to retrieve access token.")
            raise Exception("Failed to retrieve access token.")

    def is_token_expired(self):
        """Überprüft, ob das Token abgelaufen ist.

        Returns:
            bool: True if the token is expired or not set, False otherwise.
        """
        return time.time() >= self.expiry_time if self.expiry_time else True

    def ensure_connection(self):
        """Stellt sicher, dass die Verbindung gültig ist, und erneuert sie bei Bedarf."""
        if self.is_token_expired():
            self.connect()

    def request(self, method, url, **kwargs):
        """Führt eine API-Anfrage aus und stellt sicher, dass die Verbindung gültig ist.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST', etc.).
            url (str): The URL for the request.
            **kwargs: Additional arguments passed to the requests method.

        Returns:
            requests.Response: The response object.
        """
        self.ensure_connection()
        try:
            response = self.session.request(method, url, **kwargs)
        except requests.RequestException as e:
            self.logger.error(f"Failed to make request: {e}")
            raise

        if response.status_code == 401 and 'Token has expired' in response.text:
            # Token is expired. Reconnect and query again
            self.logger.warning("Token has expired, renewing connection.")
            self.connect()
            try:
                response = self.session.request(method, url, **kwargs)
            except requests.RequestException as e:
                self.logger.error(f"Failed to make request: {e}")
                raise

        return response
