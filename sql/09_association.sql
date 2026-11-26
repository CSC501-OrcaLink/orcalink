-- Store derived co-sighting associations between individual whales.
-- A co-sighting association does not by itself imply a social relationship.

CREATE TABLE IF NOT EXISTS Association (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,

    WhaleAId INTEGER NOT NULL,
    WhaleBId INTEGER NOT NULL,

    AssociationType TEXT NOT NULL DEFAULT 'CoSighting',

    SharedSightingCount INTEGER NOT NULL,
    WhaleASightingCount INTEGER NOT NULL,
    WhaleBSightingCount INTEGER NOT NULL,

    Score REAL NOT NULL,
    Method TEXT NOT NULL,
    EvidencePolicy TEXT NOT NULL,

    Notes TEXT,

    CONSTRAINT UK_Association_Pair_Type_Method_Evidence
        UNIQUE (
            WhaleAId,
            WhaleBId,
            AssociationType,
            Method,
            EvidencePolicy
        ),

    CONSTRAINT CK_Association_WhaleOrder
        CHECK (WhaleAId < WhaleBId),

    CONSTRAINT CK_Association_SharedCount
        CHECK (SharedSightingCount > 0),

    CONSTRAINT CK_Association_WhaleACount
        CHECK (WhaleASightingCount >= SharedSightingCount),

    CONSTRAINT CK_Association_WhaleBCount
        CHECK (WhaleBSightingCount >= SharedSightingCount),

    CONSTRAINT CK_Association_Score
        CHECK (Score >= 0.0 AND Score <= 1.0),

    CONSTRAINT FK_Association_WhaleAId_2_Whale_Id
        FOREIGN KEY (WhaleAId)
        REFERENCES Whale(Id),

    CONSTRAINT FK_Association_WhaleBId_2_Whale_Id
        FOREIGN KEY (WhaleBId)
        REFERENCES Whale(Id)
);