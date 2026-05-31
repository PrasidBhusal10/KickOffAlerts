"""
email_templates.py — Premium HTML email templates with FIFA navy/gold theme.
Uses web-safe fonts (Inter via Google Fonts fallback to Segoe UI/Arial) for
maximum email client compatibility.
"""


def price_alert_html(
    event_name: str,
    current_price: float,
    min_price: float,
    max_price: float,
    venue: str,
    event_date: str,
    ticket_url: str,
    category: str = "Any",
    stage: str = "",
    listing_count: int = 0,
) -> str:
    """Premium HTML email for when a ticket price drops into the user's range."""

    saved = max_price - current_price
    saved_text = f"${saved:.0f} below your max" if saved > 0 else "Within your range"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="x-apple-disable-message-reformatting">
  <title>Price Alert — {event_name}</title>
  <!--[if mso]>
  <style>* {{ font-family: Arial, sans-serif !important; }}</style>
  <![endif]-->
</head>
<body style="margin:0;padding:0;background:#F1F5F9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;color:#0F172A;-webkit-font-smoothing:antialiased">

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="padding:30px 16px;background:#F1F5F9">
<tr><td align="center">

<table role="presentation" width="560" cellpadding="0" cellspacing="0" border="0"
       style="max-width:560px;background:#FFFFFF;border-radius:14px;border:1px solid #E5E7EB;border-collapse:separate">

  <!-- HEADER -->
  <tr><td style="background:#003087;padding:22px 26px;border-radius:14px 14px 0 0">
    <table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
      <td style="vertical-align:middle">
        <table cellpadding="0" cellspacing="0" border="0"><tr>
          <td style="vertical-align:middle;padding-right:11px">
            <table width="40" height="40" cellpadding="0" cellspacing="0" border="0"
                   style="background:#C9A84C;border-radius:10px">
              <tr><td align="center" valign="middle" style="font-size:18px;font-weight:700;color:#003087;font-family:Arial,sans-serif">
                🏆
              </td></tr>
            </table>
          </td>
          <td style="vertical-align:middle">
            <div style="font-size:17px;font-weight:700;color:#FFFFFF;letter-spacing:-.3px;line-height:1">
              KickOff<span style="color:#E5C870">Alerts</span>
            </div>
            <div style="font-size:11px;color:rgba(255,255,255,.55);margin-top:3px;letter-spacing:.3px">
              World Cup 2026 · Price Tracker
            </div>
          </td>
        </tr></table>
      </td>
      <td align="right" style="vertical-align:middle">
        <span style="font-size:10px;font-weight:700;color:#003087;background:#E5C870;padding:5px 11px;border-radius:20px;letter-spacing:.4px;text-transform:uppercase;display:inline-block">
          Price drop
        </span>
      </td>
    </tr></table>
  </td></tr>

  <!-- GOLD BAR -->
  <tr><td style="background:#E5C870;height:3px;line-height:3px;font-size:1px">&nbsp;</td></tr>

  <!-- BODY -->
  <tr><td style="padding:30px 26px 24px">

    <!-- EYEBROW -->
    <div style="font-size:10.5px;font-weight:700;color:#C9A84C;letter-spacing:1.8px;text-transform:uppercase;margin-bottom:8px">
      <span style="display:inline-block;width:18px;height:1px;background:#C9A84C;vertical-align:middle;margin-right:8px"></span>
      Alert triggered · just now
    </div>

    <!-- HEADLINE -->
    <h1 style="font-size:26px;font-weight:700;color:#0F172A;letter-spacing:-.6px;line-height:1.2;margin:0 0 8px;font-family:-apple-system,'Segoe UI',Arial,sans-serif">
      Your ticket just got cheaper
    </h1>

    <!-- SUB -->
    <p style="font-size:14px;color:#64748B;line-height:1.6;margin:0 0 24px">
      A listing for <strong style="color:#0F172A;font-weight:600">{event_name}</strong> just
      dropped into your price range. Act fast — listings at this price typically sell
      out within minutes.
    </p>

    <!-- PRICE HERO -->
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
           style="background:#F0F4FF;border-radius:12px;border:1px solid #DBE3FF;margin-bottom:18px">
      <tr>
        <td style="padding:22px;vertical-align:bottom;width:50%">
          <div style="font-size:10.5px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:.8px;margin-bottom:4px">
            Current lowest
          </div>
          <div style="font-size:38px;font-weight:800;color:#003087;line-height:1;letter-spacing:-1.5px;font-family:-apple-system,'Segoe UI',Arial,sans-serif">
            <span style="font-size:16px;font-weight:600;color:#64748B;vertical-align:8px;margin-right:2px">$</span>{current_price:.0f}
          </div>
          <div style="display:inline-block;background:#1A6B3C;color:#FFFFFF;font-size:11px;font-weight:600;padding:4px 10px;border-radius:20px;margin-top:10px;letter-spacing:.2px">
            ↓ {saved_text}
          </div>
        </td>
        <td style="padding:22px 22px 22px 0;vertical-align:bottom;width:50%;text-align:right;border-left:1px solid #DBE3FF">
          <div style="font-size:10.5px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:.8px;margin-bottom:4px">
            Your range
          </div>
          <div style="font-size:22px;font-weight:700;color:#475569;line-height:1;font-family:-apple-system,'Segoe UI',Arial,sans-serif">
            ${min_price:.0f} – ${max_price:.0f}
          </div>
        </td>
      </tr>
    </table>

    <!-- MATCH CARD -->
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
           style="border:1px solid #E5E7EB;border-radius:12px;margin-bottom:18px;border-collapse:separate">
      <!-- card header -->
      <tr><td style="background:#FAFBFC;padding:14px 18px;border-bottom:1px solid #E5E7EB;border-radius:12px 12px 0 0">
        <table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
          <td style="font-size:14px;font-weight:600;color:#0F172A">{event_name}</td>
          <td align="right">
            <span style="font-size:11px;font-weight:600;color:#003087;background:#E0E7FF;padding:3px 9px;border-radius:20px;letter-spacing:.2px">{stage or "Match"}</span>
          </td>
        </tr></table>
      </td></tr>
      <!-- data rows -->
      <tr><td style="padding:14px 18px">
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td style="padding:7px 0;border-bottom:1px solid #F1F5F9;color:#64748B;font-size:13px">📍 Venue</td>
            <td align="right" style="padding:7px 0;border-bottom:1px solid #F1F5F9;color:#0F172A;font-size:13px;font-weight:500">{venue}</td>
          </tr>
          <tr>
            <td style="padding:7px 0;border-bottom:1px solid #F1F5F9;color:#64748B;font-size:13px">📅 Date</td>
            <td align="right" style="padding:7px 0;border-bottom:1px solid #F1F5F9;color:#0F172A;font-size:13px;font-weight:500">{event_date}</td>
          </tr>
          <tr>
            <td style="padding:7px 0;border-bottom:1px solid #F1F5F9;color:#64748B;font-size:13px">🎟 Category</td>
            <td align="right" style="padding:7px 0;border-bottom:1px solid #F1F5F9;color:#0F172A;font-size:13px;font-weight:500">{category}</td>
          </tr>
          <tr>
            <td style="padding:7px 0;color:#64748B;font-size:13px">💾 Listings available</td>
            <td align="right" style="padding:7px 0;color:#0F172A;font-size:13px;font-weight:500">{listing_count or "Multiple"} tickets</td>
          </tr>
        </table>
      </td></tr>
    </table>

    <!-- URGENCY NOTE -->
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
           style="background:#FFF7ED;border:1px solid #FED7AA;border-left:3px solid #C9A84C;border-radius:0 8px 8px 0;margin-bottom:18px">
      <tr><td style="padding:12px 14px">
        <table cellpadding="0" cellspacing="0" border="0"><tr>
          <td style="vertical-align:top;padding-right:10px;color:#C9A84C;font-size:18px;line-height:1">⚡</td>
          <td style="font-size:13px;color:#7C2D12;line-height:1.6">
            <strong style="font-weight:600;color:#7C2D12;display:block;margin-bottom:2px">Act fast — tickets at this price sell within minutes</strong>
            Prices typically rise back up within 30 minutes of dropping. The link below takes you straight to the listing.
          </td>
        </tr></table>
      </td></tr>
    </table>

    <!-- CTA BUTTON -->
    <table width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr><td>
        <a href="{ticket_url}"
           style="display:block;background:#003087;color:#FFFFFF;text-align:center;padding:14px;border-radius:10px;text-decoration:none;font-size:14px;font-weight:600;letter-spacing:.2px;border:1px solid #001F5B;font-family:-apple-system,'Segoe UI',Arial,sans-serif">
          View tickets and book now &rarr;
        </a>
      </td></tr>
      <tr><td align="center" style="padding-top:8px;font-size:11px;color:#94A3B8;letter-spacing:.2px">
        Secure checkout via FIFA Collect marketplace
      </td></tr>
    </table>

  </td></tr>

  <!-- FOOTER -->
  <tr><td style="background:#F8FAFC;border-top:1px solid #E5E7EB;padding:16px 26px;border-radius:0 0 14px 14px">
    <table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
      <td style="font-size:11px;color:#94A3B8">
        Sent by KickOff Alerts · <a href="https://kickoffalerts.com" style="color:#64748B;text-decoration:none">kickoffalerts.com</a>
      </td>
      <td align="right" style="font-size:11px">
        <a href="#" style="color:#64748B;text-decoration:none">Unsubscribe</a> ·
        <a href="#" style="color:#64748B;text-decoration:none">Manage alerts</a>
      </td>
    </tr></table>
  </td></tr>

