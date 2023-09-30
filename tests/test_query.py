"Test cases for the :module:`arango_orm.database`"

import logging
from datetime import date
from .data import Person, Car
from arango import ArangoClient
from arango.exceptions import CollectionStatisticsError

from arango_orm.database import Database
from arango_orm.collections import Collection
from arango_orm.query import Query

from .fixtures import (  # noqa: F401
    test_db,
    university_graph,
    ensure_student_collection,
    ensure_person_collection,
    ensure_car_collection,
    sample_person,
    sample_persons,
    sample_cars,
)

log = logging.getLogger(__name__)


def test_get_count(test_db: Database, ensure_person_collection):  # noqa: F811
    count_1 = test_db.query(Person).count()
    assert count_1 == 0


def test_get_all_records(test_db: Database, ensure_person_collection):  # noqa: F811
    count_1 = test_db.query(Person).count()
    test_db.add(Person(name="test1", _key="12312", dob=date(year=2016, month=9, day=12)))
    test_db.add(Person(name="test2", _key="22312", dob=date(year=2015, month=9, day=12)))

    assert test_db.query(Person).count() == count_1 + 2

    persons = test_db.query(Person).all()
    assert len(persons) == 2
    assert isinstance(persons[0], Person)


def test_get_records_by_aql(test_db: Database, sample_cars):  # noqa: F811
    cars = test_db.query(Car).aql("FOR rec IN @@collection RETURN rec")

    assert len(cars) == len(sample_cars)
    assert isinstance(cars[0], Car)


def test_get_by_key(test_db: Database, sample_person: Person):  # noqa: F811
    p = test_db.query(Person).by_key(sample_person.key_)
    assert p.name == sample_person.name


def test_test_filter_condition(test_db: Database, sample_cars):  # noqa: F811
    results = test_db.query(Car).filter("year==2005").all()
    assert 1 == len(results)
    assert "Mitsubishi" == results[0].make
    assert "Lancer" == results[0].model
    assert 2005 == results[0].year


def test_test_filter_condition_using_bind_vars(test_db: Database, sample_cars):  # noqa: F811
    results = test_db.query(Car).filter("year==@year", year=2005).all()

    assert 1 == len(results)
    assert "Mitsubishi" == results[0].make
    assert "Lancer" == results[0].model
    assert 2005 == results[0].year


def test_multiple_filter_conditions(test_db: Database, sample_cars):  # noqa: F811
    results = (
        test_db.query(Car)
        .filter("make==@make", make="Honda")
        .filter("year<=@year", year=1990)
        .all()
    )

    assert 1 == len(results)
    assert "Honda" == results[0].make
    assert "Civic" == results[0].model
    assert 1984 == results[0].year


def test_filter_or_conditions(test_db: Database, sample_cars):  # noqa: F811
    results = (
        test_db.query(Car)
        .filter("make==@make", make="Mitsubishi")
        .filter("year<=@year", _or=True, year=1987)
        .all()
    )

    assert 2 == len(results)
    assert results[0].make in ["Honda", "Mitsubishi"]
    assert results[0].model in ["Civic", "Lancer"]
    assert results[0].year in [1984, 2005]


def test_limit_records(test_db: Database, sample_cars):  # noqa: F811
    records = test_db.query(Car).limit(5).all()

    assert len(records) == 5
    assert isinstance(records[0], Car)

    # we'll get only 2 records since we have total of 7 records
    records = test_db.query(Car).limit(3, 5).all()

    assert len(records) == 2
    assert isinstance(records[0], Car)


def test_sort_records(test_db: Database, sample_cars):  # noqa: F811
    records = test_db.query(Car).sort("year DESC").all()

    assert isinstance(records[0], Car)
    assert 2005 == records[0].year

    records = test_db.query(Car).sort("year").all()

    assert isinstance(records[0], Car)
    assert 1984 == records[0].year


def test_multiple_sort(test_db: Database, sample_cars):  # noqa: F811
    records = test_db.query(Car).sort("make").sort("year DESC").all()

    assert isinstance(records[0], Car)
    assert 2001 == records[0].year
    assert "Honda" == records[0].make
    assert "Civic" == records[0].model

    assert isinstance(records[4], Car)
    assert 2005 == records[4].year
    assert "Mitsubishi" == records[4].make
    assert "Lancer" == records[4].model

    assert isinstance(records[6], Car)
    assert 1988 == records[6].year
    assert "Toyota" == records[6].make
    assert "Corolla" == records[6].model


def test_sort_and_limit_records(test_db: Database, sample_cars):  # noqa: F811
    records = test_db.query(Car).sort("year DESC").limit(2).all()

    assert 2 == len(records)

    assert isinstance(records[0], Car)
    assert 2005 == records[0].year
    assert "Mitsubishi" == records[0].make
    assert "Lancer" == records[0].model

    assert isinstance(records[1], Car)
    assert 2004 == records[1].year
    assert "Toyota" == records[1].make
    assert "Corolla" == records[1].model


def test_filter_sort_and_limit_records(test_db: Database, sample_cars):  # noqa: F811
    records = test_db.query(Car).filter("year>=2000").sort("year ASC").limit(2).all()

    assert 2 == len(records)

    assert isinstance(records[0], Car)
    assert 2001 == records[0].year
    assert "Honda" == records[0].make
    assert "Civic" == records[0].model

    assert isinstance(records[1], Car)
    assert 2004 == records[1].year
    assert "Toyota" == records[1].make
    assert "Corolla" == records[1].model


def test_fetch_partial_fields(test_db: Database, sample_cars):  # noqa: F811
    r0 = test_db.query(Car).limit(1).returns("make", "model", "year").all()[0]
    r1 = test_db.query(Car).limit(1).returns("make", "model", "year").first()

    assert r0.owner_key is None
    assert r1.owner_key is None


def test_update_filtered_records(test_db: Database, sample_cars):  # noqa: F811
    test_db.query(Car).filter("model==@model", model="Civic").update(model="CIVIC", make="HONDA")

    records = test_db.query(Car).filter("make=='HONDA'").filter("model=='CIVIC'").all()

    assert 7 == test_db.query(Car).count()
    assert 4 == len(records)


def test_update_some_records(test_db: Database, sample_cars):  # noqa: F811
    test_db.query(Car).sort("year DESC").limit(2).update(make="NEW MAKE")

    records = test_db.query(Car).sort("year DESC").limit(2).all()

    assert isinstance(records[0], Car)
    assert 2005 == records[0].year
    assert "NEW MAKE" == records[0].make
    assert "Lancer" == records[0].model

    assert isinstance(records[1], Car)
    assert 2004 == records[1].year
    assert "NEW MAKE" == records[1].make
    assert "Corolla" == records[1].model


def test_update_all_records(test_db: Database, sample_persons: list[Person]):  # noqa: F811
    test_db.query(Person).update(name="Anonymous")

    persons = test_db.query(Person).all()
    for person in persons:
        assert person.name == "Anonymous"


def test_delete_some_records(test_db: Database, sample_cars):  # noqa: F811
    test_db.query(Car).limit(2).delete()

    assert test_db.query(Car).count() == len(sample_cars) - 2


def test_delete_all_records(test_db: Database, sample_cars):  # noqa: F811
    test_db.query(Car).delete()

    assert 0 == test_db.query(Car).count()


def test_get_full_count(test_db: Database, sample_persons: list[Person]):  # noqa: F811
    count_1 = test_db.query(Person).limit(1).full_count()

    assert count_1 == len(sample_persons)
