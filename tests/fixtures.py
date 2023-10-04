import os
from typing import Generator, Any
from datetime import date

# from arango_orm.fields import String, Date, Integer, Boolean, List, Nested, Number, Float
# from arango_orm import Collection, Relation, Graph, GraphConnection
import pytest
from arango import ArangoClient


from arango_orm.database import Database
from arango_orm import Relation, Graph

from .data import (
    Citizen,
    UniversityGraph,
    Person,
    Car,
    Student,
    Teacher,
    Subject,
    SpecializesIn,
    Area,
    cars,
    persons,
    teachers_data,
    students_data,
    subjects_data,
    specializations_data,
    areas_data,
)


@pytest.fixture
def arango_client() -> Generator[ArangoClient, Any, None]:
    arango_hosts = os.environ.get("ARANGO_HOSTS", "http://127.0.0.1:8529")
    client = ArangoClient(hosts=arango_hosts)

    yield client

    client.close()
    client = None


@pytest.fixture
def test_db(arango_client: ArangoClient) -> Generator[Database, Any, None]:
    username = os.environ.get("ARANGO_USERNAME", "kashif")
    password = os.environ.get("ARANGO_PASSWORD", "compulife")
    database_name = os.environ.get("ARANGO_DATABASE", "arango_orm_v1_test")
    _db = arango_client.db(database_name, username=username, password=password)
    db = Database(_db)

    yield db

    db = None


@pytest.fixture
def ensure_citizen_collection(test_db: Database):
    test_db.create_collection(Citizen)
    yield
    test_db.drop_collection(Citizen)


@pytest.fixture
def ensure_person_collection(test_db: Database):
    test_db.create_collection(Person)
    yield
    test_db.drop_collection(Person)


@pytest.fixture
def sample_person(test_db: Database, ensure_person_collection) -> Generator[Person, Any, None]:
    p = Person(name="temp", _key="12312", dob=date(year=2016, month=9, day=12))
    test_db.add(p)
    yield p
    test_db.delete(p)


@pytest.fixture
def sample_persons(
    test_db: Database, ensure_person_collection
) -> Generator[list[Person], Any, None]:
    for person in persons:
        test_db.add(person)

    yield persons


@pytest.fixture
def ensure_car_collection(test_db: Database):
    test_db.create_collection(Car)
    yield
    test_db.drop_collection(Car)


@pytest.fixture
def sample_cars(test_db: Database, ensure_car_collection) -> Generator[list[Car], Any, None]:
    for car in cars:
        test_db.add(car)

    yield cars


@pytest.fixture
def ensure_student_collection(test_db: Database):
    test_db.create_collection(Student)
    yield
    test_db.drop_collection(Student)


@pytest.fixture
def ensure_teacher_collection(test_db: Database):
    test_db.create_collection(Teacher)
    yield
    test_db.drop_collection(Teacher)


@pytest.fixture
def ensure_subject_collection(test_db: Database):
    test_db.create_collection(Subject)
    yield
    test_db.drop_collection(Subject)


@pytest.fixture
def ensure_area_collection(test_db: Database):
    test_db.create_collection(Area)
    yield
    test_db.drop_collection(Area)


@pytest.fixture
def ensure_specializes_in_collection(test_db: Database):
    test_db.create_collection(SpecializesIn)
    yield
    test_db.drop_collection(SpecializesIn)


@pytest.fixture
def university_graph(test_db: Database) -> Generator[Graph, Any, None]:
    # Reset graph class connections to original (removing any dummy connections)
    UniversityGraph.graph_connections = UniversityGraph.graph_connections[:4]
    u_graph = UniversityGraph(connection=test_db)

    test_db.create_graph(u_graph)
    yield u_graph

    test_db.drop_graph(u_graph, drop_collections=True)
    u_graph = None


@pytest.fixture
def university_graph_data(test_db: Database, university_graph: Graph):  # noqa: F811
    data = students_data + teachers_data + subjects_data + areas_data + specializations_data

    test_db.bulk_add(data)

    yield

    test_db.bulk_delete(data)


@pytest.fixture
def university_graph_data_with_relations(
    test_db: Database, university_graph: Graph, university_graph_data  # noqa: F811
):
    gotham = test_db.query(Area).by_key("Gotham")
    metropolis = test_db.query(Area).by_key("Metropolis")
    star_city = test_db.query(Area).by_key("StarCity")

    john_wayne = test_db.query(Student).by_key("S1001")
    lilly_parker = test_db.query(Student).by_key("S1002")
    cassandra_nix = test_db.query(Student).by_key("S1003")
    peter_parker = test_db.query(Student).by_key("S1004")

    intro_to_prog = test_db.query(Subject).by_key("ITP101")
    comp_history = test_db.query(Subject).by_key("CS102")
    oop = test_db.query(Subject).by_key("CSOOP02")

    barry_allen = test_db.query(Teacher).by_key("T002")
    bruce_wayne = test_db.query(Teacher).by_key("T001")
    amanda_waller = test_db.query(Teacher).by_key("T003")

    test_db.add(university_graph.relation(peter_parker, Relation("studies"), oop))
    test_db.add(university_graph.relation(peter_parker, Relation("studies"), intro_to_prog))
    test_db.add(university_graph.relation(john_wayne, Relation("studies"), oop))
    test_db.add(university_graph.relation(john_wayne, Relation("studies"), comp_history))
    test_db.add(university_graph.relation(lilly_parker, Relation("studies"), intro_to_prog))
    test_db.add(university_graph.relation(lilly_parker, Relation("studies"), comp_history))
    test_db.add(university_graph.relation(cassandra_nix, Relation("studies"), oop))
    test_db.add(university_graph.relation(cassandra_nix, Relation("studies"), intro_to_prog))

    test_db.add(
        university_graph.relation(barry_allen, SpecializesIn(expertise_level="expert"), oop)
    )
    test_db.add(
        university_graph.relation(
            barry_allen, SpecializesIn(expertise_level="expert"), intro_to_prog
        )
    )
    test_db.add(
        university_graph.relation(bruce_wayne, SpecializesIn(expertise_level="medium"), oop)
    )
    test_db.add(
        university_graph.relation(
            bruce_wayne, SpecializesIn(expertise_level="expert"), comp_history
        )
    )
    test_db.add(
        university_graph.relation(
            amanda_waller, SpecializesIn(expertise_level="basic"), intro_to_prog
        )
    )
    test_db.add(
        university_graph.relation(
            amanda_waller, SpecializesIn(expertise_level="medium"), comp_history
        )
    )

    test_db.add(university_graph.relation(bruce_wayne, Relation("teaches"), oop))
    test_db.add(university_graph.relation(barry_allen, Relation("teaches"), intro_to_prog))
    test_db.add(university_graph.relation(amanda_waller, Relation("teaches"), comp_history))

    test_db.add(university_graph.relation(bruce_wayne, Relation("resides_in"), gotham))
    test_db.add(university_graph.relation(barry_allen, Relation("resides_in"), star_city))
    test_db.add(university_graph.relation(amanda_waller, Relation("resides_in"), metropolis))
    test_db.add(university_graph.relation(john_wayne, Relation("resides_in"), gotham))
    test_db.add(university_graph.relation(lilly_parker, Relation("resides_in"), metropolis))
    test_db.add(university_graph.relation(cassandra_nix, Relation("resides_in"), star_city))
    test_db.add(university_graph.relation(peter_parker, Relation("resides_in"), metropolis))
