import os
import requests

class AnthropicAPIClient:
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")

    def call_anthropic_api(self, data):
        headers = {
            "content-type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
        if response.status_code != 200:
            raise Exception(f"API request failed with status {response.status_code}: {response.json()}")
        return response.json()