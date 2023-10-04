"Test cases for collection references"

import logging
from datetime import date

import pytest
from arango.exceptions import CollectionStatisticsError
from arango_orm.database import Database
from arango_orm.graph import GraphConnection, Graph
from arango_orm.collections import Collection
from arango_orm.exceptions import DetachedInstanceError


from . import has_same_items
from .data import Citizen, Scientist, Employee
from .fixtures import test_db, ensure_citizen_collection  # noqa: F401

log = logging.getLogger(__name__)


def test_collection_can_store_child_classes(
    test_db: Database, ensure_citizen_collection  # noqa: F811
):
    unemployed = Citizen(key_="PK-1", name="Sleepy Joe", dob="1990-10-10")
    test_db.add(unemployed)

    employee = Employee(key_="PK-2", name="Regular Joe", dob="1990-11-10", base_salary=160000)
    test_db.add(employee)

    scientist = Scientist(
        key_="PK-3",
        name="Genius Joe",
        dob="1990-12-10",
        degress=["PhD", "Masters"],
        research_field="Physics",
    )
    test_db.add(scientist)

    r1: Citizen = test_db.query(Citizen).by_key('PK-1')
    assert r1.name == 'Sleepy Joe'
    assert r1.dob.isoformat() == "1990-10-10"

    r2: Citizen = test_db.query(Citizen).by_key('PK-2')
    assert r2.name == 'Regular Joe'
    assert r2.dob.isoformat() == "1990-11-10"
    assert 'base_salary' not in r2.model_dump()

    r3: Citizen = test_db.query(Citizen).by_key('PK-3')
    assert r3.name == 'Genius Joe'
    assert r3.dob.isoformat() == "1990-12-10"
    assert 'degrees' not in r3.model_dump()
    assert 'research_field' not in r3.model_dump()

    e1: Employee = test_db.query(Employee).by_key("PK-2")
    assert isinstance(e1, Employee)
    assert isinstance(e1, Citizen)
    assert e1.name == 'Regular Joe'
    assert e1.base_salary == 160000

    s1: Scientist = test_db.query(Scientist).by_key("PK-3")
    assert isinstance(s1, Scientist)
    assert isinstance(s1, Citizen)
    assert s1.name == 'Genius Joe'
    assert s1.research_field == 'Physics'
