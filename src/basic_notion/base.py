from __future__ import annotations

import abc
from collections import ChainMap
from typing import Any, ClassVar, Optional, TYPE_CHECKING, Type

import attr

from basic_notion import exc

if TYPE_CHECKING:
    from basic_notion.data_gen import DataGenBase


def _get_attr_keys_for_cls(members: dict[str, Any]) -> dict[str, tuple[str, ...]]:
    from basic_notion.attr import ItemAttrDescriptor

    result: dict[str, tuple[str, ...]] = dict()
    for name, prop in members.items():
        if not isinstance(prop, ItemAttrDescriptor):
            continue
        attr_key: tuple[str, ...]
        try:
            attr_key = prop.key
        except AttributeError:
            attr_key = (name,)
        result[name] = attr_key

    return result


class NotionItemBaseMetaclass(abc.ABCMeta):
    # abc.ABCMeta is needed here for the abc.ABC functionality

    """Metaclass that adds ``__notion_attr_keys__`` to all ``NotionItemBase`` subclasses"""

    def __new__(cls, name: str, bases: tuple[type, ...], dct: dict):
        attr_keys_name = '__notion_attr_keys__'
        base_attr_key_maps = tuple(
            getattr(base, attr_keys_name)  # type: ignore
            for base in bases if type(base) is cls
        )
        attr_keys = dict(ChainMap(_get_attr_keys_for_cls(dct), *base_attr_key_maps))
        dct[attr_keys_name] = attr_keys
        new_cls = super().__new__(cls, name, bases, dct)
        return new_cls


@attr.s(slots=True)
class NotionItemBase(metaclass=NotionItemBaseMetaclass):
    __notion_attr_keys__: dict[str, tuple[str, ...]]  # defined in metaclass

    OBJECT_TYPE_KEY_STR: ClassVar[str] = ''
    OBJECT_TYPE_STR: ClassVar[str] = ''
    DATA_GEN_CLS: ClassVar[Optional[Type[DataGenBase]]] = None

    _data: Optional[dict[str, Any]] = attr.ib(kw_only=True, default=None)

    def __attrs_post_init__(self) -> None:
        if self._data is not None and self.OBJECT_TYPE_KEY_STR and self.OBJECT_TYPE_STR:
            assert self._data[self.OBJECT_TYPE_KEY_STR] == self.OBJECT_TYPE_STR

    @classmethod
    @property
    def attr_keys(cls) -> dict[str, tuple[str, ...]]:
        return cls.__notion_attr_keys__

    @property
    def data(self) -> dict:
        if self._data is None:
            raise exc.ItemHasNoData(f'Object {type(self).__name__} has no data')
        return self._data

    @classmethod
    def generate(cls, *args, **kwargs) -> dict:
        assert cls.DATA_GEN_CLS is not None
        return cls.DATA_GEN_CLS(item_cls=cls).generate(*args, **kwargs)
