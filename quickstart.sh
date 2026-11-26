#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ "$#" -gt 1 ]; then
    echo "Usage: bash quickstart.sh [--build-only|--rebuild]"
    exit 1
fi

MODE="${1:-}"
if [ -n "$MODE" ] && [ "$MODE" != "--build-only" ] && [ "$MODE" != "--rebuild" ]; then
    echo "Usage: bash quickstart.sh [--build-only|--rebuild]"
    exit 1
fi

# Create a Python environment if needed
if [ ! -d .venv ]; then
    python3 -m venv .venv
fi

PYTHON=".venv/bin/python"
"$PYTHON" -m pip install -r requirements.txt

# Build a fresh database or check the existing one
if [ "$MODE" = "--rebuild" ]; then
    "$PYTHON" scripts/build_database.py --rebuild
else
    "$PYTHON" scripts/build_database.py
fi

# Initialize the graph once. A staged load keeps a failed import from
# leaving a partially initialized store at the path Flask opens.
"$PYTHON" - <<'PYTHON'
from pathlib import Path
from tempfile import TemporaryDirectory

from pyoxigraph import Store

from scripts.semantic_store import (
    DATA_GRAPH_IRI,
    ONTOLOGY_GRAPH_IRI,
    ONTOLOGY_PATH,
    STORE_PATH,
    graph_count,
    load_data,
    load_ontology,
)

if STORE_PATH.exists():
    store = Store.read_only(str(STORE_PATH))
    if not all(graph_count(store, graph) for graph in (ONTOLOGY_GRAPH_IRI, DATA_GRAPH_IRI)):
        raise SystemExit(
            f"Oxigraph store at {STORE_PATH} is missing ontology or data triples. "
            "Set ORCALINK_SEMANTIC_STORE to a new path to build a fresh demo store."
        )
    print(f"Using existing Oxigraph store: {STORE_PATH}")
else:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=STORE_PATH.parent) as temporary_dir:
        staged_path = Path(temporary_dir) / "store"
        store = Store(staged_path)
        load_ontology(store, ONTOLOGY_PATH)
        load_data(store, [
            ONTOLOGY_PATH.with_name("orcalink_jpod_abox.rdf"),
            ONTOLOGY_PATH.with_name("orcalink_associations.ttl"),
        ])
        del store
        staged_path.rename(STORE_PATH)
PYTHON

if [ "$MODE" = "--build-only" ]; then
    echo "SQLite and Oxigraph ready"
    exit 0
fi

# Start Flask with the prepared demo databases.
export ORCALINK_DB="$PWD/orcalink_demo.db"
PORT="${ORCALINK_PORT:-5000}"
echo "Open http://127.0.0.1:$PORT"
"$PYTHON" -m flask --app app run --host 127.0.0.1 --port "$PORT"