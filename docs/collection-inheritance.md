# Inheritance

Same collection can be used to store data for more specific entities of the same type. Instead of creating separate collections to store the more specialized data, it can be stored in the same collection and multiple data models can point to the same collection.

## Example

```python
from arango_orm import Collection
from pydantic import Field
from arango import ArangoClient
from arango_orm import Database

client = ArangoClient(hosts='http://localhost:8529')
test_db = client.db('test', username='test', password='test')

db = Database(test_db)


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


db.create_collection(Citizen)


unemployed = Citizen(key_="PK-1", name="Sleepy Joe", dob="1990-10-10")
db.add(unemployed)

employee = Employee(key_="PK-2", name="Regular Joe", dob="1990-11-10", base_salary=160000)
db.add(employee)

scientist = Scientist(
    key_="PK-3",
    name="Genius Joe",
    dob="1990-12-10",
    degress=["PhD", "Masters"],
    research_field="Physics",
)
db.add(scientist)

r1: Citizen = test_db.query(Citizen).by_key('PK-1')
print(r1.name)  # Sleepy Joe
print(r1.dob.isoformat())  # 1990-10-10

r2: Citizen = test_db.query(Citizen).by_key('PK-2')
print(r2.name)  # 'Regular Joe'
print(r2.dob.isoformat())  # 1990-11-10
assert 'base_salary' not in r2.model_dump()  # True

r3: Citizen = test_db.query(Citizen).by_key('PK-3')
print(r3.name)  # Genius Joe
print(r3.dob.isoformat())  # 1990-12-10
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
```
