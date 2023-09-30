"Test cases for the :module:`arango_orm.database`"

import logging
from datetime import date

import pytest
from arango.exceptions import CollectionStatisticsError
from arango_orm.database import Database
from arango_orm.graph import GraphConnection, Graph
from arango_orm.collections import Collection

from . import has_same_items
from .data import (
    Person,
    UniversityGraph,
    Student,
    Teacher,
    Subject,
    SpecializesIn,
    Area,
    DummyFromCol1,
    DummyFromCol2,
    DummyRelation,
    DummyToCol1,
    DummyToCol2,
    Car,
)
from .fixtures import (  # noqa: F401
    test_db,
    university_graph,
    ensure_student_collection,
    ensure_person_collection,
    ensure_car_collection,
    sample_person,
)

log = logging.getLogger(__name__)


def test_database_object_creation(test_db: Database):  # noqa: F811
    assert isinstance(test_db, Database)


def test_collection_create_and_drop(test_db: Database):  # noqa: F811
    new_col = Collection("new_collection")

    test_db.create_collection(new_col)

    assert test_db["new_collection"].statistics()

    test_db.drop_collection(new_col)

    with pytest.raises(CollectionStatisticsError):
        test_db["new_collection"].statistics()


def test_create_collection_from_custom_class(
    test_db: Database, ensure_person_collection  # noqa: F811
):
    assert test_db["persons"].statistics()


def test_add_records(test_db: Database, ensure_person_collection):  # noqa: F811
    p = Person(
        name="test",
        _key="12312",
        age=18,
        dob=date(year=2016, month=9, day=12),
    )
    test_db.add(p)


def test_delete_records(test_db: Database, ensure_person_collection):  # noqa: F811
    p = Person(name="temp", _key="73", dob=date(year=2016, month=9, day=12))

    test_db.add(p)

    count_1 = test_db.query(Person).count()

    test_db.delete(p)

    count_2 = test_db.query(Person).count()

    assert count_2 == count_1 - 1


def test_update_records(test_db: Database, ensure_person_collection):  # noqa: F811
    p = Person(name="temp", _key="12312", dob=date(year=2016, month=9, day=12))

    test_db.add(p)

    p = test_db.query(Person).by_key("12312")
    p.name = "Anonymous"
    test_db.update(p)

    p = test_db.query(Person).by_key("12312")
    assert "Anonymous" == p.name


def test_raw_aql_and_object_conversion(test_db: Database, ensure_person_collection):  # noqa: F811
    test_db.add(Person(name="test1", _key="12345", dob=date(year=2016, month=9, day=12)))
    test_db.add(Person(name="test2", _key="22346", dob=date(year=2015, month=9, day=12)))

    persons = [Person(**p) for p in test_db.aql.execute("FOR p IN persons RETURN p")]

    assert len(persons) >= 2
    assert isinstance(persons[0], Person)


def test_add_record_with_auto_key(test_db: Database, ensure_person_collection):  # noqa: F811
    p = Person(name="key less", dob=date(year=2016, month=9, day=12))
    test_db.add(p)

    assert isinstance(p.key_, str) and p.key_ != ""


def test_default_field_value(test_db: Database, sample_person: Person):  # noqa: F811
    assert sample_person.is_staff is False  # not None


def test_nodirty_from_db(test_db: Database, sample_person: Person):  # noqa: F811
    p = test_db.query(Person).by_key(sample_person.key_)
    assert not p._dirty

    p.name = "Anonymous"
    assert has_same_items(p._dirty, {"name"})


def test_nodirty_after_save(test_db: Database, sample_person: Person):  # noqa: F811
    p = test_db.query(Person).by_key(sample_person.key_)
    p.name = "NB"
    assert has_same_items(p._dirty, {"name"})
    test_db.update(p)
    assert not p._dirty

    new_p = Person(name="test1", dob=date(year=2016, month=9, day=12))
    assert len(new_p._dirty)
    test_db.add(new_p)
    assert not new_p._dirty


def test_only_save_dirty_fields(test_db: Database, sample_person: Person):  # noqa: F811
    # We keep two references of the same record from db
    p_ref1 = test_db.query(Person).by_key(sample_person.key_)

    # Then, let's do update of only dirty fields
    p_ref1.name = "NB-1"
    p_ref1.age = 98

    test_db.update(p_ref1, only_dirty=True)
    fresh = test_db.query(Person).by_key(sample_person.key_)
    assert fresh.name == "NB-1"
    assert fresh.age == 98


