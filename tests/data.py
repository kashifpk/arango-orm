from typing import Literal
from datetime import datetime, date

# from arango_orm.fields import String, Date, Integer, Boolean, List, Nested, Number, Float
# from arango_orm import Collection, Relation, Graph, GraphConnection
from pydantic import BaseModel, ConfigDict, Field
from arango_orm.references import relationship, graph_relationship, Relationship
from arango_orm import Collection, Relation, Graph, GraphConnection



class Person(Collection):
    __collection__ = "persons"
    _index = [{"type": "hash", "unique": False, "fields": ["name"]}]

    class Hobby(BaseModel):
        class Equipment(BaseModel):
            name: str = None
            price: int = None

        name: str = None
        equipment: list[Equipment] = None

    key_: str = Field(None, alias="_key")
    name: str
    age: int | None = None
    dob: date | None = None
    is_staff: bool = False
    favorite_hobby: Hobby | None = None
    # hobby = List(Nested(Hobby.schema()), required=False, allow_none=True, default=None)
    cars: list["Car"] = relationship(__name__ + ".Car", "key_", target_field="owner_key")
    cars_no_cache: list["Car"] = relationship(__name__ + ".Car", "key_", target_field="owner_key", cache=False)

    @property
    def is_adult(self):
        return self.age and self.age >= 18

    def __str__(self):
        return "<Person(" + self.name + ")>"


class Car(Collection):
    __collection__ = "cars"

    model_config = ConfigDict(extra="allow")  # _allow_extra_fields = True (old style)

    make: str
    model: str
    year: int
    owner_key: str | None = None

    owner: Person = relationship(Person, "owner_key")
    owner_no_cache: Person = relationship(Person, "owner_key", cache=False)

    def __str__(self):
        return "<Car({} - {} - {})>".format(self.make, self.model, self.year)


persons = [
    Person(key_="kashif", name="Kashif Iftikhar", dob=date.today()),
    Person(key_="azeen", name="Azeen Kashif", dob=date.today()),
]

cars = [
    Car(make="Honda", model="Civic", year=1984, owner_key="kashif"),
    Car(make="Honda", model="Civic", year=1995, owner_key="kashif"),
    Car(make="Honda", model="Civic", year=1998, owner_key="Azeen"),
    Car(make="Honda", model="Civic", year=2001, owner_key="Azeen"),
    Car(make="Toyota", model="Corolla", year=1988, owner_key="kashif"),
    Car(make="Toyota", model="Corolla", year=2004, owner_key="Azeen"),
    Car(make="Mitsubishi", model="Lancer", year=2005, owner_key="Azeen"),
]


# Graph data
class Student(Collection):
    __collection__ = "students"

    # key_ is registration number
    name: str
    age: int = None

    def __str__(self):
        return "<Student({})>".format(self.name)


class Teacher(Collection):
    __collection__ = "teachers"

    key_: str = Field(..., alias="_key")  # employee id
    name: str

    def __str__(self):
        return "<Teacher({})>".format(self.name)


class Subject(Collection):
    __collection__ = "subjects"

    key_: str = Field(..., alias="_key")  # subject code
    name: str
    credit_hours: int | None = None
    has_labs: bool = True

    def __str__(self):
        return "<Subject({})>".format(self.name)


class SpecializesIn(Relation):
    __collection__ = "specializes_in"

    expertise_level: Literal["expert", "medium", "basic"]

    def __str__(self):
        return "<SpecializesIn(key_={}, expertise_level={}, _from={}, _to={})>".format(
            self.key_, self.expertise_level, self.from_, self.to_
        )


class Area(Collection):
    __collection__ = "areas"

    key_: str = Field(..., alias="_key")  # area name


# DUMMY COLLECTIONS #


class DummyFromCol1(Collection):
    __collection__ = "dummy_from_col_1"

    key_: str = Field(..., alias="_key")


class DummyFromCol2(Collection):
    __collection__ = "dummy_from_col_2"

    key_: str = Field(..., alias="_key")


class DummyRelation(Relation):
    __collection__ = "dummy_relation"


class DummyToCol1(Collection):
    __collection__ = "dummy_to_col_1"


class DummyToCol2(Collection):
    __collection__ = "dummy_to_col_2"


class UniversityGraph(Graph):
    __graph__ = "university_graph"

    graph_connections: list[GraphConnection] = [
        # Using general Relation class for relationship
        GraphConnection(Student, Relation("studies"), Subject),
        GraphConnection(Teacher, Relation("teaches"), Subject),
        # Using specific classes for vertex and edges
        GraphConnection(Teacher, SpecializesIn, Subject),
        GraphConnection([Teacher, Student], Relation("resides_in"), Area),
    ]


students_data = [
    Student(key_="S1001", name="John Wayne", age=30),
    Student(key_="S1002", name="Lilly Parker", age=22),
    Student(key_="S1003", name="Cassandra Nix", age=25),
    Student(key_="S1004", name="Peter Parker", age=20),
]

teachers_data = [
    Teacher(key_="T001", name="Bruce Wayne"),
    Teacher(key_="T002", name="Barry Allen"),
    Teacher(key_="T003", name="Amanda Waller"),
]

