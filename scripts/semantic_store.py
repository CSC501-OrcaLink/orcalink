import argparse
import os
from pathlib import Path

from pyoxigraph import (
    NamedNode,
    QueryBoolean,
    QuerySolutions,
    QueryTriples,
    RdfFormat,
    Store,
)


PROJECT_DIR = Path(__file__).resolve().parent.parent

STORE_PATH = Path(
    os.environ.get(
        "ORCALINK_SEMANTIC_STORE",
        PROJECT_DIR / "data" / "semantic" / "oxigraph_store"
    )
)

ONTOLOGY_PATH = (
    PROJECT_DIR
    / "src"
    / "dal"
    / "models"
    / "semantic"
    / "orcalink.owl"
)

ONTOLOGY_GRAPH_IRI = (
    "https://github.com/CSC501-OrcaLink/orcalink/graph/ontology"
)

DATA_GRAPH_IRI = (
    "https://github.com/CSC501-OrcaLink/orcalink/graph/data"
)


def open_store():
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    return Store(STORE_PATH)


def graph_count(store, graph_iri):
    query = f"""
    SELECT (COUNT(*) AS ?count)
    WHERE {{
        GRAPH <{graph_iri}> {{
            ?s ?p ?o .
        }}
    }}
    """

    result = store.query(query)
    row = next(iter(result), None)

    if row is None:
        return 0

    return int(row["count"].value)


def print_status(store):
    print(f"Store path: {STORE_PATH}")
    print(f"Ontology graph: {ONTOLOGY_GRAPH_IRI}")
    print(f"Data graph: {DATA_GRAPH_IRI}")

    print(
        "Ontology triples:",
        graph_count(store, ONTOLOGY_GRAPH_IRI)
    )

    print(
        "Data triples:",
        graph_count(store, DATA_GRAPH_IRI)
    )

    graphs = list(store.named_graphs())

    print(f"Named graphs: {len(graphs)}")

    for graph in graphs:
        print(f"  {graph.value}")


def load_ontology(store, path):
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Ontology file does not exist: {path}"
        )

    graph = NamedNode(ONTOLOGY_GRAPH_IRI)

    # Repeatable execution: replace only the ontology graph.
    store.update(
        f"CLEAR SILENT GRAPH <{ONTOLOGY_GRAPH_IRI}>"
    )

    store.load(
        path=path,
        format=RdfFormat.RDF_XML,
        to_graph=graph,
    )

    store.flush()

    count = graph_count(store, ONTOLOGY_GRAPH_IRI)

    print(f"Ontology loaded: {path}")
    print(f"Ontology triples: {count}")


def rdf_format_for_path(path):
    suffix = Path(path).suffix.lower()

    formats = {
        ".rdf": RdfFormat.RDF_XML,
        ".xml": RdfFormat.RDF_XML,
        ".owl": RdfFormat.RDF_XML,
        ".ttl": RdfFormat.TURTLE,
        ".nt": RdfFormat.N_TRIPLES,
        ".nq": RdfFormat.N_QUADS,
        ".trig": RdfFormat.TRIG,
    }

    if suffix not in formats:
        raise ValueError(
            f"Unsupported RDF file extension: {suffix}"
        )

    return formats[suffix]


def load_data(store, path):
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"RDF data file does not exist: {path}"
        )

    graph = NamedNode(DATA_GRAPH_IRI)

    # Repeatable execution: replace only the instance-data graph.
    store.update(
        f"CLEAR SILENT GRAPH <{DATA_GRAPH_IRI}>"
    )

    store.load(
        path=path,
        format=rdf_format_for_path(path),
        to_graph=graph,
    )

    store.flush()

    count = graph_count(store, DATA_GRAPH_IRI)

    print(f"RDF data loaded: {path}")
    print(f"Data triples: {count}")


def print_query_result(result):
    if isinstance(result, QueryBoolean):
        print(bool(result))
        return

    if isinstance(result, QuerySolutions):
        variables = [
            variable.value
            for variable in result.variables
        ]

        print("\t".join(variables))

        row_count = 0

        for row in result:
            values = []

            for variable in variables:
                value = row[variable]

                if value is None:
                    values.append("")
                else:
                    values.append(value.value)

            print("\t".join(values))
            row_count += 1

        print(f"Rows: {row_count}")
        return

    if isinstance(result, QueryTriples):
        count = 0

        for triple in result:
            print(triple)
            count += 1

        print(f"Triples: {count}")
        return

    print(result)


def run_query(store, query_path):
    query_path = Path(query_path)

    query = query_path.read_text(
        encoding="utf-8"
    )

    result = store.query(query)

    print_query_result(result)


def run_update(store, update_path):
    update_path = Path(update_path)

    update = update_path.read_text(
        encoding="utf-8"
    )

    store.update(update)
    store.flush()

    print(f"SPARQL update executed: {update_path}")


def main():
    parser = argparse.ArgumentParser(
        description="OrcaLink semantic triple-store utility"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    subparsers.add_parser(
        "init",
        help="Create/open the local semantic store"
    )

    load_ontology_parser = subparsers.add_parser(
        "load-ontology",
        help="Replace and load the ontology named graph"
    )

    load_ontology_parser.add_argument(
        "path",
        nargs="?",
        default=str(ONTOLOGY_PATH)
    )

    load_data_parser = subparsers.add_parser(
        "load-data",
        help="Replace and load the instance-data named graph"
    )

    load_data_parser.add_argument("path")

    subparsers.add_parser(
        "status",
        help="Show triple counts and named graphs"
    )

    query_parser = subparsers.add_parser(
        "query",
        help="Run a SPARQL query file"
    )

    query_parser.add_argument("path")

    update_parser = subparsers.add_parser(
        "update",
        help="Run a SPARQL Update file"
    )

    update_parser.add_argument("path")

    args = parser.parse_args()

    store = open_store()

    if args.command == "init":
        print(f"Semantic store ready: {STORE_PATH}")

    elif args.command == "load-ontology":
        load_ontology(store, args.path)

    elif args.command == "load-data":
        load_data(store, args.path)

    elif args.command == "status":
        print_status(store)

    elif args.command == "query":
        run_query(store, args.path)

    elif args.command == "update":
        run_update(store, args.path)


if __name__ == "__main__":
    main()