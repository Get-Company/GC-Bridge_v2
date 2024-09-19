import base64
import json

import requests
from ..MailCoreController import MailCoreController
from ..entities.MailEntity import MailEntity
from config import MJMLAPIConfig


class MailController(MailCoreController):
    def __init__(self):
        self._mail_entity = MailEntity()
        super().__init__()

    def render_mjml_to_html(self, mjml):
        base_url = MJMLAPIConfig.BASE_URL
        app_id = MJMLAPIConfig.APP_ID
        secret = MJMLAPIConfig.SECRET

        # Create the payload for the POST request
        payload = {
            'mjml': mjml
        }

        # Create the encoded authorization
        auth_string = f"{app_id}:{secret}"
        auth_bytes = base64.b64encode(auth_string.encode('ascii')).decode('ascii')

        # Create the HTTP headers with the basic auth
        headers = {
            "Authorization": f"Basic {auth_bytes}",
            "Content-Type": "application/json"
        }

        response = requests.post(base_url, headers=headers, data=json.dumps(payload))

        # Check if request was successful
        if response.status_code == 200:
            return response.json()
        else:
            return {"Error": f"Request failed with status code {response.status_code}"}
