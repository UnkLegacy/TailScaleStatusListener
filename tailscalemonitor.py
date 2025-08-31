import time

from config import Config
from logger import Logger
from statemanager import StateManager
from emailnotifier import EmailNotifier
from tailscaleapi import TailscaleAPI
from devicechecker import DeviceChecker

class TailscaleMonitor:
    """Main monitor class that orchestrates all components"""

    def __init__(self, config_file: str = "config.json"):
        self.config = Config.load_from_file(config_file)
        self.logger = Logger()
        self.state_manager = StateManager()
        self.email_notifier = EmailNotifier(self.config, self.logger)
        self.tailscale_api = TailscaleAPI(self.config.tailscale_api_key, self.logger)
        self.device_checker = DeviceChecker(self.config, self.logger)

        self.logger.log("Tailscale Monitor initialized successfully")

    def run_check_cycle(self):
        """Run a single check cycle"""
        self.logger.log("Checking devices...")

        try:
            devices = self.tailscale_api.get_devices()
            offline_devices, online_devices = self.device_checker.check_devices(devices, self.state_manager)

            # Send notifications if there are changes
            self.email_notifier.send_status_changes(offline_devices, online_devices)

            # Log status if all devices are OK
            if not offline_devices:
                self.logger.log("All devices are OK")

            # Save state
            self.state_manager.save_state()

        except Exception as e:
            self.logger.log(f"Error during check cycle: {e}")

    def run(self):
        """Main monitoring loop"""
        while True:
            self.run_check_cycle()
            self.logger.log(f"Sleeping for {self.config.sleep_seconds} seconds...")
            time.sleep(self.config.sleep_seconds)