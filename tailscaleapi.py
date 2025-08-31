import requests
from typing import List, Dict

from logger import Logger

class TailscaleAPI:
    """Handles Tailscale API interactions"""

    def __init__(self, api_key: str, logger: Logger):
        self.api_key = api_key
        self.logger = logger

    def get_devices(self) -> List[Dict]:
        """Fetch devices from Tailscale API"""
        try:
            resp = requests.get(
                "https://api.tailscale.com/api/v2/tailnet/-/devices",
                auth=(self.api_key, "")
            )
            resp.raise_for_status()
            return resp.json().get("devices", [])
        except Exception as e:
            self.logger.log(f"Error fetching devices from API: {e}")
            raise