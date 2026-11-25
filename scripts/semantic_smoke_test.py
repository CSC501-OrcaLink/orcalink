from pathlib import Path

from semantic_store import (
    DATA_GRAPH_IRI,
    ONTOLOGY_GRAPH_IRI,
    graph_count,
    load_data,
    load_ontology,
    open_store,
)


ROOT = Path(__file__).resolve().parent.parent

SEMANTIC_DIR = (
    ROOT
    / "src"
    / "dal"
    / "models"
    / "semantic"
)

SPARQL_DIR = SEMANTIC_DIR / "sparql"

ONTOLOGY_PATH = SEMANTIC_DIR / "orcalink.owl"

JPOD_ABOX_PATH = (
    SEMANTIC_DIR
    / "orcalink_jpod_abox.rdf"
)

ASSOCIATION_ABOX_PATH = (
    SEMANTIC_DIR
    / "orcalink_associations.ttl"
)


def read_query(name):
    return (
        SPARQL_DIR / name
    ).read_text(
        encoding="utf-8"
    )


def query_count(store, query):
    result = store.query(query)

    row = next(iter(result), None)

    if row is None:
        raise RuntimeError(
            "Count query returned no result."
        )

    return int(row["count"].value)


def ask_query(store, name):
    result = store.query(
        read_query(name)
    )

    return bool(result)


def check_equal(label, actual, expected):
    if actual != expected:
        raise RuntimeError(
            f"{label}: expected {expected}, "
            f"got {actual}"
        )

    print(
        f"[PASS] {label}: {actual}"
    )


def main():
    print("Starting OrcaLink semantic smoke test...")
    print()

    store = open_store()

    # Rebuild the semantic store from committed source files.
    load_ontology(
        store,
        ONTOLOGY_PATH
    )

    load_data(
        store,
        [
            JPOD_ABOX_PATH,
            ASSOCIATION_ABOX_PATH,
        ]
    )

    print()

    ontology_triples = graph_count(
        store,
        ONTOLOGY_GRAPH_IRI
    )

    data_triples = graph_count(
        store,
        DATA_GRAPH_IRI
    )

    if ontology_triples <= 0:
        raise RuntimeError(
            "Ontology graph is empty."
        )

    if data_triples <= 0:
        raise RuntimeError(
            "Data graph is empty."
        )

    print(
        f"[PASS] Ontology triples: "
        f"{ontology_triples}"
    )

    print(
        f"[PASS] Data triples: "
        f"{data_triples}"
    )

    # Validate the TBox.
    class_count = query_count(
        store,
        f"""
        PREFIX owl:
            <http://www.w3.org/2002/07/owl#>

        SELECT (COUNT(DISTINCT ?class) AS ?count)
        WHERE {{
            GRAPH <{ONTOLOGY_GRAPH_IRI}> {{
                ?class a owl:Class .
            }}
        }}
        """
    )

    check_equal(
        "Ontology classes",
        class_count,
        8
    )

    # Validate important ABox counts.
    matriline_count = query_count(
        store,
        f"""
        PREFIX :
            <https://github.com/CSC501-OrcaLink/orcalink/ontology#>

        SELECT (COUNT(DISTINCT ?x) AS ?count)
        WHERE {{
            GRAPH <{DATA_GRAPH_IRI}> {{
                ?x a :Matriline .
            }}
        }}
        """
    )

    membership_count = query_count(
        store,
        f"""
        PREFIX :
            <https://github.com/CSC501-OrcaLink/orcalink/ontology#>

        SELECT (COUNT(*) AS ?count)
        WHERE {{
            GRAPH <{DATA_GRAPH_IRI}> {{
                ?whale
                    :belongsToMatriline
                    ?matriline .
            }}
        }}
        """
    )

    mother_link_count = query_count(
        store,
        f"""
        PREFIX :
            <https://github.com/CSC501-OrcaLink/orcalink/ontology#>

        SELECT (COUNT(*) AS ?count)
        WHERE {{
            GRAPH <{DATA_GRAPH_IRI}> {{
                ?offspring
                    :hasMother
                    ?mother .
            }}
        }}
        """
    )

    association_count = query_count(
        store,
        f"""
        PREFIX :
            <https://github.com/CSC501-OrcaLink/orcalink/ontology#>

        SELECT (COUNT(DISTINCT ?x) AS ?count)
        WHERE {{
            GRAPH <{DATA_GRAPH_IRI}> {{
                ?x a :Association .
            }}
        }}
        """
    )

    check_equal(
        "Matrilines",
        matriline_count,
        6
    )

    check_equal(
        "Matriline memberships",
        membership_count,
        23
    )

    check_equal(
        "Mother links",
        mother_link_count,
        19
    )

    check_equal(
        "Associations",
        association_count,
        686
    )

    # Validate the J49 family query.
    family_result = store.query(
        read_query(
            "07_family_grandmother.sparql"
        )
    )

    family_row = next(
        iter(family_result),
        None
    )

    if family_row is None:
        raise RuntimeError(
            "Family query returned no result."
        )

    grandmother = (
        family_row[
            "grandmotherCode"
        ].value
    )

    matriline = (
        family_row[
            "matrilineLabel"
        ].value
    )

    if (
        grandmother != "J14"
        or matriline != "J14 matriline"
    ):
        raise RuntimeError(
            "Unexpected family-query result: "
            f"{grandmother}, {matriline}"
        )

    print(
        "[PASS] Family query: "
        "J49 -> J14 / J14 matriline"
    )

    # Validate the indirect co-sighting query.
    indirect_result = store.query(
        read_query(
            "09_indirect_cosighting.sparql"
        )
    )

    indirect_row = next(
        iter(indirect_result),
        None
    )

    if indirect_row is None:
        raise RuntimeError(
            "Indirect co-sighting query "
            "returned no candidate."
        )

    print(
        "[PASS] Indirect co-sighting "
        "query returned a candidate"
    )

    # Clean up any previous demo resource.
    store.update(
        read_query(
            "12_delete_demo.sparql"
        )
    )

    if ask_query(
        store,
        "11_ask_demo.sparql"
    ):
        raise RuntimeError(
            "Demo resource still exists "
            "after cleanup."
        )

    print(
        "[PASS] Initial demo resource "
        "is absent"
    )

    # INSERT demonstration.
    store.update(
        read_query(
            "10_insert_demo.sparql"
        )
    )

    if not ask_query(
        store,
        "11_ask_demo.sparql"
    ):
        raise RuntimeError(
            "SPARQL INSERT failed."
        )

    print(
        "[PASS] SPARQL INSERT + ASK"
    )

    # DELETE demonstration.
    store.update(
        read_query(
            "12_delete_demo.sparql"
        )
    )

    if ask_query(
        store,
        "11_ask_demo.sparql"
    ):
        raise RuntimeError(
            "SPARQL DELETE failed."
        )

    print(
        "[PASS] SPARQL DELETE + ASK"
    )

    # Make sure the test leaves the graph unchanged.
    final_data_triples = graph_count(
        store,
        DATA_GRAPH_IRI
    )

    if final_data_triples != data_triples:
        raise RuntimeError(
            "Smoke test changed the final "
            "data graph size: "
            f"{data_triples} -> "
            f"{final_data_triples}"
        )

    print(
        "[PASS] Data graph restored "
        f"to {final_data_triples} triples"
    )

    print()
    print(
        "Semantic smoke test passed."
    )


if __name__ == "__main__":
    main()