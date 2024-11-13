#!/usr/bin/env python3
""" Base module"""
from datetime import datetime
from os import path
from typing import TypeVar, List, Iterable
import uuid
import json


DATA = {}
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"


class Base:
    """Base class"""

    def __init__(self, *args: list, **kwargs: dict):
        """Initializes a Base instance"""
        obj_class = str(self.__class__.__name__)
        if DATA.get(obj_class) is None:
            DATA[obj_class] = {}

        self.id = kwargs.get("id", str(uuid.uuid4()))
        if kwargs.get("created_at") is not None:
            self.created_at = datetime.strptime(
                kwargs.get("created_at"), TIMESTAMP_FORMAT
            )
        else:
            self.created_at = datetime.utcnow()
        if kwargs.get("updated_at") is not None:
            self.updated_at = datetime.strptime(
                kwargs.get("updated_at"), TIMESTAMP_FORMAT
            )
        else:
            self.updated_at = datetime.utcnow()

    def __eq__(self, other: TypeVar("Base")) -> bool:
        """Equality op"""
        if not isinstance(Base):
            return False
        if type(self) != type(other):
            return False
        return self.id == other.id

    def to_json(self, for_serialization: bool = False) -> dict:
        """Convert the object a JSON dictionary"""
        result = {}
        for k, v in self.__dict__.items():
            if not for_serialization and k[0] == "_":
                continue
            if type(v) is datetime:
                result[k] = v.strftime(TIMESTAMP_FORMAT)
            else:
                result[k] = v
        return result

    @classmethod
    def load_from_file(cls):
        """Load all objects from file"""
        obj_class = cls.__name__
        file_path = ".db_{}.json".format(obj_class)
        DATA[obj_class] = {}
        if not path.exists(file_path):
            return

        with open(file_path, "r") as f:
            objs_json = json.load(f)
            for obj_id, obj_json in objs_json.items():
                DATA[obj_class][obj_id] = cls(**obj_json)

    @classmethod
    def save_to_file(cls):
        """Save all objects to file"""
        obj_class = cls.__name__
        file_path = ".db_{}.json".format(obj_class)
        objs_json = {}
        for obj_id, obj in DATA[obj_class].items():
            objs_json[obj_id] = obj.to_json(True)

        with open(file_path, "w") as f:
            json.dump(objs_json, f)

    def save(self):
        """Save current object"""
        obj_class = self.__class__.__name__
        self.updated_at = datetime.utcnow()
        DATA[obj_class][self.id] = self
        self.__class__.save_to_file()

    def remove(self):
        """Remove object"""
        obj_class = self.__class__.__name__
        if DATA[obj_class].get(self.id) is not None:
            del DATA[obj_class][self.id]
            self.__class__.save_to_file()

    @classmethod
    def search(cls, attributes: dict = {}) -> List[TypeVar("Base")]:
        """Search all objects with matching attributes"""
        obj_class = cls.__name__

        def search_func(obj):
            if len(attributes) == 0:
                return True
            for k, v in attributes.items():
                if getattr(obj, k) != v:
                    return False
            return True

        return list(filter(search_func, DATA[obj_class].values()))

    @classmethod
    def count(cls) -> int:
        """Count all objects"""
        obj_class = cls.__name__
        return len(DATA[obj_class].keys())

    @classmethod
    def all(cls) -> Iterable[TypeVar("Base")]:
        """Get all objects"""
        return cls.search()

    @classmethod
    def get(cls, id: str) -> TypeVar("Base"):
        """Get one object by ID"""
        obj_class = cls.__name__
        return DATA[obj_class].get(id)
