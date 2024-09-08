# Collections

A collection class definition represents a database collection.

Define models to represent your data. Models extend the [Collection][arango_orm.collections.Collection] base class which is an extension of the pydantic `BaseModel` class. So all functionality provided by pydantic models is available. The same model class can be used for ORM and for defining API request/response structures.

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


## Collection Configuration

### Defining Indexes

Define extra indexes for your data using CollectionConfig.

```python
class Person(Collection):

    __collection__ = "people"

    _collection_config = CollectionConfig(
        indexes=[
            IndexSpec(index_type='hash', fields=["_key"], unique=True, sparse=False),
        ]
    )

    name: str
    ssn: str
```
