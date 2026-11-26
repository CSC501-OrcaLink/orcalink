import sqlite3
import sys
from pathlib import Path
from urllib.parse import quote


PROJECT_DIR = Path(__file__).resolve().parent.parent

DB_PATH = (
    Path(sys.argv[1])
    if len(sys.argv) > 1
    else PROJECT_DIR / "orcalink_demo.db"
)

OUTPUT_PATH = (
    Path(sys.argv[2])
    if len(sys.argv) > 2
    else (
        PROJECT_DIR
        / "src"
        / "dal"
        / "models"
        / "semantic"
        / "orcalink_associations.ttl"
    )
)

ONTOLOGY_NS = (
    "https://github.com/CSC501-OrcaLink/orcalink/ontology#"
)


def table_exists(conn, table_name):
    return conn.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        """,
        (table_name,),
    ).fetchone() is not None


def escape_literal(value):
    text = str(value)

    text = text.replace("\\", "\\\\")
    text = text.replace('"', '\\"')
    text = text.replace("\r", "\\r")
    text = text.replace("\n", "\\n")

    return f'"{text}"'


def resource_iri(local_name):
    encoded = quote(
        str(local_name),
        safe=""
    )

    return f"<{ONTOLOGY_NS}{encoded}>"


def export_rdf(conn, output_path):
    whales = conn.execute(
        """
        SELECT Id, WhaleCode
        FROM Whale
        WHERE WhaleCode IS NOT NULL
        ORDER BY Id
        """
    ).fetchall()

    associations = conn.execute(
        """
        SELECT
            A.Id,
            WA.WhaleCode,
            WB.WhaleCode,
            A.AssociationType,
            A.SharedSightingCount,
            A.WhaleASightingCount,
            A.WhaleBSightingCount,
            A.Score,
            A.Method,
            A.EvidencePolicy,
            A.Notes
        FROM Association AS A
        JOIN Whale AS WA
            ON A.WhaleAId = WA.Id
        JOIN Whale AS WB
            ON A.WhaleBId = WB.Id
        ORDER BY A.Id
        """
    ).fetchall()

    lines = [
        "@prefix : "
        "<https://github.com/CSC501-OrcaLink/orcalink/ontology#> .",
        "@prefix xsd: "
        "<http://www.w3.org/2001/XMLSchema#> .",
        "",
    ]

    triple_count = 0

    # Export Whale identifiers as semantic resources.
    # These may overlap with the J-Pod ABox; RDF graphs use set semantics,
    # so identical triples are not duplicated in the store.
    for _, whale_code in whales:
        whale = resource_iri(whale_code)

        lines.extend([
            f"{whale} a :Whale ;",
            f"    :whaleCode {escape_literal(whale_code)} .",
            "",
        ])

        triple_count += 2

    for (
        association_id,
        whale_a,
        whale_b,
        association_type,
        shared_count,
        whale_a_count,
        whale_b_count,
        score,
        method,
        evidence_policy,
        notes,
    ) in associations:

        association = resource_iri(
            f"association_{association_id}"
        )

        properties = [
            f":hasWhaleA {resource_iri(whale_a)}",
            f":hasWhaleB {resource_iri(whale_b)}",
            (
                ":associationType "
                f"{escape_literal(association_type)}"
            ),
            (
                ':sharedSightingCount '
                f'"{int(shared_count)}"^^xsd:integer'
            ),
            (
                ':whaleASightingCount '
                f'"{int(whale_a_count)}"^^xsd:integer'
            ),
            (
                ':whaleBSightingCount '
                f'"{int(whale_b_count)}"^^xsd:integer'
            ),
            (
                ':associationScore '
                f'"{float(score):.17g}"^^xsd:double'
            ),
            (
                ":associationMethod "
                f"{escape_literal(method)}"
            ),
            (
                ":evidencePolicy "
                f"{escape_literal(evidence_policy)}"
            ),
        ]

        if notes is not None:
            properties.append(
                ":associationNotes "
                f"{escape_literal(notes)}"
            )

        lines.append(
            f"{association} a :Association ;"
        )

        for index, prop in enumerate(properties):
            ending = " ." if index == len(properties) - 1 else " ;"

            lines.append(
                f"    {prop}{ending}"
            )

        lines.append("")

        # rdf:type + all exported properties
        triple_count += 1 + len(properties)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    print(f"Whales exported: {len(whales)}")
    print(
        f"Associations exported: "
        f"{len(associations)}"
    )
    print(
        f"RDF triples written: "
        f"{triple_count}"
    )
    print(f"Output: {output_path}")


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database does not exist: {DB_PATH}"
        )

    conn = sqlite3.connect(DB_PATH)

    for table in ("Whale", "Association"):
        if not table_exists(conn, table):
            conn.close()

            raise RuntimeError(
                f"Required table {table} does not exist."
            )

    association_count = conn.execute(
        "SELECT COUNT(*) FROM Association"
    ).fetchone()[0]

    if association_count == 0:
        conn.close()

        raise RuntimeError(
            "Association table is empty."
        )

    invalid_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM Association
        WHERE WhaleAId >= WhaleBId
           OR SharedSightingCount <= 0
           OR Score NOT BETWEEN 0.0 AND 1.0
        """
    ).fetchone()[0]

    if invalid_count:
        conn.close()

        raise RuntimeError(
            f"Invalid association rows: {invalid_count}"
        )

    export_rdf(
        conn,
        OUTPUT_PATH
    )

    conn.close()


if __name__ == "__main__":
    main()