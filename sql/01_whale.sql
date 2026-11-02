-- Store individual whale information.
CREATE TABLE IF NOT EXISTS Whale (
    whale_id INTEGER PRIMARY KEY,
    whale_code TEXT NOT NULL UNIQUE,
    name TEXT,
    sex TEXT,
    birth_date TEXT,
    death_date TEXT,
    notes TEXT
);
