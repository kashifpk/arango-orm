# Referencing objects from other collection

The [relationship][arango_orm.references.relationship] links one of the collection fields to data in other collections. The referenced object can then be accessed as a property of the current object.

## Example

```python
    from pydantic import BaseModel, ConfigDict, Field
    from arango_orm.references import relationship, graph_relationship, Relationship
    from arango_orm import Collection, Relation, Graph, GraphConnection


    class Person(Collection):
        __collection__ = "persons"
        key_: str = Field(None, alias="_key")
        name: str
        cars: list["Car"] = relationship(__name__ + ".Car", "key_", target_field="owner_key")


    class Car(Collection):
        __collection__ = "cars"

        make: str
        model: str
        year: int
        owner_key: str | None = None

        owner: Person = relationship(Person, "owner_key")

    db.add(Person(key_="ABC", name="Mr. ABC"))
    db.add(Car(make="Honda", model="Civic", year=1984, owner_key="ABC"))
    db.add(Car(make="Toyota", model="Corolla", year=1988, owner_key="ABC"))

    p = db.query(Person).by_key('ABC')
    print(len(p.cars))  # 4

    car1 = db.query(Car).first()
    print(car1.owner.name)  # Mr. ABC
```

### Caching

The referenced object is cached in the current object when the current object is fetched from the database. Future access to the reference does not require a call to the database. This behavior can be disabled by passing `cache=False` to the `relationship` function.
