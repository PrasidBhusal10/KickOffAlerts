import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional

from src import database as db
from src.notifier import send_price_alert_email, send_confirmation_email

app = FastAPI(title="KickOff Alerts", version="1.0.0")

# Allow frontend on any port to call the API (important for local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the frontend's static files (HTML/CSS/JS)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ─── Request / Response models ────────────────────────────────────────────────

class AlertCreate(BaseModel):
    email: EmailStr
    event_id: int
    min_price: float
    max_price: float
    category: Optional[str] = "Any category"


# ─── Page route ───────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
def root():
    path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(path):
        return FileResponse(path)
    return JSONResponse({"message": "KickOff Alerts API is running. Frontend not found."})


# ─── Events ───────────────────────────────────────────────────────────────────

@app.get("/api/events")
def get_events():
    """All tracked events with their latest price snapshot."""
    events = db.get_all_events()
    result = []
    for e in events:
        latest = db.get_latest_price(e["id"])
        result.append({
            "id":            e["id"],
            "name":          e["name"],
            "venue":         e["venue"],
            "event_date":    str(e["event_date"]) if e["event_date"] else None,
            "seatgeek_id":   e["seatgeek_id"],
            "lowest_price":  float(latest["lowest_price"])  if latest else None,
            "average_price": float(latest["average_price"]) if latest else None,
            "listing_count": latest["listing_count"]        if latest else 0,
            "last_updated":  str(latest["fetched_at"])      if latest else None,
        })
    return {"events": result, "count": len(result)}


@app.get("/api/events/{event_id}/history")
def get_price_history(event_id: int, limit: int = 96):
    """
    Price history for one event — used to draw the chart.
    Default limit = 96 points = 24 hours at 15-min intervals.
    """
    event = db.execute(
        "SELECT * FROM events WHERE id = %s", (event_id,), fetch="one"
    )
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    rows = db.get_price_history(event_id, limit=limit)
    return {
        "event_id":   event_id,
        "event_name": event["name"],
        # reverse so oldest-first for chart rendering
        "history": [
            {
                "price":      float(r["lowest_price"]),
                "average":    float(r["average_price"]),
                "fetched_at": str(r["fetched_at"]),
            }
            for r in reversed(rows)
        ],
    }


# ─── Alerts ───────────────────────────────────────────────────────────────────

@app.post("/api/alerts", status_code=201)
def create_alert(data: AlertCreate):
    """
    Create a price alert. Steps:
      1. Validate the event exists
      2. Validate min < max
      3. Upsert the user row
      4. Insert the alert row
      5. Send confirmation email
    """
    event = db.execute(
        "SELECT * FROM events WHERE id = %s", (data.event_id,), fetch="one"
    )
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if data.min_price >= data.max_price:
        raise HTTPException(
            status_code=400,
            detail="min_price must be strictly less than max_price"
        )

    # Upsert user
    user = db.execute(
        "SELECT id FROM users WHERE email = %s", (data.email,), fetch="one"
    )
    if not user:
        db.execute("INSERT INTO users (email) VALUES (%s)", (data.email,))
        user = db.execute(
            "SELECT id FROM users WHERE email = %s", (data.email,), fetch="one"
        )

    # Insert alert
    db.execute(
        """
        INSERT INTO user_alerts (user_id, event_id, min_price, max_price, active)
        VALUES (%s, %s, %s, %s, TRUE)
        """,
        (user["id"], data.event_id, data.min_price, data.max_price),
    )

    # Confirmation email — non-blocking
    try:
        send_confirmation_email(
            to_email   = data.email,
            event_name = event["name"],
            min_price  = data.min_price,
            max_price  = data.max_price,
        )
    except Exception as ex:
        print(f"  [API] Confirmation email failed (non-fatal): {ex}")

    return {
        "success":    True,
        "event_name": event["name"],
        "message":    (
            f"Alert created for {event['name']}. "
            f"We'll email {data.email} when price drops to "
            f"${data.min_price:.0f}–${data.max_price:.0f}."
        ),
    }


@app.get("/api/alerts/{email}")
def get_alerts_for_user(email: str):
    """Return all alerts belonging to an email address."""
    user = db.execute(
        "SELECT id FROM users WHERE email = %s", (email,), fetch="one"
    )
    if not user:
        return {"alerts": [], "count": 0}

    rows = db.execute(
        """
        SELECT ua.id, ua.event_id, ua.min_price, ua.max_price,
               ua.active, ua.last_notified_at, ua.created_at,
               e.name AS event_name, e.venue, e.event_date
        FROM user_alerts ua
        JOIN events e ON e.id = ua.event_id
        WHERE ua.user_id = %s
        ORDER BY ua.created_at DESC
        """,
        (user["id"],),
        fetch="all",
    )
    alerts = [
        {
            "id":               r["id"],
            "event_id":         r["event_id"],
            "event_name":       r["event_name"],
            "venue":            r["venue"],
            "min_price":        float(r["min_price"]),
            "max_price":        float(r["max_price"]),
            "active":           r["active"],
            "last_notified_at": str(r["last_notified_at"]) if r["last_notified_at"] else None,
            "created_at":       str(r["created_at"]),
        }
        for r in rows
    ]
    return {"alerts": alerts, "count": len(alerts)}


@app.delete("/api/alerts/{alert_id}")
def delete_alert(alert_id: int):
    """Soft-delete (deactivate) an alert."""
    row = db.execute(
        "SELECT id FROM user_alerts WHERE id = %s", (alert_id,), fetch="one"
    )
    if not row:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.execute(
        "UPDATE user_alerts SET active = FALSE WHERE id = %s", (alert_id,)
    )
    return {"success": True, "message": "Alert removed."}


# ─── Stats ────────────────────────────────────────────────────────────────────

@app.get("/api/stats")
def get_stats():
    """Summary numbers for the dashboard header strip."""
    total   = db.execute("SELECT COUNT(*) AS n FROM events", fetch="one")
    active  = db.execute(
        "SELECT COUNT(*) AS n FROM user_alerts WHERE active = TRUE", fetch="one"
    )
    lowest  = db.execute(
        "SELECT MIN(lowest_price) AS n FROM price_snapshots", fetch="one"
    )
    return {
        "total_events":      total["n"]          if total   else 0,
        "active_alerts":     active["n"]         if active  else 0,
        "lowest_price_ever": float(lowest["n"])  if lowest and lowest["n"] else None,
    }