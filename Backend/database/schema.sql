-- ============================================================
-- Ticket Price Tracker — Database Schema
-- Run this once in your Supabase SQL editor to create all tables
-- ============================================================

-- TABLE 1: events
-- One row per match/event you want to track.
-- You add rows here manually (or via your dashboard later).
CREATE TABLE IF NOT EXISTS events (
    id              SERIAL PRIMARY KEY,         -- auto-incrementing ID
    name            TEXT NOT NULL,              -- "Brazil vs Argentina"
    venue           TEXT,                       -- "Lusail Stadium"
    event_date      TIMESTAMP,                  -- when the match happens
    seatgeek_id     TEXT UNIQUE NOT NULL,       -- SeatGeek's own ID for this event
    created_at      TIMESTAMP DEFAULT NOW()
);

-- TABLE 2: price_snapshots
-- Every single price reading we ever store goes here.
-- This table grows over time — it's your price history.
-- One row = one price check for one event at one moment in time.
CREATE TABLE IF NOT EXISTS price_snapshots (
    id              SERIAL PRIMARY KEY,
    event_id        INTEGER REFERENCES events(id) ON DELETE CASCADE,
    lowest_price    NUMERIC(10, 2),             -- cheapest ticket found
    average_price   NUMERIC(10, 2),             -- average ticket price
    listing_count   INTEGER,                    -- how many tickets available
    fetched_at      TIMESTAMP DEFAULT NOW()     -- when we checked
);

-- Index to speed up queries like "give me all prices for event X"
CREATE INDEX IF NOT EXISTS idx_snapshots_event_id ON price_snapshots(event_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_fetched_at ON price_snapshots(fetched_at);

-- TABLE 3: users
-- Stores registered users who want alerts.
-- Keep this simple for now — no passwords yet.
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    email           TEXT UNIQUE NOT NULL,
    phone           TEXT,                       -- optional, for SMS alerts
    created_at      TIMESTAMP DEFAULT NOW()
);

-- TABLE 4: user_alerts
-- Each row = one user watching one event at a specific price range.
-- A user can have multiple alerts for different events.
-- A user can also have multiple alerts for the same event (different ranges).
CREATE TABLE IF NOT EXISTS user_alerts (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER REFERENCES users(id) ON DELETE CASCADE,
    event_id            INTEGER REFERENCES events(id) ON DELETE CASCADE,
    min_price           NUMERIC(10, 2) NOT NULL,    -- lower bound of their range
    max_price           NUMERIC(10, 2) NOT NULL,    -- upper bound of their range
    active              BOOLEAN DEFAULT TRUE,        -- can be turned on/off
    last_notified_at    TIMESTAMP,                   -- when we last sent them a notification
    created_at          TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- SAMPLE DATA — uncomment and run to add test events
-- ============================================================

-- INSERT INTO events (name, venue, event_date, seatgeek_id) VALUES
--   ('Brazil vs Argentina', 'Lusail Stadium', '2026-06-14 20:00:00', '5555555'),
--   ('World Cup Final',     'Lusail Stadium', '2026-07-15 18:00:00', '6666666');

-- INSERT INTO users (email, phone) VALUES
--   ('you@example.com', '+11234567890');

-- INSERT INTO user_alerts (user_id, event_id, min_price, max_price) VALUES
--   (1, 1, 100.00, 200.00);   -- alert me when Brazil vs Arg is $100–$200