def test_bulk_create(test_db: Database, ensure_person_collection):  # noqa: F811
    p_ref_10 = Person(
        name="test_10",
        age=18,
        dob=date(year=2016, month=9, day=12),
    )
    p_ref_11 = Person(
        name="test_11",
        age=18,
        dob=date(year=2016, month=9, day=12),
    )

    test_db.bulk_add(entity_list=[p_ref_10, p_ref_11])
    assert p_ref_10.key_ is not None
    assert p_ref_11.key_ is not None

    p_ref10_recall = test_db.query(Person).by_key(p_ref_10.key_)
    assert p_ref_10.name == p_ref10_recall.name
    assert p_ref_10.key_ == p_ref10_recall.key_
    assert p_ref_10.age == p_ref10_recall.age
    assert p_ref_10.dob == p_ref10_recall.dob


def test_mixed_collection_bulk_create(
    test_db: Database, ensure_person_collection, ensure_car_collection  # noqa: F811
):
    p_ref_10 = Person(
        name="test_10",
        age=18,
        dob=date(year=2016, month=9, day=12),
    )
    p_ref_11 = Person(
        name="test_11",
        age=18,
        dob=date(year=2016, month=9, day=12),
    )
    car1 = Car(make="Honda", model="Fiat", year=2010)
    car2 = Car(make="Honda", model="Skoda", year=2015)

    test_db.bulk_add(entity_list=[p_ref_10, p_ref_11, car1, car2])
    assert p_ref_10.key_ is not None
    assert p_ref_11.key_ is not None
    assert car1.key_ is not None
    assert car2.key_ is not None

    p_ref10_recall = test_db.query(Person).by_key(p_ref_10.key_)
    assert p_ref_10.name == p_ref10_recall.name
    assert p_ref_10.key_ == p_ref10_recall.key_
    assert p_ref_10.age == p_ref10_recall.age
    assert p_ref_10.dob == p_ref10_recall.dob

    car2_recall = test_db.query(Car).by_key(car2.key_)
    assert car2.key_ == car2_recall.key_
    assert car2.make == car2_recall.make
    assert car2.model == car2_recall.model
    assert car2.year == car2_recall.year


def test_bulk_update(test_db: Database, ensure_person_collection):  # noqa: F811
    p_ref1 = Person(
        key_="12312",
        name="test_10",
        age=18,
        dob=date(year=2016, month=9, day=12),
    )
    p_ref2 = Person(
        key_="12345",
        name="test_11",
        age=18,
        dob=date(year=2016, month=9, day=12),
    )

    test_db.bulk_add(entity_list=[p_ref1, p_ref2])

    # First, let's watch the normal behavior
    p_ref1.name = "NB-1"
    p_ref2.name = "NB-2"
    test_db.bulk_update(entity_list=[p_ref1, p_ref2])
    p_ref1 = test_db.query(Person).by_key("12312")
    p_ref2 = test_db.query(Person).by_key("12345")
    assert p_ref1.name == "NB-1"
    assert p_ref2.name == "NB-2"


def test_mixed_collection_bulk_update(
    test_db: Database, ensure_person_collection, ensure_student_collection  # noqa: F811
):
    p1 = Person(
        key_="12312",
        name="test_10",
        age=18,
        dob=date(year=2016, month=9, day=12),
    )
    p2 = Person(
        key_="12345",
        name="test_11",
        age=18,
        dob=date(year=2016, month=9, day=12),
    )
    s1 = Student(_key="S1001", name="John Wayne", age=30)
    s2 = Student(_key="S1002", name="Lilly Parker", age=22)

    test_db.bulk_add(entity_list=[p1, p2, s1, s2])

    s1.name = "Wayne John"
    s2.name = "Parker Lilly"
    p1.name = "NB-10"
    p2.name = "NB-20"
    test_db.bulk_update(entity_list=[s1, s2, p1, p2])

    p1 = test_db.query(Person).by_key("12312")
    p2 = test_db.query(Person).by_key("12345")
    s1 = test_db.query(Student).by_key("S1001")
    s2 = test_db.query(Student).by_key("S1002")
    assert p1.name == "NB-10"
    assert p2.name == "NB-20"
    assert s1.name == "Wayne John"
    assert s2.name == "Parker Lilly"


def test_bulk_delete_records(test_db: Database, ensure_person_collection):  # noqa: F811
    count_0 = test_db.query(Person).count()
    p = [
        Person(name="temp0", _key="73", dob=date(year=2016, month=9, day=12)),
        Person(name="temp1", _key="74", dob=date(year=2017, month=9, day=12)),
        Person(name="temp2", _key="75", dob=date(year=2018, month=9, day=12)),
    ]
    test_db.bulk_add(p)

    count_1 = test_db.query(Person).count()
    assert count_1 == count_0 + len(p)

    test_db.bulk_delete(p)

    count_2 = test_db.query(Person).count()
    assert count_2 == count_0


