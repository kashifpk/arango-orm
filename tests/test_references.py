"Test cases for collection references"

# TODO:
import logging
from datetime import date

import pytest
from arango.exceptions import CollectionStatisticsError
from arango_orm.database import Database
from arango_orm.graph import GraphConnection, Graph
from arango_orm.collections import Collection
from arango_orm.exceptions import DetachedInstanceError


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
    sample_cars,
)

log = logging.getLogger(__name__)


def test_model_dump_excludes_references(
    test_db: Database, sample_person: Person, sample_cars: list[Car]  # noqa: F811
):
    for car in sample_cars:
        car.owner_key = sample_person.key_
        test_db.update(car, only_dirty=True)

    person: Person = test_db.query(Person).by_key(sample_person.key_)
    d = person.model_dump()
    assert 'cars' not in d

def test_reference_access(
        test_db: Database, sample_person: Person, sample_cars: list[Car]  # noqa: F811
):
    for car in sample_cars:
        car.owner_key = sample_person.key_
        test_db.update(car, only_dirty=True)

    person: Person = test_db.query(Person).by_key(sample_person.key_)

    assert len(person.cars) == len(sample_cars)
    cars = test_db.query(Car).all()
    for car in cars:
        assert car.owner.id_ == person.id_


def test_detached_instance(
        test_db: Database, sample_person: Person, sample_cars: list[Car]  # noqa: F811
):
    for car in sample_cars:
        car.owner_key = sample_person.key_
        test_db.update(car, only_dirty=True)

    sample_person._db = None
    with pytest.raises(DetachedInstanceError):
        sample_person.cars
