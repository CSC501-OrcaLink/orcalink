from functools import wraps
from threading import Lock

from pyoxigraph import NamedNode, Store

from scripts.semantic_store import DATA_GRAPH_IRI, STORE_PATH


_graph_lock = Lock()


def with_data_graph(operation):
    @wraps(operation)
    def run(*args, **kwargs):
        with _graph_lock:
            if not STORE_PATH.is_dir():
                raise OSError("The OrcaLink semantic store has not been loaded.")

            store = Store(STORE_PATH)
            try:
                if not store.contains_named_graph(NamedNode(DATA_GRAPH_IRI)):
                    raise OSError("The OrcaLink data graph has not been loaded.")
                return operation(store, *args, **kwargs)
            finally:
                del store

    return run