</table>

</td></tr>
</table>

</body>
</html>"""


def confirmation_html(
    event_name: str,
    min_price: float,
    max_price: float,
    email: str,
) -> str:
    """Premium confirmation email when a user creates a new alert."""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Alert confirmed — {event_name}</title>
</head>
<body style="margin:0;padding:0;background:#F1F5F9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;color:#0F172A;-webkit-font-smoothing:antialiased">

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="padding:30px 16px;background:#F1F5F9">
<tr><td align="center">

<table role="presentation" width="560" cellpadding="0" cellspacing="0" border="0"
       style="max-width:560px;background:#FFFFFF;border-radius:14px;border:1px solid #E5E7EB">

  <!-- HEADER -->
  <tr><td style="background:#003087;padding:22px 26px;border-radius:14px 14px 0 0">
    <table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
      <td>
        <table cellpadding="0" cellspacing="0" border="0"><tr>
          <td style="vertical-align:middle;padding-right:11px">
            <table width="40" height="40" cellpadding="0" cellspacing="0" border="0"
                   style="background:#C9A84C;border-radius:10px">
              <tr><td align="center" valign="middle" style="font-size:18px">🏆</td></tr>
            </table>
          </td>
          <td style="vertical-align:middle">
            <div style="font-size:17px;font-weight:700;color:#FFFFFF;letter-spacing:-.3px;line-height:1">
              KickOff<span style="color:#E5C870">Alerts</span>
            </div>
            <div style="font-size:11px;color:rgba(255,255,255,.55);margin-top:3px">
              World Cup 2026 · Price Tracker
            </div>
          </td>
        </tr></table>
      </td>
      <td align="right">
        <span style="font-size:10px;font-weight:700;color:#FFFFFF;background:#1A6B3C;padding:5px 11px;border-radius:20px;letter-spacing:.4px;text-transform:uppercase;display:inline-block">
          ✓ Confirmed
        </span>
      </td>
    </tr></table>
  </td></tr>

  <!-- GOLD BAR -->
  <tr><td style="background:#E5C870;height:3px;line-height:3px;font-size:1px">&nbsp;</td></tr>

  <!-- BODY -->
  <tr><td style="padding:30px 26px 24px">

    <div style="font-size:10.5px;font-weight:700;color:#C9A84C;letter-spacing:1.8px;text-transform:uppercase;margin-bottom:8px">
      <span style="display:inline-block;width:18px;height:1px;background:#C9A84C;vertical-align:middle;margin-right:8px"></span>
      Alert active · monitoring now
    </div>

    <h1 style="font-size:26px;font-weight:700;color:#0F172A;letter-spacing:-.6px;line-height:1.2;margin:0 0 8px">
      You're watching {event_name}
    </h1>

    <p style="font-size:14px;color:#64748B;line-height:1.6;margin:0 0 24px">
      We'll email <strong style="color:#0F172A;font-weight:600">{email}</strong> the
      moment a ticket drops into your price range. No further action needed.
    </p>

    <!-- ALERT DETAILS CARD -->
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
           style="border:1px solid #E5E7EB;border-radius:12px;margin-bottom:20px;border-collapse:separate">
      <tr><td style="background:#FAFBFC;padding:14px 18px;border-bottom:1px solid #E5E7EB;border-radius:12px 12px 0 0">
        <div style="font-size:11px;font-weight:600;color:#475569;letter-spacing:.4px;text-transform:uppercase">
          Alert details
        </div>
      </td></tr>
      <tr><td style="padding:14px 18px">
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td style="padding:8px 0;border-bottom:1px solid #F1F5F9;color:#64748B;font-size:13px;width:40%">Watching</td>
            <td align="right" style="padding:8px 0;border-bottom:1px solid #F1F5F9;color:#0F172A;font-size:13px;font-weight:600">{event_name}</td>
          </tr>
          <tr>
            <td style="padding:8px 0;border-bottom:1px solid #F1F5F9;color:#64748B;font-size:13px">Price range</td>
            <td align="right" style="padding:8px 0;border-bottom:1px solid #F1F5F9;color:#003087;font-size:15px;font-weight:700">${min_price:.0f} – ${max_price:.0f}</td>
          </tr>
          <tr>
            <td style="padding:8px 0;border-bottom:1px solid #F1F5F9;color:#64748B;font-size:13px">Check frequency</td>
            <td align="right" style="padding:8px 0;border-bottom:1px solid #F1F5F9;color:#0F172A;font-size:13px">Every 15 minutes, 24/7</td>
          </tr>
          <tr>
            <td style="padding:8px 0;color:#64748B;font-size:13px">Notification email</td>
            <td align="right" style="padding:8px 0;color:#0F172A;font-size:13px">{email}</td>
          </tr>
        </table>
      </td></tr>
    </table>

    <!-- INFO NOTE -->
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
           style="background:#EFF6FF;border:1px solid #BFDBFE;border-left:3px solid #003087;border-radius:0 8px 8px 0;margin-bottom:8px">
      <tr><td style="padding:14px 16px">
        <div style="font-size:13px;color:#1E3A8A;line-height:1.7">
          <strong style="font-weight:600;display:block;margin-bottom:4px">What happens next</strong>
          We monitor FIFA Collect listings every 15 minutes. The instant a ticket lists
          at ${min_price:.0f}–${max_price:.0f}, you'll get an email with a direct booking link —
          one click and you're at the listing.
        </div>
      </td></tr>
    </table>

  </td></tr>

  <!-- FOOTER -->
  <tr><td style="background:#F8FAFC;border-top:1px solid #E5E7EB;padding:16px 26px;border-radius:0 0 14px 14px">
    <table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
      <td style="font-size:11px;color:#94A3B8">
        Sent by KickOff Alerts · <a href="https://kickoffalerts.com" style="color:#64748B;text-decoration:none">kickoffalerts.com</a>
      </td>
      <td align="right" style="font-size:11px">
        <a href="#" style="color:#64748B;text-decoration:none">Unsubscribe</a>
      </td>
    </tr></table>
  </td></tr>

</table>

</td></tr>
</table>

</body>
</html>"""