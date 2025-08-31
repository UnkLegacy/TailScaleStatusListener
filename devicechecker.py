from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone

from config import Config
from logger import Logger
from statemanager import StateManager


class DeviceChecker:
    """Checks device status and determines online/offline state"""

    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger

    def find_device(self, devices: List[Dict], hostname: str) -> Optional[Dict]:
        """Find a device by hostname in the device list"""
        # First try exact hostname match
        device = next((d for d in devices if d["hostname"].lower() == hostname.lower()), None)

        if not device:
            # Try matching the first part of the name (before the first dot)
            device = next(
                (d for d in devices if d.get("name", "").split(".")[0].lower() == hostname.lower()),
                None
            )

        return device

    def is_device_online(self, device: Dict) -> tuple[bool, Optional[datetime]]:
        """Check if a device is online based on lastSeen timestamp"""
        last_seen_str = device.get("lastSeen")

        if not last_seen_str:
            return False, None

        last_seen = datetime.fromisoformat(last_seen_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        is_online = (now - last_seen) <= timedelta(minutes=self.config.check_minutes)

        return is_online, last_seen

    def check_devices(self, devices: List[Dict], state_manager: StateManager) -> tuple[
        List[tuple[str, Optional[datetime]]], List[tuple[str, Optional[datetime]]]]:
        """Check all configured devices and return status changes"""
        offline_now = []
        online_now = []

        for hostname in self.config.hostnames:
            device = self.find_device(devices, hostname)

            if not device:
                self.logger.log(f"Device {hostname} not found in tailnet")
                continue

            is_online, last_seen = self.is_device_online(device)
            prev_status = state_manager.get_previous_status(hostname)

            if not is_online and prev_status != "offline":
                self.logger.log(f"{hostname} went OFFLINE (last seen {last_seen})")
                offline_now.append((hostname, last_seen))
                state_manager.update_status(hostname, "offline")

            elif is_online and prev_status != "online":
                self.logger.log(f"{hostname} is back ONLINE (last seen {last_seen})")
                online_now.append((hostname, last_seen))
                state_manager.update_status(hostname, "online")

        return offline_now, online_now