import json
from dataclasses import dataclass

@dataclass
class Config:
    """Configuration data class for the monitor"""
    tailscale_api_key: str
    check_minutes: int
    sleep_seconds: int
    retries: int
    smtp_server: str
    smtp_port: int
    email_user: str
    email_pass: str
    email_to: str
    hostnames: list[str]

    @classmethod
    def load_from_file(cls, filename: str) -> 'Config':
        """Load configuration from JSON file"""
        with open(filename, "r") as f:
            data = json.load(f)

        return cls(
            tailscale_api_key=data["TAILSCALE_API_KEY"],
            check_minutes=data["CHECK_MINUTES"],
            sleep_seconds=data["SLEEP_SECONDS"],
            retries=data["RETRIES"],
            smtp_server=data["SMTP_SERVER"],
            smtp_port=data["SMTP_PORT"],
            email_user=data["EMAIL_USER"],
            email_pass=data["EMAIL_PASS"],
            email_to=data["EMAIL_TO"],
            hostnames=data["HOSTNAMES"]
        )