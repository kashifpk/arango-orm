"Test cases for the :module:`arango_orm.database`"

from datetime import date, datetime
from arango_orm import Collection

from . import has_same_items, all_in,  verify_property_values
from .data import Car, Person


def test_object_from_dict():
    pd = {
        "_key": "37405-4564665-7",
        "dob": "2016-09-12",
        "name": "Kashif Iftikhar",
    }
    new_person = Person(**pd)

    assert "37405-4564665-7" == new_person._key
    assert "Kashif Iftikhar" == new_person.name
    assert date(year=2016, month=9, day=12) == new_person.dob


    pd = {
        "key_": "37405-4564665-7",
        "dob": "2016-09-12",
        "name": "Kashif Iftikhar",
    }
    new_person = Person(**pd)

    assert "37405-4564665-7" == new_person.key_
    assert new_person.key_ == new_person._key
    assert "Kashif Iftikhar" == new_person.name
    assert date(year=2016, month=9, day=12) == new_person.dob


def test_object_creation():
    p = Person(name="test", _key="12312", dob=date(year=2016, month=9, day=12))
    assert "test" == p.name
    assert "12312" == p._key
    assert date(year=2016, month=9, day=12) == p.dob


def test_object_dump():
    p = Person(name="test", _key="12312", dob=date(year=2016, month=9, day=12))
    d = p.model_dump(mode="json", by_alias=True)

    assert "test" == d["name"]
    assert "12312" == d["_key"]
    assert "2016-09-12" == d["dob"]


def test_object_dump_only():
    p = Person(name="test", _key="12312", dob=date(year=2016, month=9, day=12))

    only_fields = ["key_", "name"]
    d = p.model_dump(include=only_fields)

    assert has_same_items(only_fields, d.keys())


def test_object_partial_fields_and_dump():
    p = Person(name="test", _key="12312")
    d = p.model_dump()

    assert all_in(["name", "key_"], d)
    assert d["dob"] is None


def test_object_load_and_dump_with_extra_fields_disabled():
    d = {
        "_key": "person_1",
        "name": "John Doe",
        "dob": "2016-09-12",
        "profession": "absent",
    }
    p = Person(**d)

    assert hasattr(p, "_key")
    assert hasattr(p, "name")
    assert hasattr(p, "dob")
    assert hasattr(p, "profession") is False

    d2 = p.model_dump(by_alias=True)
    assert all_in(["_key", "name", "dob"], d2)
    assert "profession" not in d2


def test_object_load_and_dump_with_extra_fields_enabled():
    d = {
        "make": "Mitsubishi",
        "model": "Lancer",
        "year": 2005,
        "nickname": "Lancer Evo",
    }

    c = Car(**d)
    assert verify_property_values(c, **d)
    assert all_in(["make", "model", "year", "nickname"], c.model_dump())


def test_collection_mixin():
    class ResultMixin:
        timestamp: datetime
        stats: str

    class PingResult(ResultMixin, Collection):
        __collection__ = "ping_results"
        host: str
        status: str
        error_message: str
        stats: dict

    assert all_in(
        ["key_", "timestamp", "host", "status", "error_message", "stats"],
        PingResult.model_fields,
    )

    assert PingResult.model_fields["stats"].annotation is dict  # not String from ResultMixin


def test_multi_level_collection_inheritence():
    class ResultMixin:
        key_: str
        timestamp: datetime
        stats: str

    class Result(ResultMixin):
        host: str
        status: str
        error_message: str

    class PingResult(Result, Collection):
        __collection__ = "ping_results"

        stats: dict

    assert all_in(
        ["key_", "timestamp", "host", "status", "error_message", "stats"],
        PingResult.model_fields,
    )

    assert PingResult.model_fields["stats"].annotation is dict  # not String from ResultMixin


def test_dirty_fields():
    p1 = Person(name="test", _key="12312", dob=date(year=2016, month=9, day=12))
    p2 = Person(
        **{
            "_key": "37405-4564665-7",
            "dob": "2016-09-12",
            "name": "Kashif Iftikhar",
        }
    )

    assert has_same_items(
        p1._dirty, ["name", "key_", "rev_", "dob", "age", "is_staff", "favorite_hobby"]
    )
    assert has_same_items(
        p2._dirty, ["name", "key_", "rev_", "dob", "age", "is_staff", "favorite_hobby"]
    )

    p1._dirty.clear()
    p1.name = "test"  # change name, even if the same as before!
    assert has_same_items(p1._dirty, ["name"])


def test_nested_field():
    pd = {
        "_key": "37405-4564665-7",
        "dob": "2016-09-12",
        "name": "Kashif Iftikhar",
        "favorite_hobby": {
            "name": "Programming",
            "equipment": [{"name": "computer", "price": 500}, {"name": "chair", "price": 100}],
        },
    }
    new_person = Person(**pd)
    assert "37405-4564665-7" == new_person.key_
    assert "Kashif Iftikhar" == new_person.name
    assert "2016-09-12" == new_person.dob.isoformat()
    assert "Programming" == new_person.favorite_hobby.name
    assert "computer" == new_person.favorite_hobby.equipment[0].name


def test_class_inheritance():
    class SuperCar(Car):
        __collection__ = "supercar"

    bmw_m3_e92 = SuperCar(**{"make": "BMW", "model": "M3 E92", "year": "2009"})

    assert bmw_m3_e92.__collection__ == "supercar"


# def test_json_schema(self):
#     assert False