def test_create_and_drop_graph(test_db: Database, university_graph: Graph):  # noqa: F811
    assert university_graph.__graph__ in [g["name"] for g in test_db.graphs()]


def test_update_graph_add_connection(test_db: Database, university_graph: Graph):  # noqa: F811
    university_graph.__class__.graph_connections.append(
        GraphConnection(DummyFromCol1, DummyRelation, DummyToCol1)
    )

    assert 5 == len(university_graph.__class__.graph_connections)

    graph = university_graph.__class__(connection=test_db)

    test_db.update_graph(graph)

    # Test if we have the new collections and graph relation
    col_names = [c["name"] for c in test_db.collections()]

    assert DummyFromCol1.__collection__ in col_names
    assert DummyToCol1.__collection__ in col_names
    assert DummyRelation.__collection__ in col_names

    assert DummyFromCol2.__collection__ not in col_names
    assert DummyToCol2.__collection__ not in col_names

    gi = test_db.graphs()[0]
    log.debug(gi)

    assert DummyRelation.__collection__ in [e["edge_collection"] for e in gi["edge_definitions"]]


def test_update_graph_update_connection(test_db: Database, university_graph: Graph):  # noqa: F811
    gc = university_graph.__class__.graph_connections[-1]

    university_graph.__class__.graph_connections[-1] = GraphConnection(
        [DummyFromCol1, DummyFromCol2],
        DummyRelation,
        [DummyToCol1, DummyToCol2],
    )

    assert 4 == len(university_graph.__class__.graph_connections)

    graph = university_graph.__class__(connection=test_db)

    test_db.update_graph(graph)

    # Test if we have the new collections and graph relation
    col_names = [c["name"] for c in test_db.collections()]

    assert DummyFromCol1.__collection__ in col_names
    assert DummyFromCol2.__collection__ in col_names
    assert DummyToCol1.__collection__ in col_names
    assert DummyToCol2.__collection__ in col_names
    assert DummyRelation.__collection__ in col_names

    gi = test_db.graphs()[0]
    assert DummyRelation.__collection__ in [e["edge_collection"] for e in gi["edge_definitions"]]

    university_graph.__class__.graph_connections[-1] = gc


def test_update_graph_remove_connection(test_db: Database, university_graph: Graph):  # noqa: F811
    # Remove the dummy relation connection
    gc = university_graph.__class__.graph_connections.pop()
    assert 3 == len(university_graph.__class__.graph_connections)

    graph = university_graph.__class__(connection=test_db)

    test_db.update_graph(graph)

    gi = test_db.graphs()[0]
    assert "resides_in" not in [e["edge_collection"] for e in gi["edge_definitions"]]

    # Reinsert the removed graph connection to maintain consistency for other test cases
    university_graph.__class__.graph_connections.append(gc)


def test_drop_graph_without_collections(test_db: Database, university_graph: Graph):  # noqa: F811
    test_db.drop_graph(university_graph, drop_collections=False)

    # verify that the collections are not deleted
    assert "teaches" in [c["name"] for c in test_db.collections()]

    test_db.create_graph(university_graph)


def test_15_drop_graph_with_collections(test_db: Database, university_graph: Graph):  # noqa: F811
    # making sure we remove the dummy collections too
    test_db.drop_graph(university_graph, drop_collections=True)

    # verify that the collections are not deleted
    assert "teaches" not in [c["name"] for c in test_db.collections()]

    test_db.create_graph(university_graph)


def test_16_create_all(test_db: Database, university_graph: Graph):  # noqa: F811
    test_db.drop_graph(university_graph, drop_collections=True)

    db_objects = [UniversityGraph, DummyFromCol1, DummyToCol1]

    test_db.create_all(db_objects)

    # confirm that graph was created
    assert len(test_db.graphs()) > 0
    assert test_db.graphs()[0]["name"] == university_graph.__graph__

    col_names = [c["name"] for c in test_db.collections()]
    # Confrim dummy from col 1 and to col 2 are created and other dummy collections are not
    # created by the create_all call
    assert DummyFromCol1.__collection__ in col_names
    assert DummyToCol1.__collection__ in col_names

    assert DummyFromCol2.__collection__ not in col_names
    assert DummyToCol2.__collection__ not in col_names
    assert DummyRelation.__collection__ not in col_names

    # Confirm all graph collections are craeted
    assert Student.__collection__ in col_names
    assert Teacher.__collection__ in col_names
    assert Subject.__collection__ in col_names
    assert SpecializesIn.__collection__ in col_names
    assert Area.__collection__ in col_names

    # Now drop the graph and any remaining collections
    test_db.drop_collection(DummyFromCol1)
    test_db.drop_collection(DummyToCol1)
