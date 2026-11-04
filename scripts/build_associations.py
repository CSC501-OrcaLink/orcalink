import sqlite3
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent

DB_PATH = (
    Path(sys.argv[1])
    if len(sys.argv) > 1
    else PROJECT_DIR / "orcalink.db"
)

ASSOCIATION_TYPE = "CoSighting"
METHOD = "Jaccard"
EVIDENCE_POLICY = "LinkedWhaleIds_UnverifiedPerRow"


def table_exists(conn, table_name):
    return conn.execute("""
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
    """, (table_name,)).fetchone() is not None


def build_associations(conn):

    # Rebuild only this derived association set.
    conn.execute("""
        DELETE FROM Association
        WHERE AssociationType = ?
          AND Method = ?
          AND EvidencePolicy = ?
    """, (
        ASSOCIATION_TYPE,
        METHOD,
        EVIDENCE_POLICY
    ))

    conn.execute("""
        WITH ValidObservation AS (
            SELECT DISTINCT
                WhaleId,
                SightingId
            FROM IndividualObservation
            WHERE WhaleId IS NOT NULL
        ),

        WhaleCounts AS (
            SELECT
                WhaleId,
                COUNT(*) AS SightingCount
            FROM ValidObservation
            GROUP BY WhaleId
        ),

        PairCounts AS (
            SELECT
                A.WhaleId AS WhaleAId,
                B.WhaleId AS WhaleBId,
                COUNT(*) AS SharedSightingCount
            FROM ValidObservation AS A
            JOIN ValidObservation AS B
                ON A.SightingId = B.SightingId
               AND A.WhaleId < B.WhaleId
            GROUP BY
                A.WhaleId,
                B.WhaleId
        )

        INSERT INTO Association (
            WhaleAId,
            WhaleBId,
            AssociationType,
            SharedSightingCount,
            WhaleASightingCount,
            WhaleBSightingCount,
            Score,
            Method,
            EvidencePolicy,
            Notes
        )

        SELECT
            P.WhaleAId,
            P.WhaleBId,
            ?,
            P.SharedSightingCount,
            ACount.SightingCount,
            BCount.SightingCount,

            CAST(P.SharedSightingCount AS REAL)
            /
            (
                ACount.SightingCount
                + BCount.SightingCount
                - P.SharedSightingCount
            ),

            ?,
            ?,

            'Derived from linked individual-observation records. '
            || 'Row-level identification confirmation is unavailable.'

        FROM PairCounts AS P

        JOIN WhaleCounts AS ACount
            ON P.WhaleAId = ACount.WhaleId

        JOIN WhaleCounts AS BCount
            ON P.WhaleBId = BCount.WhaleId
    """, (
        ASSOCIATION_TYPE,
        METHOD,
        EVIDENCE_POLICY
    ))

    conn.commit()

    count = conn.execute("""
        SELECT COUNT(*)
        FROM Association
        WHERE AssociationType = ?
          AND Method = ?
          AND EvidencePolicy = ?
    """, (
        ASSOCIATION_TYPE,
        METHOD,
        EVIDENCE_POLICY
    )).fetchone()[0]

    print(f"Associations created: {count}")


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    for table in ("Whale", "IndividualObservation", "Association"):
        if not table_exists(conn, table):
            conn.close()
            raise RuntimeError(
                f"Required table {table} does not exist."
            )

    build_associations(conn)

    conn.close()


if __name__ == "__main__":
    main()