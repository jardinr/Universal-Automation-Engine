
import os
import requests
import json

class HubSpotCRM:
    def __init__(self, config):
        self.config = config
        self.api_key = os.getenv(config.get("api_key_env_var"))
        if not self.api_key:
            raise ValueError("HubSpot API key not found in environment variables.")
        self.base_url = "https://api.hubapi.com"

    def create_deal(self, deal_data):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        url = f"{self.base_url}/crm/v3/objects/deals"
        
        # Example mapping, this would be more dynamic based on config
        properties = {
            "dealname": deal_data.get("dealname"),
            "dealstage": deal_data.get("dealstage"),
            "pipeline": "default", # Assuming a default pipeline
            "notes": deal_data.get("notes")
        }
        
        payload = {"properties": properties}
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()

    def create_contact(self, contact_data):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        url = f"{self.base_url}/crm/v3/objects/contacts"
        
        properties = {
            "email": contact_data.get("email"),
            "firstname": contact_data.get("firstname"),
            "lastname": contact_data.get("lastname")
        }
        
        payload = {"properties": properties}
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()

    # Add other HubSpot actions as needed (e.g., update_deal, create_ticket)
