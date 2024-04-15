from typing import Any, TypeVar

from loguru import logger
from sqlalchemy import inspect
from sqlalchemy.orm import collections, DeclarativeMeta, DeclarativeBase
from pydantic.v1.main import ModelMetaclass
from pydantic import BaseModel as PydanticModel

from src.settings import DEBUG

ViewType = TypeVar("ViewType", bound=PydanticModel)
SelectType = TypeVar("SelectType", bound=PydanticModel)
CreateType = TypeVar("CreateType", bound=PydanticModel)
UpdateType = TypeVar("UpdateType", bound=PydanticModel)


class BaseRepository:
    def __init__(
            self,
    ) -> None:
        if DEBUG is False:
            from src.core.domain import test_db_engine
            self.session = test_db_engine.test_session
            self.db = test_db_engine
        else:
            from src.core.domain import db_engine
            self.session = db_engine.session
            self.db = db_engine

    def _pydantic_to_model(
            self,
            obj_in: PydanticModel | dict,
            model: DeclarativeMeta | DeclarativeBase,
    ) -> DeclarativeBase:
        if isinstance(obj_in, PydanticModel):
            obj_in = obj_in.dict(exclude_unset=True)

        if isinstance(model, DeclarativeMeta):
            model = model()

        mapper = inspect(model)

        if hasattr(mapper, "mapper"):
            mapper = mapper.mapper

        for name, field in mapper.relationships.items():
            class_ = field.mapper.class_
            try:
                relation_obj = obj_in.pop(name)
            except KeyError:
                continue

            attr = [] if field.uselist else class_()

            # if attr is None:
            #    attr = [] if field.uselist else class_()

            if field.uselist and not isinstance(relation_obj, list):
                relation_obj = [relation_obj]

            if field.uselist:
                length = len(attr)
                for idx, obj in enumerate(relation_obj):
                    if length > 0:
                        attr[idx] = self._pydantic_to_model(obj, attr[idx])
                    else:
                        attr.append(self._pydantic_to_model(obj, class_))
                    length -= 1
            else:
                attr = self._pydantic_to_model(relation_obj, attr)

            obj_in[name] = attr
        if isinstance(obj_in, dict):
            for field, value in obj_in.items():
                if hasattr(mapper.attrs, field):
                    setattr(model, field, value)

        return model

    def _model_to_dict(self, model: DeclarativeBase) -> dict[str | Any]:
        model_dict = model.__dict__

        for name, field in model_dict.items():

            if isinstance(field, DeclarativeBase):
                model_dict[name] = self._model_to_dict(field)
            elif isinstance(field, collections.InstrumentedList):
                items = []
                for i in list(field):
                    if isinstance(i, DeclarativeBase):
                        items.append(self._model_to_dict(i))
                    else:
                        items.append(i)
                model_dict[name] = items
        return model_dict

    def _model_to_pydantic(
            self,
            model: DeclarativeBase,
            view_model: ModelMetaclass,
    ) -> ViewType | SelectType:
        return view_model.parse_obj(
            self._model_to_dict(model),
        )

    @staticmethod
    def _dict_to_pydantic(
            data: dict,
            view_model: ModelMetaclass,
    ):
        return view_model.parse_obj(
            data
        )

    @staticmethod
    def is_pydantic(obj: object):
        """Checks whether an object is pydantic."""
        return type(obj).__class__.__name__ == "ModelMetaclass"

    def parse_pydantic_schema(self, schema):
        """
            Iterates through pydantic schema and parses nested schemas
            to a dictionary containing SQLAlchemy models.
            Only works if nested schemas have specified the Meta.orm_model.
        """
        parsed_schema = dict(schema)
        for key, value in parsed_schema.items():
            try:
                if isinstance(value, list) and len(value):
                    if self.is_pydantic(value[0]):
                        parsed_schema[key] = [schema.Meta.orm_model(**schema.dict()) for schema in value]
                else:
                    if self.is_pydantic(value):
                        parsed_schema[key] = value.Meta.orm_model(**value.dict())
            except AttributeError:
                raise AttributeError("Found nested Pydantic model but Meta.orm_model was not specified.")
        return parsed_schema
