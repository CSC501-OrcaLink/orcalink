<img src="assets/OrcaLink_Logo.png" alt="OrcaLink logo" width="180">

# OrcaLink

**CSC 501 · Algorithms and Data Models**
University of Victoria

**Team** · Aung Htut, Bowen Zhang, Sophia Umukoro

OrcaLink organizes records about Southern Resident killer whales. Milestone 4 uses SQLite for whale and sighting records. Milestone 5 adds an OWL ontology and an Oxigraph knowledge graph for exploring J-Pod family relationships and whale co-sightings.

## Quickstart

You need Git, Bash, Python 3.10 or newer with `venv`, and an internet connection for the first dependency install. SQLite is included with Python, and Oxigraph runs locally through PyOxigraph.

```bash
git clone https://github.com/CSC501-OrcaLink/orcalink.git
cd orcalink
bash quickstart.sh
```

From an existing checkout on the Milestone 5 branch, start with the last command. The script installs dependencies, builds the SQLite demo database, and initializes the Oxigraph ontology and data graphs from the repository files. Open [OrcaLink](http://127.0.0.1:5000) and press `Ctrl+C` in the terminal when finished.

If port 5000 is in use, run `ORCALINK_PORT=5051 bash quickstart.sh` and open [OrcaLink on port 5051](http://127.0.0.1:5051). To prepare both stores without starting Flask, run `bash quickstart.sh --build-only`.

The default local stores are `orcalink_demo.db` and `data/semantic/oxigraph_store/`. Repeat runs reuse the graph and keep edits made in the UI. The `--rebuild` flag rebuilds the SQLite demo database and starts Flask. To create a separate knowledge graph from the source files, set `ORCALINK_SEMANTIC_STORE` to a new path before running quickstart.

## Try the app

| Page | Try it |
|---|---|
| Whale Records | Search for `J49` by code and open the **Family** link beside it. The page also supports adding, editing, and deleting SQLite whale records. |
| Family Lookup | Search for `J49`. The graph shows mother `J37`, maternal grandmother `J14`, and the `J14 matriline`. Use **Add a whale** with a unique test code, then use **Edit matriline** to assign it a matriline. A test code added here is stored locally in Oxigraph. |
| Co-sightings | Search for `J1`. The row for `J2` shows 70 shared sightings in the supplied dataset. |

Whale Records writes to SQLite. Family Lookup reads and writes Oxigraph. These stores have separate records and changes are not synchronized. Family data covers selected J-Pod whales. A co-sighting counts records that include both whales.

## Architecture and files

The browser calls Flask. Whale Records uses the SQLite database through Python's `sqlite3` module. The Family Lookup and Co-sightings routes in `src/ui/` call the data access code in `src/dal/`, which uses PyOxigraph to query and update the local graph. The terminal CLI also accesses the graph for loading, queries, and updates.

| Path | Purpose |
|---|---|
| `app.py`, `templates/`, `assets/` | Flask entry point, Whale Records page, and shared assets |
| `src/ui/` | Family Lookup and Co-sightings routes and templates |
| `src/dal/` | Semantic data access |
| `src/dal/models/semantic/` | OWL ontology, J-Pod RDF/XML, association Turtle, and SPARQL files |
| `scripts/semantic_store.py` | Oxigraph command-line interface |
| `scripts/`, `sql/`, `data/processed/` | SQLite build, schema, and prepared datasets |
| `docs/`, `reports/` | Project documentation and reports |

Oxigraph stores the schema in the ontology named graph and instances in the data named graph. Run the CLI `status` command to see both graph IRIs and their counts.

## Run SPARQL and tests

After quickstart has populated the stores, stop Flask with `Ctrl+C` if it is running. From the project root, run the following commands.

```bash
SPARQL_DIR=src/dal/models/semantic/sparql
.venv/bin/python scripts/semantic_store.py status
.venv/bin/python scripts/semantic_store.py query "$SPARQL_DIR/07_family_grandmother.sparql"
.venv/bin/python scripts/semantic_store.py query "$SPARQL_DIR/09_indirect_cosighting.sparql"
.venv/bin/python -m scripts.web_test
```

The family query returns `J14` and `J14 matriline` for `J49`. The indirect query finds pairs of whales connected through a third whale's co-sightings. The web test checks SQLite view, search, add, edit, and delete on a temporary database.

If you have the optional `sqlite3` command installed, run these relational data checks.

```bash
sqlite3 orcalink_demo.db < sql/sighting_checks.sql
sqlite3 orcalink_demo.db < sql/08_group_observation_checks.sql
sqlite3 orcalink_demo.db < sql/10_association_checks.sql
```

Run the semantic smoke test against a disposable store. The test loads both graphs, checks the expected data and sample queries, and demonstrates SPARQL INSERT, ASK, and DELETE.

```bash
(
  orcalink_test_dir="$(mktemp -d)"
  trap 'rm -rf -- "$orcalink_test_dir"' EXIT
  ORCALINK_SEMANTIC_STORE="$orcalink_test_dir/store" \
    .venv/bin/python scripts/semantic_smoke_test.py
)
```

To load the source files manually, use a new store path or a store you intend to reset. Each load command replaces the named graph it loads.

```bash
SEMANTIC_DIR=src/dal/models/semantic
.venv/bin/python scripts/semantic_store.py load-ontology "$SEMANTIC_DIR/orcalink.owl"
.venv/bin/python scripts/semantic_store.py load-data \
  "$SEMANTIC_DIR/orcalink_jpod_abox.rdf" \
  "$SEMANTIC_DIR/orcalink_associations.ttl"
```

## Data sources and reuse

The project uses J-Pod data from Dryad, historical sighting records supplied by The Whale Museum, and background information from the Center for Whale Research. See [Data sources](docs/data_sources.md) for details. Dataset reuse and redistribution are subject to their respective licenses and data-release agreements. The team has not specified a code license.

## Contributions

- **Aung Htut** · Whale and IndividualObservation, OWL ontology, and Flask interface
- **Bowen Zhang** · GroupObservation and Association, Oxigraph and SPARQL, and integration testing
- **Sophia Umukoro** · DataSource, Location, and Sighting, and J-Pod family RDF

Individual contributions are also recorded in the Git history.