subjects_data = [
    Subject(
        key_="ITP101",
        name="Introduction to Programming",
        credit_hours=4,
        has_labs=True,
    ),
    Subject(key_="CS102", name="Computer History", credit_hours=3, has_labs=False),
    Subject(
        key_="CSOOP02",
        name="Object Oriented Programming",
        credit_hours=3,
        has_labs=True,
    ),
]

areas_data = [
    Area(key_="Gotham"),
    Area(key_="Metropolis"),
    Area(key_="StarCity"),
]

specializations_data = [
    SpecializesIn(from_="teachers/T001", to_="subjects/ITP101", expertise_level="medium")
]


# # FOR v, e, p IN 1..3 INBOUND 'areas/gotham'
# # GRAPH 'university_graph'
# # RETURN p

# Inheritance data
class Citizen(Collection):
    __collection__ = 'citizens'

    key_: str = Field(..., alias="_key")  # citizen identification number
    name: str
    dob: date


class Scientist(Citizen):

    degress: list[str]
    research_field: str


class Employee(Citizen):

    base_salary: int | None = None


# class Owner(Collection):
#     __collection__ = "owner"

#     key_ = String()
#     name = String()


# class Vehicle(Collection):
#     __collection__ = "vehicle"

#     _inheritance_field = "discr"
#     _inheritance_mapping = {
#         'Bike': 'moto',
#         'Truck': 'truck'
#     }

#     key_ = String()
#     brand = String()
#     model = String()
#     discr = String(required=True)


# class Bike(Vehicle):
#     motor_size = Float()


# class Truck(Vehicle):
#     traction_power = Float()


# class Own(Relation):
#     __collection__ = "own"


# class OwnershipGraph(Graph):
#     __graph__ = "ownership_graph"

#     graph_connections = [
#         GraphConnection(Owner, Own, Vehicle)
#     ]


# owner_data = [
#     Owner(key_='001', name="John Doe"),
#     Owner(key_='002', name="Billy the Kid"),
#     Owner(key_='003', name="Lucky Luke")
# ]

# vehicle_data = [
#     Bike(key_='001', motor_size=125, brand='Harley Davidson', model='Hummer'),
#     Truck(key_='002', traction_power=520, brand='Renault Trucks', model='T High')
# ]

# own_data = [
#     Own(_from='owner/001', _to='vehicle/001'),
#     Own(_from='owner/002', _to='vehicle/002'),
#     Own(_from='owner/003', _to='vehicle/001'),
#     Own(_from='owner/003', _to='vehicle/002')
# ]


# class Owner2(Collection):
#     __collection__ = "owner"

#     key_ = String()
#     name = String()


# class Vehicle2(Collection):
#     __collection__ = "vehicle"

#     key_ = String()
#     brand = String()
#     model = String()


# class Bike2(Vehicle2):
#     motor_size = Float()


# class Truck2(Vehicle2):
#     traction_power = Float()


# class Own2(Relation):
#     __collection__ = "own"


# class OwnershipGraph2(Graph):
#     __graph__ = "ownership_graph"

#     graph_connections = [
#         GraphConnection(Owner2, Own2, Vehicle2)
#     ]

#     def inheritance_mapping_resolver(self, col_name: str, doc_dict: dict = {}):
#         if col_name == 'vehicle':
#             if 'traction_power' in doc_dict:
#                 return Truck2
#             else:
#                 return Bike2

#         return self.vertices[col_name]


# owner_data2 = [
#     Owner2(key_='001', name="John Doe"),
#     Owner2(key_='002', name="Billy the Kid"),
#     Owner2(key_='003', name="Lucky Luke")
# ]

# vehicle_data2 = [
#     Bike2(key_='001', motor_size=125, brand='Harley Davidson', model='Hummer'),
#     Truck2(key_='002', traction_power=520, brand='Renault Trucks', model='T High')
# ]

# own_data2 = [
#     Own2(_from='owner/001', _to='vehicle/001'),
#     Own2(_from='owner/002', _to='vehicle/002'),
#     Own2(_from='owner/003', _to='vehicle/001'),
#     Own2(_from='owner/003', _to='vehicle/002')
# ]


# # Multiple inheritance data

# class People(Collection):
#     __collection__ = "people"

#     key_ = String()
#     name = String()


# class Parent(People):
#     work = String()


# class Child(People):
#     hobby = String()


# class Boy(People):
#     personality = String()


# class Girl(People):
#     hair_color = String()


# class Father(Parent, Boy):
#     wife_name = String()


# class Mother(Parent, Girl):
#     husband_name = String()


# class Son(Child, Boy):
#     sister_name = String()


# class Daughter(Child, Girl):
#     brother_name = String()


# class PeopleGraph(Graph):
#     __graph__ = "people_graph"

#     graph_connections = [
#         GraphConnection(People, Relation('resides_with'), People)
#     ]

# people_data = [
#     Father(key_='001', name='Homer', work='Nuclear supervisor', personality='lazy', wife_name='Marge'),
#     Mother(key_='002', name='Marge', work='None', hair_color='blue', husband_name='Homer'),
#     Son(key_='003', name='Bart', hobby='Skateboard', personality='playful', sister_name='Lisa'),
#     Daughter(key_='004', name='Lisa', hobby='Saxophone', hair_color='yellow', brother_name='Bart')
# ]
