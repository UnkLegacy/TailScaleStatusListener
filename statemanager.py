import os
import json
from typing import Dict, Optional

class StateManager:
    """Manages persistent state of device statuses"""

    def __init__(self, state_file: str = "state.json"):
        self.state_file = state_file
        self.device_status: Dict[str, str] = self._load_state()

    def _load_state(self) -> Dict[str, str]:
        """Load device status from file"""
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                return json.load(f)
        return {}

    def save_state(self):
        """Save current device status to file"""
        with open(self.state_file, "w") as f:
            json.dump(self.device_status, f)

    def get_previous_status(self, hostname: str) -> Optional[str]:
        """Get the previous status of a device"""
        return self.device_status.get(hostname)

    def update_status(self, hostname: str, status: str):
        """Update the status of a device"""
        self.device_status[hostname] = status