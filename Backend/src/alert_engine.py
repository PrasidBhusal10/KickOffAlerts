from datetime import datetime
from src.config import NOTIFICATION_COOLDOWN_HOURS
from src import database as db
from src.notifier import send_price_alert_email


def hours_since(ts) -> float:
    if ts is None:
        return 9999
    now = datetime.now()
    if hasattr(ts, "tzinfo") and ts.tzinfo:
        now = datetime.now(ts.tzinfo)
    return (now - ts).total_seconds() / 3600


def check_alerts_for_event(event_id: int, event_name: str, venue: str,
                            event_date: str, new_price: float):
    alerts = db.get_active_alerts_for_event(event_id)
    if not alerts:
        return

    print(f"  [Alerts] {len(alerts)} alert(s) for '{event_name}' @ ${new_price}")

    for alert in alerts:
        in_range    = alert["min_price"] <= new_price <= alert["max_price"]
        cooled_down = hours_since(alert["last_notified_at"]) >= NOTIFICATION_COOLDOWN_HOURS

        if not in_range:
            continue

        if not cooled_down:
            print(f"    • {alert['email']}: in range but on cooldown — skipping")
            continue

        print(f"    ✓ {alert['email']}: ${new_price} in range — sending alert")

        # Build direct ticket URL (SeatGeek deep-link)
        ticket_url = f"https://seatgeek.com/e/{event_id}"

        send_price_alert_email(
            to_email      = alert["email"],
            event_name    = event_name,
            current_price = new_price,
            min_price     = float(alert["min_price"]),
            max_price     = float(alert["max_price"]),
            venue         = venue or "TBD",
            event_date    = str(event_date) if event_date else "TBD",
            ticket_url    = ticket_url,
        )

        db.update_alert_notified(alert["id"])


def run_all_alerts():
    """Called by scheduler after every fetch cycle."""
    print("\n  [Alerts] Running alert engine...")
    events = db.get_all_events()

    for event in events:
        latest = db.get_latest_price(event["id"])
        if latest is None:
            continue
        check_alerts_for_event(
            event_id   = event["id"],
            event_name = event["name"],
            venue      = event.get("venue", ""),
            event_date = event.get("event_date"),
            new_price  = float(latest["lowest_price"]),
        )

    print("  [Alerts] Done.\n")