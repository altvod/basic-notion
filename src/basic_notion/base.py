from __future__ import annotations

import abc
from collections import ChainMap
from typing import Any, ClassVar, Optional, Type, TypeVar

import attr

from basic_notion import exc
from basic_notion.utils import set_to_dict, del_from_dict


def _get_attr_keys_for_cls(
        members: dict[str, Any],
        only_editable: bool = False,
        only_derived: bool = False,
) -> dict[str, tuple[str, ...]]:
    from basic_notion.attr import ItemAttrDescriptor

    result: dict[str, tuple[str, ...]] = dict()
    for name, prop in members.items():
        if not isinstance(prop, ItemAttrDescriptor):
            continue
        if only_editable and not prop.editable:
            continue
        if only_derived and not prop.derived:
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
        editable_keys_name = '__notion_editable_keys__'
        derived_keys_name = '__notion_derived_keys__'
        base_attr_key_maps = tuple(
            getattr(base, attr_keys_name)  # type: ignore
            for base in bases if type(base) is cls
        )
        base_editable_key_maps = tuple(
            getattr(base, editable_keys_name)  # type: ignore
            for base in bases if type(base) is cls
        )
        base_derived_key_maps = tuple(
            getattr(base, derived_keys_name)  # type: ignore
            for base in bases if type(base) is cls
        )
        attr_keys = dict(ChainMap(_get_attr_keys_for_cls(dct), *base_attr_key_maps))
        editable_keys = dict(ChainMap(_get_attr_keys_for_cls(dct, only_editable=True), *base_editable_key_maps))
        derived_keys = dict(ChainMap(_get_attr_keys_for_cls(dct, only_derived=True), *base_derived_key_maps))
        # Added to __dict__
        dct[attr_keys_name] = attr_keys
        dct[editable_keys_name] = editable_keys
        dct[derived_keys_name] = derived_keys
        new_cls = super().__new__(cls, name, bases, dct)
        return new_cls


_ITEM_TV = TypeVar('_ITEM_TV', bound='NotionItemBase')


@attr.s(slots=True)
class NotionItemBase(metaclass=NotionItemBaseMetaclass):
    __notion_attr_keys__: dict[str, tuple[str, ...]] = None  # type: ignore  # defined in metaclass
    __notion_editable_keys__: dict[str, tuple[str, ...]] = None  # type: ignore  # defined in metaclass
    __notion_derived_keys__: dict[str, tuple[str, ...]] = None  # type: ignore  # defined in metaclass

    OBJECT_TYPE_KEY_STR: ClassVar[str] = ''
    OBJECT_TYPE_STR: ClassVar[str] = ''

    _data: Optional[dict[str, Any]] = attr.ib(kw_only=True, default=None)

    @classmethod
    @property
    def attr_keys(cls) -> dict[str, tuple[str, ...]]:
        return cls.__notion_attr_keys__

    @classmethod
    @property
    def editable_keys(cls) -> dict[str, tuple[str, ...]]:
        return cls.__notion_editable_keys__

    @classmethod
    @property
    def derived_keys(cls) -> dict[str, tuple[str, ...]]:
        return cls.__notion_derived_keys__

    @property
    def data(self) -> dict:
        if self._data is None:
            raise exc.ItemHasNoData(f'Object {type(self).__name__} has no data')
        return self._data

    @classmethod
    def _make_inst_attr_dict(cls, kwargs: dict[str, Any]) -> dict:
        data: dict[str, Any] = {}
        for name, key in cls.editable_keys.items():  # type: ignore
            if name not in kwargs:
                continue

            value = kwargs[name]

            # Get attr descriptor and its `set_converter` callable
            # (if it exists) to convert the value into its serializable form
            prop = getattr(cls, name)
            set_converter = prop.set_converter
            if set_converter is not None:
                value = set_converter(value)

            set_to_dict(data, key, value)

        return data

    @classmethod
    def _make_inst_dict(cls, kwargs: dict[str, Any]) -> dict:
        data = {}
        if cls.OBJECT_TYPE_KEY_STR and cls.OBJECT_TYPE_STR:
            data[cls.OBJECT_TYPE_KEY_STR] = cls.OBJECT_TYPE_STR

        data.update(cls._make_inst_attr_dict(kwargs))
        return data

    @classmethod
    def make(cls: Type[_ITEM_TV], **kwargs: Any) -> _ITEM_TV:
        """Generate instance from attributes"""
        data = cls._make_inst_dict(kwargs)
        return cls(data=data)

    def clear_derived_attrs(self) -> None:
        for name, other_key in self.attr_keys.items():
            if name in self.derived_keys:
                # Is not editable
                del_from_dict(self.data, other_key)
