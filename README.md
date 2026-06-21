# 🏆 KickOff Alerts

> **A full-stack ticket price tracker for the FIFA World Cup 2026 that monitors live ticket prices every 15 minutes and emails users the moment a ticket drops into their price range.**

🌐 **Live demo:** [kickoffalerts.com](https://www.kickoffalerts.com)

---

## 📌 What it does

KickOff Alerts solves a real problem: World Cup tickets are expensive and prices fluctuate constantly. Manually refreshing the FIFA Collect marketplace is exhausting, and by the time you check, the price you wanted is gone.

This app does the watching for you:

1. **You set a price range** — e.g. "alert me when Brazil vs Morocco tickets drop to $400–$600"
2. **The system scrapes prices every 15 minutes** from the official FIFA Collect aggregator
3. **The instant a ticket enters your range, you get an email** with a direct booking link
4. **One click** takes you straight to the listing — no searching, no wasted time

---

## 🛠️ Tech stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.12, FastAPI, Uvicorn |
| **Database** | PostgreSQL (Supabase) |
| **Scraping** | BeautifulSoup4, Requests |
| **Scheduling** | APScheduler |
| **Email** | SendGrid (with SPF/DKIM/DMARC domain auth) |
| **Frontend** | HTML, CSS, JavaScript (vanilla) |
| **Deployment** | Railway, GoDaddy DNS |
| **Version control** | Git, GitHub |

---

## ✨ Features

- 🔴 **Real-time price scraping** from the official FIFA Collect marketplace covering all 104 World Cup 2026 matches
- ⏰ **24/7 background scheduler** running every 15 minutes — completely autonomous, no human intervention required
- 💰 **Custom price alerts** with dual-range slider for setting min/max budget
- 📧 **Premium HTML email notifications** with FIFA navy/gold theme, direct booking links, and SPF/DKIM authentication for inbox delivery
- 🕐 **Live countdown** to the opening match (Mexico vs South Africa, June 11, 2026)
- 🌍 **Scrolling flag ticker** featuring all 48 participating nations
- ⭐ **User review system** with star ratings and match associations
- 🚫 **6-hour cooldown** per alert prevents notification spam when prices bounce
- 📊 **Live dashboard** showing all 104 matches organized by group with current lowest price, average price, and price change

---

## 📂 Project structure

```
KickOffAlerts/
├── .gitignore
├── .python-version          # Pins Python 3.12 for Railway
├── Procfile                 # Railway deployment config
├── README.md
├── requirements.txt
└── Backend/
    ├── main.py              # Entry point: starts scheduler + API
    ├── requirements.txt
    ├── database/
    │   └── schema.sql       # 4-table PostgreSQL schema
    ├── src/
    │   ├── __init__.py
    │   ├── api.py           # FastAPI REST endpoints
    │   ├── alert_engine.py  # Price-range check + cooldown logic
    │   ├── config.py        # Loads environment variables
    │   ├── database.py      # psycopg2 wrapper
    │   ├── email_templates.py # Branded HTML email templates
    │   ├── fifa_fetcher.py  # FIFA Collect web scraper
    │   ├── notifier.py      # SendGrid email sender
    │   └── scheduler.py     # APScheduler 15-minute job
    └── static/
        └── index.html       # Frontend dashboard
```

---

## 🏗️ How it works

### Architecture overview

```
┌─────────────────────┐
│  FIFA Collect site  │
└──────────┬──────────┘
           │ HTTP scrape (every 15 min)
           ▼
┌─────────────────────┐
│  fifa_fetcher.py    │ → parses HTML with BeautifulSoup4
└──────────┬──────────┘
           │ stores price snapshot
           ▼
┌─────────────────────┐
│  PostgreSQL (Supabase) │ → 4 tables: events, users, user_alerts, price_snapshots
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  alert_engine.py    │ → checks if new price is in any user's range
└──────────┬──────────┘
           │ if match found
           ▼
┌─────────────────────┐
│  notifier.py        │ → sends branded HTML email via SendGrid
└──────────┬──────────┘
           │
           ▼
        📧 User's inbox
```

### Database schema

- **events** — match name, venue, date, source identifier
- **price_snapshots** — timestamped price readings per event (builds full price history)
- **users** — email addresses for notifications
- **user_alerts** — links users to events with min/max price range and last-notified timestamp

Indexes on `event_id` and `fetched_at` enable fast time-series queries.

### Alert logic

Every 15 minutes, the alert engine:

1. Fetches the latest price snapshot for each tracked event
2. For each active user alert, checks: is `new_price` between `min_price` and `max_price`?
3. Verifies the 6-hour cooldown (`last_notified_at + 6h <= now`) to prevent spam
4. If both checks pass, sends a SendGrid email with the current price and a direct booking link
5. Updates `last_notified_at` to the current time

---

## 🚀 Getting started locally

### Prerequisites

- Python 3.12+
- PostgreSQL database (Supabase free tier works)
- SendGrid account (free tier gives 100 emails/day)

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/PrasidBhusal10/KickOffAlerts.git
cd KickOffAlerts

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate     # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cd Backend
cp .env.example .env
# Then open .env in your editor and fill in your values:
#   DATABASE_URL
#   SENDGRID_API_KEY
#   SENDGRID_FROM_EMAIL
#   FETCH_INTERVAL_MINUTES=15
#   NOTIFICATION_COOLDOWN_HOURS=6

# 5. Set up the database
# Run the SQL in database/schema.sql in your Supabase SQL editor

# 6. Start the app
python main.py
```

The dashboard will be live at `http://localhost:8001`.

API docs are auto-generated at `http://localhost:8001/docs`.

---

## 📡 API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the frontend dashboard |
| `GET` | `/api/events` | List all tracked events with latest prices |
| `POST` | `/api/alerts` | Create a new price alert |
| `GET` | `/api/alerts/{email}` | Get all active alerts for a user |
| `DELETE` | `/api/alerts/{id}` | Deactivate an alert |
| `GET` | `/api/stats` | System statistics (total alerts, lowest price, etc.) |
| `GET` | `/docs` | Interactive Swagger API docs |

---

## 🚢 Deployment

The production app runs on **Railway** with auto-deploy from this repository's `main` branch. The database is hosted on **Supabase** with PgBouncer connection pooling for IPv4 compatibility. The custom domain `kickoffalerts.com` is managed through **GoDaddy** DNS pointing to Railway via CNAME records.

Email delivery is handled through **SendGrid** with authenticated DNS records (SPF, DKIM, DMARC) on the `kickoffalerts.com` domain, ensuring inbox delivery rather than spam.

---

## 🧠 Engineering challenges solved

- **IPv4 vs IPv6 database connectivity** — WSL on Windows defaulted to IPv6, but Supabase direct connections require IPv4 add-ons. Solved by using Supabase's Session Pooler on port 6543 which is IPv4-compatible.
- **HTML scraper resilience** — initial CSS selectors didn't match the aggregator's actual table structure. Solved by fetching raw HTML and inspecting the DOM directly to write accurate selectors.
- **Fuzzy team name matching** — scraped match names like "Korea Republic" had to match database events like "South Korea". Solved with a word-overlap scoring algorithm.
- **Email deliverability** — Gmail flagged early test emails as spam. Solved by purchasing a custom domain and authenticating it with SendGrid via SPF, DKIM, and DMARC DNS records.
- **Railway Python version mismatch** — Railway defaulted to Python 3.13 which broke pydantic-core compilation. Solved by pinning `3.12` in a `.python-version` file and updating dependencies to compatible versions.

---

## 🔮 Future improvements

- [ ] WhatsApp & SMS notifications via Twilio for users who don't check email often
- [ ] Price history charts on the frontend (7-day, 30-day trends)
- [ ] Multi-source scraping (StubHub, Vivid Seats) for comparison
- [ ] User accounts with persistent alert management
- [ ] Mobile app (React Native) for push notifications
- [ ] Migration from APScheduler to Celery + Redis for distributed job queues
- [ ] Add Redis caching layer to reduce database load on the dashboard

---

## 📊 Stats (as of launch)

- **104** matches tracked (all 12 groups + knockout rounds)
- **48** group stage matches across 12 groups
- **15-minute** price refresh interval
- **24/7** autonomous operation
- **6-hour** anti-spam cooldown per alert

---

## 👤 Author

**Prasid Bhusal**

- GitHub: [@PrasidBhusal10](https://github.com/PrasidBhusal10)
- Project: [KickOff Alerts](https://github.com/PrasidBhusal10/KickOffAlerts)
- Live site: [kickoffalerts.com](https://www.kickoffalerts.com)

---

## 📄 License

This project is open source. Feel free to fork it, learn from it, or adapt it for tracking prices of any event-driven marketplace.

---

## 🙏 Acknowledgments

- **FIFA Collect** for the open public ticket data
- **Supabase** for the generous free PostgreSQL tier
- **SendGrid** for reliable transactional email delivery
- **Railway** for one-click GitHub deployment
