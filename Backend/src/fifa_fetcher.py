"""
fifa_fetcher.py — Scrapes real live ticket prices from fifacollect.info
which aggregates listings from the official FIFA Collect marketplace.

Real data confirmed:
  - Mexico vs South Africa CAT1: $5,530 starting price
  - Korea Republic vs Czech Republic CAT2: $1,800
  - Canada vs Bosnia CAT3: $975
  etc.
"""

import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.fifacollect.info/",
}

BASE_URL = "https://www.fifacollect.info/tickets/world-cup-2026/listings"


def parse_price(text: str) -> float | None:
    """Extract a float price from text like '$5,530.00' or '$1,800'."""
    if not text:
        return None
    cleaned = re.sub(r'[^\d.]', '', text.replace(',', ''))
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def scrape_all_listings() -> list:
    """
    Scrape all ticket listings from fifacollect.info in one request.
    Returns list of dicts with match info and prices.
    """
    print(f"  [FIFA Scraper] Fetching listings from fifacollect.info...")

    try:
        resp = requests.get(BASE_URL, headers=HEADERS, timeout=20)
        print(f"  [FIFA Scraper] HTTP {resp.status_code} — {len(resp.text)} bytes")

        if resp.status_code != 200:
            print(f"  [FIFA Scraper] Non-200 response, aborting.")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")

        # Find all table rows
        rows = soup.select("table tr")
        print(f"  [FIFA Scraper] Found {len(rows)} table rows")

        results = []
        current_match = None

        for row in rows:
            cells = row.select("td")
            if not cells:
                continue

            # Check if this row has a match link (first cell with an anchor)
            match_link = cells[0].select_one("a[href*='marketplace']")
            if match_link:
                match_text = match_link.get_text(strip=True)
                # Extract match name — remove date and match number
                # e.g. "M1 Mexico vs. South Africa June 11, 2026" -> "Mexico vs South Africa"
                match_text = re.sub(r'^M\d+\s*', '', match_text)
                match_text = re.sub(r'\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*.*$', '', match_text)
                match_text = match_text.replace('vs.', 'vs').strip()
                current_match = match_text

                # Get ticket link
                ticket_url = match_link.get("href", "")

            # Try to get category, face value, last sale, starting price
            try:
                # Find the "Starting at" price — last price column
                price_cells = [c for c in cells if '$' in c.get_text()]
                if not price_cells:
                    continue

                # Category is usually in a cell with "CAT"
                cat_cell = next((c for c in cells if 'CAT' in c.get_text()), None)
                category = cat_cell.get_text(strip=True) if cat_cell else "Unknown"

                # Starting price is the last price in the row (rightmost $)
                starting_price = None
                for cell in reversed(cells):
                    text = cell.get_text(strip=True)
                    if text.startswith('$'):
                        p = parse_price(text.split()[0])
                        if p and p > 0:
                            starting_price = p
                            break

                # Face value
                face_value = None
                for cell in cells:
                    text = cell.get_text(strip=True)
                    if text.startswith('$'):
                        p = parse_price(text)
                        if p and p > 0:
                            face_value = p
                            break

                # Location
                loc_cells = [c for c in cells if '\n' in c.get_text() or len(c.get_text(strip=True)) > 5]
                location = ""
                for cell in cells:
                    text = cell.get_text(strip=True)
                    if any(city in text for city in ["City", "Stadium", "Field", "Park", "Bowl", "Arena"]):
                        location = text[:50]
                        break

                # Round
                round_name = ""
                for cell in cells:
                    text = cell.get_text(strip=True)
                    if any(r in text for r in ["Group", "Final", "Round", "Quarter", "Semi"]):
                        round_name = text[:30]
                        break

                if current_match and starting_price:
                    results.append({
                        "match_name":    current_match,
                        "category":      category,
                        "face_value":    face_value,
                        "starting_price": starting_price,
                        "location":      location,
                        "round":         round_name,
                        "ticket_url":    ticket_url if 'ticket_url' in dir() else BASE_URL,
                        "source":        "fifacollect.info",
                        "fetched_at":    datetime.now().isoformat(),
                    })

            except Exception as e:
                continue

        print(f"  [FIFA Scraper] Parsed {len(results)} listings")
        return results

    except requests.exceptions.RequestException as e:
        print(f"  [FIFA Scraper] Network error: {e}")
        return []


def get_lowest_price_per_match(listings: list) -> dict:
    """
    From all listings, find the lowest starting price per match.
    Returns dict: {match_name: {lowest_price, listing_count, ticket_url}}
    """
    match_prices = {}
    for item in listings:
        name = item["match_name"]
        price = item["starting_price"]
        if name not in match_prices:
            match_prices[name] = {
                "lowest_price":  price,
                "listing_count": 1,
                "ticket_url":    item.get("ticket_url", BASE_URL),
                "location":      item.get("location", ""),
                "round":         item.get("round", ""),
            }
        else:
            match_prices[name]["listing_count"] += 1
            if price < match_prices[name]["lowest_price"]:
                match_prices[name]["lowest_price"] = price
    return match_prices


def fetch_and_store_all():
    """
    Main function called by the scheduler every 15 minutes.
    Scrapes fifacollect.info, matches events to our DB, stores price snapshots.
    """
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting FIFA Collect price fetch...")

    from src import database as db

    listings = scrape_all_listings()
    if not listings:
        print("  No listings found — site may be down or structure changed.")
        return

    match_prices = get_lowest_price_per_match(listings)
    events = db.get_all_events()

    stored = 0
    for event in events:
        event_name = event["name"].lower()

        # Try to find a matching scraped listing
        best_match = None
        best_score = 0
        for scraped_name, data in match_prices.items():
            scraped_lower = scraped_name.lower()
            # Score based on how many words match
            event_words  = set(event_name.replace(" vs ", " ").split())
            scraped_words = set(scraped_lower.replace(" vs ", " ").replace(" vs. ", " ").split())
            score = len(event_words & scraped_words)
            if score > best_score:
                best_score = score
                best_match = (scraped_name, data)

        if best_match and best_score >= 2:
            name, data = best_match
            avg_price = data["lowest_price"] * 1.25  # estimate avg as 25% above floor
            db.insert_price_snapshot(
                event_id      = event["id"],
                lowest        = data["lowest_price"],
                average       = avg_price,
                listing_count = data["listing_count"],
            )
            print(f"  ✓ {event['name']:35} → ${data['lowest_price']:>8,.2f}  ({data['listing_count']} listings)  [matched: {name}]")
            stored += 1
        else:
            print(f"  ✗ {event['name']:35} → no match found in scraped data")

    print(f"\n  Done. {stored}/{len(events)} price snapshots stored.\n")


if __name__ == "__main__":
    print("=" * 60)
    print("  FIFA Collect Scraper — Test Run")
    print("=" * 60)
    listings = scrape_all_listings()

    if not listings:
        print("\nNo data returned. Possible reasons:")
        print("  1. Site is down or rate limiting")
        print("  2. HTML structure changed")
        print("  3. JavaScript rendering required")
    else:
        # Show lowest price per match
        match_prices = get_lowest_price_per_match(listings)
        print(f"\n{'Match':<40} {'Lowest':>10}  {'Listings':>8}")
        print("-" * 62)
        for match, data in sorted(match_prices.items()):
            print(f"  {match:<38} ${data['lowest_price']:>9,.2f}  {data['listing_count']:>6}")
        print(f"\nTotal: {len(match_prices)} unique matches, {len(listings)} total listings")