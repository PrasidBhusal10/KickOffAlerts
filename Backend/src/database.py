import psycopg2
import psycopg2.extras  # lets rows behave like dictionaries
from src.config import DATABASE_URL

_connection = None
def get_connection():
    global _connection

    # Check if we need a new connection
    if _connection is None or _connection.closed:
        print("  [DB] Connecting to database...")
        _connection = psycopg2.connect(
            DATABASE_URL,
            cursor_factory=psycopg2.extras.RealDictCursor  # rows as dicts
        )
        _connection.autocommit = False  # we'll commit manually
        print("  [DB] Connected.")

    return _connection


def execute(sql: str, params: tuple = (), fetch: str = None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)

            if fetch == "one":
                return cur.fetchone()     # dict or None
            elif fetch == "all":
                return cur.fetchall()     # list of dicts (empty list if none)
            else:
                conn.commit()             # save changes to DB
                return None

    except Exception as e:
        conn.rollback()   # undo any partial changes if something went wrong
        print(f"  [DB] Error running query: {e}")
        print(f"  SQL: {sql}")
        raise


# ---------------------------------------------------------------------------
# Specific query functions — each one does ONE thing clearly
# ---------------------------------------------------------------------------

def get_all_events():
    """Return all events we're currently tracking."""
    return execute("SELECT * FROM events ORDER BY event_date", fetch="all")


def insert_price_snapshot(event_id: int, lowest: float, average: float, listing_count: int):
    """Save one price reading to the database."""
    execute(
        """
        INSERT INTO price_snapshots (event_id, lowest_price, average_price, listing_count)
        VALUES (%s, %s, %s, %s)
        """,
        (event_id, lowest, average, listing_count)
    )


def get_latest_price(event_id: int):
    """Get the most recent price snapshot for an event."""
    return execute(
        """
        SELECT * FROM price_snapshots
        WHERE event_id = %s
        ORDER BY fetched_at DESC
        LIMIT 1
        """,
        (event_id,),
        fetch="one"
    )


def get_price_history(event_id: int, limit: int = 100):
    """Get the last N price snapshots for an event (for charts)."""
    return execute(
        """
        SELECT lowest_price, average_price, fetched_at
        FROM price_snapshots
        WHERE event_id = %s
        ORDER BY fetched_at DESC
        LIMIT %s
        """,
        (event_id, limit),
        fetch="all"
    )


def get_active_alerts_for_event(event_id: int):
    """Get all active user alerts for a given event."""
    return execute(
        """
        SELECT
            ua.*,
            u.email,
            u.phone
        FROM user_alerts ua
        JOIN users u ON u.id = ua.user_id
        WHERE ua.event_id = %s
          AND ua.active = TRUE
        """,
        (event_id,),
        fetch="all"
    )


def update_alert_notified(alert_id: int):
    """Record that we just notified this user (to prevent spam)."""
    execute(
        "UPDATE user_alerts SET last_notified_at = NOW() WHERE id = %s",
        (alert_id,)
    )