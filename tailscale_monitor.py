import requests
import time
import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta
import os

# ========== Logging with rotation ==========
LOG_FILE = "monitor.log"
STATE_FILE = "state.json"
MAX_LOG_SIZE = 10 * 1024  # 10 KB
MAX_LOG_FILES = 9

def rotate_logs():
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_LOG_SIZE:
        oldest = f"monitor_{MAX_LOG_FILES}.log"
        if os.path.exists(oldest):
            os.remove(oldest)
        for i in range(MAX_LOG_FILES - 1, 0, -1):
            src = f"monitor_{i}.log"
            dst = f"monitor_{i+1}.log"
            if os.path.exists(src):
                os.rename(src, dst)
        os.rename(LOG_FILE, "monitor_1.log")

def log(message):
    rotate_logs()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

# ========== Load Config ==========
with open("config.json", "r") as f:
    config = json.load(f)

TAILSCALE_API_KEY = config["TAILSCALE_API_KEY"]
CHECK_MINUTES = config["CHECK_MINUTES"]
SLEEP_SECONDS = config["SLEEP_SECONDS"]
SMTP_SERVER = config["SMTP_SERVER"]
SMTP_PORT = config["SMTP_PORT"]
EMAIL_USER = config["EMAIL_USER"]
EMAIL_PASS = config["EMAIL_PASS"]
EMAIL_TO = config["EMAIL_TO"]
HOSTNAMES_TO_CHECK = set(config["HOSTNAMES"])

log("Loaded config.json successfully")

# ========== Load State ==========
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        device_status = json.load(f)
else:
    device_status = {}  # hostname -> "online"/"offline"

# ========== Email ==========
def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)

        log(f"Email sent: {subject}")
    except Exception as e:
        log(f"Error sending email: {e}")

# ========== Main Loop ==========
def main():
    while True:
        log("Checking devices...")
        try:
            resp = requests.get(
                "https://api.tailscale.com/api/v2/tailnet/-/devices",
                auth=(TAILSCALE_API_KEY, "")
            )
            resp.raise_for_status()
            devices = resp.json().get("devices", [])

            offline_now = []
            online_now = []

            for hostname in HOSTNAMES_TO_CHECK:
                dev = next((d for d in devices if d["hostname"].lower() == hostname.lower()), None)
                if not dev:
                    log(f"Device {hostname} not found in tailnet")
                    continue

                last_seen_str = dev.get("lastSeen")
                if not last_seen_str:
                    log(f"No lastSeen info for {hostname}, assuming offline")
                    is_online = False
                    last_seen = None
                else:
                    last_seen = datetime.fromisoformat(last_seen_str.replace("Z", "+00:00"))
                    now = datetime.now(timezone.utc)
                    is_online = (now - last_seen) <= timedelta(minutes=CHECK_MINUTES)

                prev_status = device_status.get(hostname)

                if not is_online and prev_status != "offline":
                    log(f"{hostname} went OFFLINE (last seen {last_seen})")
                    offline_now.append((hostname, last_seen))
                    device_status[hostname] = "offline"

                elif is_online and prev_status != "online":
                    log(f"{hostname} is back ONLINE (last seen {last_seen})")
                    online_now.append((hostname, last_seen))
                    device_status[hostname] = "online"

            # Send single email if any changes occurred
            if offline_now or online_now:
                body = ""
                if offline_now:
                    body += "Devices went offline:\n" + "\n".join([f"{h} (last seen {ls})" for h, ls in offline_now]) + "\n"
                if online_now:
                    body += "Devices recovered:\n" + "\n".join([f"{h} (last seen {ls})" for h, ls in online_now])
                send_email("Tailscale Device Status Changes", body)

            # Log status if all OK
            if not offline_now:
                log("All devices are OK")

            # Save state
            with open(STATE_FILE, "w") as f:
                json.dump(device_status, f)

        except Exception as e:
            log(f"Error checking devices: {e}")

        log(f"Sleeping for {SLEEP_SECONDS} seconds...")
        time.sleep(SLEEP_SECONDS)



if __name__ == "__main__":
    main()
