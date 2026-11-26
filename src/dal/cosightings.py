from pathlib import Path

from pyoxigraph import Literal, Variable

from src.dal.semantic_graph import with_data_graph

QUERY_PATH = (
    Path(__file__).resolve().parent
    / "models" / "semantic" / "sparql" / "14_cosighting_lookup.sparql"
)

@with_data_graph
def lookup_cosightings(store, code):
    rows = store.query(
        QUERY_PATH.read_text(encoding="utf-8"),
        substitutions={Variable("code"): Literal(code)},
    )

    return [
        {
            "code": row["otherCode"].value,
            "shared_count": int(row["sharedCount"].value),
        }
        for row in rows
    ]
