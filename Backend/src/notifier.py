
from src.config import SENDGRID_API_KEY, SENDGRID_FROM_EMAIL


def send_email(to_email: str, subject: str, plain: str, html: str = None) -> bool:
    if not SENDGRID_API_KEY:
        print(f"    [Email] No API key set — skipping email to {to_email}.")
        return False
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        msg = Mail(
            from_email=SENDGRID_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            plain_text_content=plain,
            html_content=html or plain,
        )
        resp = SendGridAPIClient(SENDGRID_API_KEY).send(msg)
        ok = resp.status_code in (200, 202)
        print(f"    [Email] {'✓' if ok else '✗'} {to_email} (HTTP {resp.status_code})")
        return ok
    except Exception as e:
        print(f"    [Email] ✗ Failed: {e}")
        return False


def send_price_alert_email(
    to_email: str, event_name: str, current_price: float,
    min_price: float, max_price: float, venue: str,
    event_date: str, ticket_url: str, category: str = "Any"
) -> bool:
    from src.email_templates import price_alert_html
    subject = f"PRICE ALERT — {event_name} dropped to ${current_price:.0f}"
    plain = (
        f"Price alert triggered!\n\n"
        f"Match:         {event_name}\n"
        f"Current price: ${current_price:.0f}\n"
        f"Your range:    ${min_price:.0f}–${max_price:.0f}\n"
        f"Venue:         {venue}\n"
        f"Date:          {event_date}\n\n"
        f"Book now: {ticket_url}\n"
    )
    html = price_alert_html(
        event_name, current_price, min_price, max_price,
        venue, event_date, ticket_url, category
    )
    return send_email(to_email, subject, plain, html)


def send_confirmation_email(
    to_email: str, event_name: str,
    min_price: float, max_price: float
) -> bool:
    from src.email_templates import confirmation_html
    subject = f"Alert confirmed — watching {event_name}"
    plain = (
        f"Your alert is active!\n\n"
        f"Match: {event_name}\n"
        f"Range: ${min_price:.0f}–${max_price:.0f}\n\n"
        f"We check prices every 15 minutes. You'll receive an email with a "
        f"direct booking link the moment a ticket drops into your range.\n"
    )
    html = confirmation_html(event_name, min_price, max_price, to_email)
    return send_email(to_email, subject, plain, html)