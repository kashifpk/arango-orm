# Introduction

Welcome to Arango ORM (Python ORM Layer For ArangoDB)

**arango_orm** is a python ORM layer inspired by SQLAlchemy but aimed to work
with the multi-model database [ArangoDB](https://www.arangodb.com). It supports accessing both collections
and graphs using the ORM. The actual communication with the database is done
using [python-arango](https://docs.python-arango.com) (the database driver for accessing arangodb from
python) and object serialization, validation, etc is handled by [pydantic](https://docs.pydantic.dev/latest/).

## Installation

```shell
python -m pip install arango-orm
```

## Differences from Pre 1.x versions

- Based on pydantic2 instead of marshmallow
- Type hints for better IDE experience
- Faster and generally simpler

## Native vs ORM field names

ArangoDB has special field names (`_key`, `_from`, `_to`) but pydantic ignores instance attributes that start with underscore. So internally in arango-orm collections the `key_` field is `key_`, `_from` is `from_` and `_to` is `to_`. However setting the data still works with both styles thanks to pydantic field aliases.
