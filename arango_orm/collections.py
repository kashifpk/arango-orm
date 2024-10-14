from __future__ import annotations
from typing import ClassVar, TYPE_CHECKING, Literal, TypeAlias, Any

if TYPE_CHECKING:
    from .database import Database

    IncEx: TypeAlias = "set[int] | set[str] | dict[int, Any] | dict[str, Any] | None"


from pydantic import BaseModel, Field, ConfigDict, model_serializer
from pydantic.fields import FieldInfo

from .config import CollectionConfig
from .references import Relationship
from .exceptions import DetachedInstanceError


class Collection(BaseModel):
    __collection__ = None

    _safe_list: ClassVar[list[str]] = [
        "__collection__",
        "_safe_list",
        "_annotated_fields"
        "_relations",
        "_index",
        "config_",
        "_collections_from",
        "_collections_to",
        "_object_from",
        "_object_to",
        "_post_process",
        "_pre_process",
        "_fields_info",
        "_fields",
        "_db",
        "_refs",
        "_refs_vals",
        "model_config",  # pydantic configuration attribute
    ]

    _annotated_fields: ClassVar[list[str]] = []

    model_config: ClassVar[dict] = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        ignored_types=(Relationship,),
    )
    _collection_config: ClassVar[dict] = CollectionConfig()
    _dirty: set
    _db: Database | None
    _fields: dict
    _refs: dict
    _refs_vals: dict

    key_: str = Field(None, alias="_key")
    rev_: str = Field(None, alias="_rev")

    def __init__(self, collection_name=None, **kwargs):
        if "_key" in kwargs:
            kwargs["key_"] = kwargs["_key"]
            del kwargs["_key"]

        if "_id" in kwargs:
            del kwargs["_id"]
        # if self._collection_config.get("key_field", None) and 'key_' not in kwargs:
        #     kwargs["key_"] = kwargs[self._collection_config["key_field"]]

        super().__init__(**kwargs)
        if collection_name is not None:
            self.__collection__ = collection_name

        # Determine actual data fields.
        self._fields = {}
        self._refs_vals: dict = {}  # Storage for referenced objects
        self._refs: dict[str, FieldInfo] = {}

        for fname, f in self.model_fields.items():
            if f.default.__class__ in self.model_config.get("ignored_types", []):
                if f.default.__class__ is Relationship:
                    self._refs[fname] = f

                continue

            if fname in self._annotated_fields:
                continue

            self._fields[fname] = f

        self._dirty = set(self._fields.keys())
        self._db = kwargs.get("_db", None)
        if self._db is not None:
            self._dirty = set()

    def __str__(self):
        return f"{self.__class__.__name__}({super().__str__()})"

    @property
    def id_(self) -> str | None:
        if self._key is not None and self.__collection__ is not None:
            return f"{self.__collection__}/{self._key}"

        # if hasattr(self, "_key") and getattr(self, "_key") is not None:
        #     return self.__collection__ + "/" + getattr(self, "_key")

        return None

    @property
    def _id(self) -> str | None:
        return self.id_

    @property
    def _key(self) -> str | None:
        return self.key_

    @_key.setter
    def _key(self, value):
        self.key_ = value

    @property
    def _rev(self) -> str | None:
        return self.rev_

    @_rev.setter
    def _rev(self, value):
        self.rev_ = value

    def __setattr__(self, attr, value):
        a_real = attr

        # if attr == self.config_.get("key_field", None):
        #     a_real = "key_"

        if attr == "_id":
            return

        if "_key" == attr:
            a_real = "key_"

        super().__setattr__(a_real, value)

        if a_real not in self.model_fields_set:
            return

        self._dirty.add(a_real)

    def __getattribute__(self, item: str):
        if item in ["_id", "id_"]:
            return super().__getattribute__("id_")

        if item == "_key":
            return super().__getattribute__("key_")

        if item.startswith(("_", "model_") or item in self._annotated_fields):
            return super().__getattribute__(item)

        if item in self._safe_list:
            return super().__getattr__(item)

        if item not in self.model_fields:
            raise AttributeError(name=item, obj=self)

        if item not in self._refs:
            return super().__getattribute__(item)

        # Item is a relationship so we need to lookit up and return proper value.
        if item in self._refs_vals:
            return self._refs_vals[item]

        if self._db is None:
            raise DetachedInstanceError()

        relationship: Relationship = self._refs[item].default
        ReferencedClass = relationship.col_class

        r_val = None
        if "key_" == relationship.target_field:
            r_val = self._db.query(ReferencedClass).by_key(
                getattr(self, relationship.field)
                # super(Collection, self).__getattribute__(ref_class.field)
            )

            if relationship.uselist is True:
                r_val = [
                    r_val,
                ]

        else:
            query = self._db.query(ReferencedClass).filter(
                relationship.target_field + "==@val",
                val=getattr(self, relationship.field),
            )

            if relationship.uselist is False:
                r_val = query.first()

            else:
                # TODO: Handle ref_class.order_by if present
                r_val = query.all()

        if relationship.cache is True:
            self._refs_vals[item] = r_val

        return r_val

    def model_dump(
        self,
        *,
        mode: Literal["json", "python"] | str = "python",
        include: IncEx = None,
        exclude: IncEx = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> dict[str, Any]:
        exclude = exclude or set()
        exclude_fields = {"_db", "_refs"}
        if exclude:
            exclude = set(exclude)
            exclude.update(exclude_fields)
        else:
            exclude = exclude_fields

        for fname in self.model_fields:
            if fname not in self._fields:
                exclude.add(fname)

        return super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
        )


class Relation(Collection):
    from_: str | None = Field(None, alias="_from")
    to_: str | None = Field(None, alias="_to")
    _collections_from: Collection | list[Collection] | None
    _collections_to: Collection | list[Collection] | None

    def __init__(self, collection_name=None, **kwargs):
        if "_from" in kwargs:
            kwargs["from_"] = kwargs["_from"]
            del kwargs["_from"]

        if "_to" in kwargs:
            kwargs["to_"] = kwargs["_to"]
            del kwargs["_to"]

        super().__init__(collection_name=collection_name, **kwargs)

        if "_collections_from" in kwargs:
            self._collections_from = kwargs["_collections_from"]
            del kwargs["_collections_from"]
        else:
            self._collections_from = None

        if "_collections_to" in kwargs:
            self._collections_to = kwargs["_collections_to"]
            del kwargs["_collections_to"]
        else:
            self._collections_to = None

        self._object_from = None
        self._object_to = None

    @property
    def _from(self) -> str | None:
        return self.from_

    @_from.setter
    def _from(self, value):
        self.from_ = value

    @property
    def _to(self) -> str | None:
        return self.to_

    @_to.setter
    def _to(self, value):
        self.to_ = value
