import smtplib
from datetime import datetime
from typing import List, Tuple, Optional
from email.mime.text import MIMEText

from config import Config
from logger import Logger

class EmailNotifier:
    """Handles email notifications"""

    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger

    def send_status_changes(self, offline_devices: List[Tuple[str, Optional[datetime]]],
                            online_devices: List[Tuple[str, Optional[datetime]]]):
        """Send email notification for device status changes"""
        if not offline_devices and not online_devices:
            return

        body = self._build_email_body(offline_devices, online_devices)
        self._send_email("Tailscale Device Status Changes", body)

    def _build_email_body(self, offline_devices: List[Tuple[str, Optional[datetime]]],
                          online_devices: List[Tuple[str, Optional[datetime]]]) -> str:
        """Build the email body content"""
        body = ""

        if offline_devices:
            body += "Devices went offline:\n"
            for hostname, last_seen in offline_devices:
                body += f"{hostname} (last seen {last_seen})\n"
            body += "\n"

        if online_devices:
            body += "Devices recovered:\n"
            for hostname, last_seen in online_devices:
                body += f"{hostname} (last seen {last_seen})\n"

        return body

    def _send_email(self, subject: str, body: str):
        """Send email using SMTP"""
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.config.email_user
        msg["To"] = self.config.email_to

        try:
            with smtplib.SMTP_SSL(self.config.smtp_server, self.config.smtp_port) as server:
                server.login(self.config.email_user, self.config.email_pass)
                server.send_message(msg)

            self.logger.log(f"Email sent: {subject}")
        except Exception as e:
            self.logger.log(f"Error sending email: {e}")