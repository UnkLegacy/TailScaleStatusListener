# TailScaleStatusListener

Create a config.json file and run the script.  Use the config-sample.json as a template.

TAILSCALE_API_KEY = Your Tailscale API key
CHECK_MINUTES = The number of minutes since last seen to consider online
SLEEP_SECONDS = The number of seconds to sleep between checks
SMTP_SERVER = Your SMTP server
SMTP_PORT = Your SMTP port
EMAIL_USER = Your email address
EMAIL_PASS = Your email password, use an app password
EMAIL_TO = The email address to send notifications to
HOSTNAMES = A list of hostnames to check

Run the script with `python3 tailscale_monitor.py`