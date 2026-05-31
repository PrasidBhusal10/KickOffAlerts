"""
main.py — Entry point for KickOff Alerts.

Usage:
    python main.py                        → API server + scheduler (normal mode)
    python main.py --once                 → one fetch + alert cycle (testing)
    python main.py --api-only             → API server only, no scheduler
    python main.py --search "Brazil vs"   → find SeatGeek event IDs
"""

import sys
import threading
import uvicorn


def run_api():
    import uvicorn
    uvicorn.run("src.api:app", host="0.0.0.0", port=8001, reload=False)


def run_scheduler():
    from src.scheduler import start
    start()


def run_once():
    print("Running one fetch + alert cycle...\n")
    from src.fifa_fetcher import fetch_and_store_all
    from src.alert_engine import run_all_alerts
    fetch_and_store_all()
    run_all_alerts()
    print("Done.")


def search(query: str):
    from src.fetcher import search_events
    print(f"Searching SeatGeek for: '{query}'\n")
    results = search_events(query, per_page=8)
    if not results:
        print("No results found.")
        return
    print(f"{'ID':<12} {'Date':<22} {'Low Price':<12} Title")
    print("-" * 80)
    for r in results:
        price = f"${r['low_price']}" if r["low_price"] else "N/A"
        date  = r["date"][:16] if r["date"] != "TBD" else "TBD"
        print(f"{r['id']:<12} {date:<22} {price:<12} {r['title']}")
    print("\nCopy the ID into your schema.sql INSERT statement.")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        print("=" * 50)
        print("  KickOff Alerts — starting up")
        print("=" * 50)
        print("  Dashboard → http://localhost:8001")
        print("  API docs  → http://localhost:8001/docs")
        print("  Scheduler → every 15 minutes, 24/7")
        print("  Press Ctrl+C to stop\n")
        # Scheduler runs in background thread
        t = threading.Thread(target=run_scheduler, daemon=True)
        t.start()
        # API server blocks the main thread
        run_api()

    elif args[0] == "--once":
        run_once()

    elif args[0] == "--api-only":
        print("Starting API server only (no scheduler)...")
        run_api()

    elif args[0] == "--search" and len(args) > 1:
        search(" ".join(args[1:]))

    else:
        print(__doc__)