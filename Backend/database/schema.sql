
CREATE TABLE IF NOT EXISTS events (
    id              SERIAL PRIMARY KEY,         -- auto-incrementing ID
    name            TEXT NOT NULL,              -- "Brazil vs Argentina"
    venue           TEXT,                       -- "Lusail Stadium"
    event_date      TIMESTAMP,                  -- when the match happens
    seatgeek_id     TEXT UNIQUE NOT NULL,       -- SeatGeek's own ID for this event
    created_at      TIMESTAMP DEFAULT NOW()
);
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
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    email           TEXT UNIQUE NOT NULL,
    phone           TEXT,                       -- optional, for SMS alerts
    created_at      TIMESTAMP DEFAULT NOW()
);
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
