import os
from dotenv import load_dotenv

# This reads your .env file and loads all variables into the environment.
# It does nothing if the variables are already set (safe to call multiple times).
load_dotenv()


def _require(name: str) -> str:
    """Get an env variable. Crash with a helpful message if it's missing."""
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(
            f"\n\n  Missing required environment variable: {name}\n"
            f"  Copy .env.example to .env and fill in your values.\n"
        )
    return value


# Database
DATABASE_URL = _require("DATABASE_URL")

# SeatGeek API
SEATGEEK_CLIENT_ID = _require("SEATGEEK_CLIENT_ID")

# Twilio (SMS) — these are optional at startup, required when sending SMS
TWILIO_ACCOUNT_SID  = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN   = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")

# SendGrid (Email) — optional at startup, required when sending email
SENDGRID_API_KEY   = os.getenv("SENDGRID_API_KEY", "")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "alerts@example.com")

# Scheduler settings
FETCH_INTERVAL_MINUTES    = int(os.getenv("FETCH_INTERVAL_MINUTES", "15"))
NOTIFICATION_COOLDOWN_HOURS = int(os.getenv("NOTIFICATION_COOLDOWN_HOURS", "6"))