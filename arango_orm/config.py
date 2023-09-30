from typing import TypedDict, Literal


class IndexSpec(TypedDict):
    index_type: Literal["hash", "fulltext", "skiplist", "geo", "persistent", "ttl"]
    fields: list[str]
    unique: bool
    sparse: bool


class CollectionArguments(TypedDict):
    sync: bool
    system: bool
    edge: bool
    key_generator: Literal["traditional", "autoincrement"]
    user_keys: bool
    key_increment: int
    key_offset: int
    shard_fields: list[str]
    shard_count: int
    replication_factor: int
    shard_like: str
    sync_replication: bool
    enforce_replication_factor: bool
    sharding_strategy: Literal[
        "community-compat",
        "enterprise-compat",
        "enterprise-smart-edge-compat",
        "hash",
        "enterprise-hash-smart-edge",
    ]
    smart_join_attribute: str
    write_concern: int
    schema: dict
    computedValues: list



class CollectionConfig(TypedDict):
    """
    Collection configuration options.
    """

    key_field: str
    indexes: list[IndexSpec]
    col_args: CollectionArguments
