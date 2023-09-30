# Getting started

## Connecting to a database

```python
from arango import ArangoClient
from arango_orm import Database

client = ArangoClient(hosts='http://localhost:8529')
test_db = client.db('test', username='test', password='test')

db = Database(test_db)
```

## Defining models

Define models to represent your data. Models extend the `Collection` base class which is an extension of the pydantic `BaseModel` class. So all functionality provided by pydantic models is available. The same model class can be used for ORM and for defining API request/response structures.

```python
from datetime import date
from arango_orm import Collection


class Student(Collection):

    __collection__ = 'students'

    name: str   # required field
    dob: date | None = None  # optional field
```

All collections have the `key_` field which translates to the `_key` field in arangoDB. If no value is provided for `key_` then one is auto-generated (arango default behavior). If you want to enforce `key_` to be always provided, you can define the key in your model.

```python
from pydantic import Field
from arango_orm import Collection


class MyCollection(Collection):

    __collection__ = 'my_collection'

    key_: str = Field(..., alias="_key")  # required
    name: str
```


## Creating collections in the database

To create database collection based on arango-orm model.

```python
db.create_collection(Student)
```


## Adding records

All the methods to create an orm object from a collection depicted below are valid.

```python
from datetime import date

# Recurd using normal field names and ISO Date format which is automatically
# converted to Date object by pydantic
s1 = Student(key_='12312', name='Student A', dob='2000-10-25')

# Use the _key alias instead of key_ and use proper date object.
s2 = Student(_key='12313', name='Student B', dob=date(year=2000, month=9, day=12))

# missing key_ is automatically generated
s3 = Student(name='Student C')

# Load from a dictionary. dob is None as it is optional.
s4 = Student(**{'key_': '12315', name='Student D'})

# insert a single record into the db
db.add(s1)

# insert multiple records
db.bulk_add([s2, s3, s4])

print(s1._id, s1._key)  # Can use _id and _key they are aliases for id_ and key_
print(s2._id, s2._key)
print(s3.id_, s3.key_)
print(s4.id_, s4.key_)
```

## Get total records in collection

```python
db.query(Student).count()
```

## Get record by key

```python
s = db.query(Student).by_key('12312')
```

## Updating records

```python
s = db.query(Student).by_key('12312')
s.name = 'Anonymous'
db.update(s)
```

## Deleting records

```python
s = db.query(Student).by_key('12312')
db.delete(s)
```

## Get all records in collection

```python
students = db.query(Student).all()
```

## Get first record matching the query

```python
first_student = db.query(Student).first()
```

## Get an iterator for the query

If you don't want to fetch all records from large collections, use an iterator to be more memory efficient.

```python
for rec in db.query(Student).iterator():
    print(rec.key_)
```
