import logging
import os

import pytest
from arango import ArangoClient
from .fixtures import (  # noqa: F401
    arango_client,
    test_db,
    ensure_car_collection,
    ensure_person_collection,
    ensure_student_collection,
    university_graph,
)

log = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database(request):
    username = os.environ.get("ARANGO_USERNAME", "test")
    password = os.environ.get("ARANGO_PASSWORD", "test")
    arango_hosts = os.environ.get("ARANGO_HOSTS", "http://127.0.0.1:8529")
    database_name = os.environ.get("ARANGO_DATABASE", "test")

    db = ArangoClient(hosts=arango_hosts).db(database_name, username=username, password=password)

    for graph_dict in db.graphs():
        g_name: str = graph_dict["name"]
        if g_name.startswith("_"):
            continue

        db.delete_graph(g_name, drop_collections=True)

    for collection_dict in db.collections():
        col_name: str = collection_dict["name"]
        if col_name.startswith("_"):
            continue

        db.delete_collection(col_name)

    yield
