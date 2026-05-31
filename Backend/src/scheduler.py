"""
scheduler.py — Sets up the APScheduler to run price fetches
and alert checks on a repeating timer, 24/7.
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from src.config import FETCH_INTERVAL_MINUTES


def job():
    """
    The one function that runs on every tick of the scheduler.
    Order matters: always fetch first, then check alerts.
    """
    # Import inside the function so errors in one run don't kill future runs
    from src.fifa_fetcher import fetch_and_store_all
    from src.alert_engine import run_all_alerts

    fetch_and_store_all()   # Step 1: get new prices from SeatGeek
    run_all_alerts()        # Step 2: check if anyone should be notified


def on_job_executed(event):
    """Log when a job finishes successfully."""
    print(f"  [Scheduler] Job completed. Next run in {FETCH_INTERVAL_MINUTES} minutes.")


def on_job_error(event):
    """Log errors but keep the scheduler alive — don't crash on one bad run."""
    print(f"  [Scheduler] ERROR in job: {event.exception}")
    print(f"  [Scheduler] Will retry in {FETCH_INTERVAL_MINUTES} minutes.")


def start():
    """
    Start the scheduler. This call BLOCKS — it runs forever.
    The scheduler wakes up every FETCH_INTERVAL_MINUTES minutes,
    calls job(), then goes back to sleep.
    """
    scheduler = BlockingScheduler()

    # Register our job — runs every N minutes
    scheduler.add_job(
        func     = job,
        trigger  = "interval",
        minutes  = FETCH_INTERVAL_MINUTES,
        id       = "price_fetch",
        name     = "Fetch ticket prices and check alerts",
        misfire_grace_time = 60,   # if a run is missed by <60s, still run it
    )

    # Listen for job completion and errors
    scheduler.add_listener(on_job_executed, EVENT_JOB_EXECUTED)
    scheduler.add_listener(on_job_error,    EVENT_JOB_ERROR)

    print(f"[Scheduler] Starting. Will fetch prices every {FETCH_INTERVAL_MINUTES} minutes.")
    print(f"[Scheduler] Press Ctrl+C to stop.\n")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n[Scheduler] Stopped by user.")
        scheduler.shutdown()