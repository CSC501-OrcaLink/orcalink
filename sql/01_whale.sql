-- Store information about individual whales
CREATE TABLE IF NOT EXISTS Whale (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    WhaleCode TEXT NOT NULL,
    Name TEXT,
    Sex TEXT,
    BirthDate TEXT,
    DeathDate TEXT,
    Notes TEXT,

    CONSTRAINT UK_Whale_WhaleCode
        UNIQUE (WhaleCode)
);