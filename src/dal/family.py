from pathlib import Path

from pyoxigraph import Literal, NamedNode, Variable

from scripts.semantic_store import DATA_GRAPH_IRI
from src.dal.semantic_graph import with_data_graph

ONTOLOGY_NS = "https://github.com/CSC501-OrcaLink/orcalink/ontology#"
PREFIXES = {
    "ol": ONTOLOGY_NS,
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
}

QUERY_PATH = (
    Path(__file__).resolve().parent
    / "models" / "semantic" / "sparql" / "13_family_lookup.sparql"
)

@with_data_graph
def lookup_family(store, code):
    rows = store.query(
        QUERY_PATH.read_text(encoding="utf-8"),
        substitutions={Variable("code"): Literal(code)},
    )

    results = []
    for row in rows:
        mother = row["motherCode"]
        grandmother = row["grandmotherCode"]
        matriline = row["matrilineLabel"]

        results.append({
            "mother": mother.value if mother is not None else None,
            "grandmother": grandmother.value if grandmother is not None else None,
            "matriline": matriline.value if matriline is not None else None,
        })

    return results


@with_data_graph
def list_matrilines(store):
    return _matrilines(store)


def _matrilines(store):
    rows = store.query(
        f"""
        SELECT DISTINCT ?matriline ?label WHERE {{
            GRAPH <{DATA_GRAPH_IRI}> {{
                ?matriline a ol:Matriline ; rdfs:label ?label .
            }}
        }}
        ORDER BY ?label ?matriline
        """,
        prefixes=PREFIXES,
    )
    return {row["matriline"].value: row["label"].value for row in rows}


def _find_whale(store, code):
    rows = store.query(
        f"""
        SELECT DISTINCT ?code ?whale WHERE {{
            GRAPH <{DATA_GRAPH_IRI}> {{
                ?whale a ol:Whale ; ol:whaleCode ?code .
            }}
        }}
        """,
        prefixes=PREFIXES,
        substitutions={Variable("code"): Literal(code)},
    )
    whales = [row["whale"] for row in rows]
    if len(whales) > 1:
        raise ValueError("More than one record uses that whale code.")
    return whales[0] if whales else None


@with_data_graph
def add_whale(store, code):
    if _find_whale(store, code) is not None:
        raise ValueError("That whale code is already in the knowledge graph.")

    whale = NamedNode(ONTOLOGY_NS + code)
    graph = NamedNode(DATA_GRAPH_IRI)
    occupied = store.query(
        f"ASK {{ GRAPH {graph} {{ {whale} ?property ?value }} }}"
    )
    if occupied:
        raise ValueError("That whale identifier is already in use.")

    store.update(
        f"""
        INSERT DATA {{
            GRAPH {graph} {{
                {whale} a ol:Whale ; ol:whaleCode {Literal(code)} .
            }}
        }}
        """,
        prefixes=PREFIXES,
    )
    store.flush()


@with_data_graph
def update_matriline(store, code, matriline_iri):
    whale = _find_whale(store, code)
    if whale is None:
        raise ValueError("That whale code was not found in the knowledge graph.")
    if matriline_iri not in _matrilines(store):
        raise ValueError("Choose a matriline from the list.")

    matriline = NamedNode(matriline_iri)
    graph = NamedNode(DATA_GRAPH_IRI)
    store.update(
        f"""
        DELETE {{ GRAPH {graph} {{ {whale} ol:belongsToMatriline ?old }} }}
        INSERT {{ GRAPH {graph} {{ {whale} ol:belongsToMatriline {matriline} }} }}
        WHERE {{
            OPTIONAL {{ GRAPH {graph} {{ {whale} ol:belongsToMatriline ?old }} }}
        }}
        """,
        prefixes=PREFIXES,
    )
    store.flush()
