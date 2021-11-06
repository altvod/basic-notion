from __future__ import annotations
import abc

from typing import Any, ClassVar, Generic, TYPE_CHECKING, Type, TypeVar, Union

import attr

if TYPE_CHECKING:
    from basic_notion.base import NotionItemBase  # noqa
    from basic_notion.parent import Parent  # noqa
    from basic_notion.page import NotionPage  # noqa
    from basic_notion.property import (
        PageProperty, PaginatedProperty,  # noqa
        TextProperty, CheckboxProperty, NumberProperty,  # noqa
        SelectProperty, MultiSelectProperty,  # noqa
    )


_ITEM_CLS_TV = TypeVar('_ITEM_CLS_TV', bound=Type['NotionItemBase'])


@attr.s(frozen=True)
class DataGenBase(abc.ABC, Generic[_ITEM_CLS_TV]):
    _item_cls: Type[_ITEM_CLS_TV] = attr.ib(kw_only=True)

    def __call__(self, *args, **kwargs) -> dict:
        return self.generate(*args, **kwargs)

    @abc.abstractmethod
    def generate(self, *args, **kwargs: Any) -> dict:
        raise NotImplementedError


@attr.s(frozen=True)
class ParentDataGen(DataGenBase[Type['Parent']]):
    def generate(self, *args, **kwargs: Any) -> dict:
        """
        Requires either ``database_id`` or ``page_id`` keyword argument,
        depending of the class of the parent.
        """
        assert not args
        return {
            self._item_cls.OBJECT_TYPE_STR: kwargs[self._item_cls.OBJECT_TYPE_STR]  # type: ignore
        }


@attr.s(frozen=True)
class PageDataGen(DataGenBase[Type['NotionPage']]):
    def generate(self, *args, **kwargs: Any) -> dict:
        parent = kwargs.pop('parent')

        property_data: dict[str, Union[dict, list]] = {}
        fields: dict[str, PageProperty] = self._item_cls.get_class_fields()  # type: ignore
        for property_attr_name, property_value in kwargs.items():
            if property_attr_name not in fields:
                raise ValueError(
                    f'Unknown property attribute "{property_attr_name}" '
                    f'for NotionPage class {self._item_cls.__name__}'
                )
            field_property = fields[property_attr_name]
            property_name = field_property.property_name
            property_data[property_name] = field_property.generate(property_value)

        return {
            'parent': parent,
            'properties': property_data,
        }


@attr.s(frozen=True)
class PropertyDataGenBase(DataGenBase):
    PROPERTY_VALUE_TYPE: ClassVar[Union[Type, tuple[Type, ...]]]

    def generate(self, *args, **kwargs: Any) -> dict:
        assert len(args) == 1 and not kwargs
        value = args[0]
        if not isinstance(value, self.PROPERTY_VALUE_TYPE):  # type: ignore
            prop_type_str = (
                self.PROPERTY_VALUE_TYPE.__name__
                if isinstance(self.PROPERTY_VALUE_TYPE, type)
                else tuple(item.__name__ for item in self.PROPERTY_VALUE_TYPE)
            )
            raise TypeError(
                f'Value for {self._item_cls.__name__} must be '
                f'a {prop_type_str}, '
                f'got {type(value).__name__}'
            )

        data = self.make_value_data(value)
        if self._item_cls.OBJECT_TYPE_STR:  # type: ignore
            data = {self._item_cls.OBJECT_TYPE_STR: data}  # type: ignore
        assert isinstance(data, dict)
        return data

    @abc.abstractmethod
    def make_value_data(self, value: Any) -> Any:
        raise NotImplementedError


@attr.s(frozen=True)
class PlainPropertyDataGenBase(PropertyDataGenBase):
    PROPERTY_VALUE_KEY: ClassVar[str]

    def make_value_data(self, value: Any) -> Any:
        return {self.PROPERTY_VALUE_KEY: value}


@attr.s(frozen=True)
class PaginatedPropertyDataGen(PropertyDataGenBase):
    PROPERTY_VALUE_TYPE = list

    def make_value_data(self, value: Any) -> list:
        from basic_notion.property import PaginatedProperty
        assert isinstance(value, list)
        assert issubclass(self._item_cls, PaginatedProperty)
        return [
            self._item_cls.ITEM_CLS.generate(prop_item_value)
            for prop_item_value in value
        ]


@attr.s(frozen=True)
class TextPropertyDataGen(PlainPropertyDataGenBase):
    PROPERTY_VALUE_TYPE = str
    PROPERTY_VALUE_KEY = 'content'


@attr.s(frozen=True)
class CheckboxPropertyDataGen(PlainPropertyDataGenBase):
    PROPERTY_VALUE_TYPE = bool
    PROPERTY_VALUE_KEY = 'checkbox'


@attr.s(frozen=True)
class NumberPropertyDataGen(PlainPropertyDataGenBase):
    PROPERTY_VALUE_TYPE = (int, float)
    PROPERTY_VALUE_KEY = 'number'


@attr.s(frozen=True)
class SelectPropertyDataGen(PlainPropertyDataGenBase):
    PROPERTY_VALUE_TYPE = str
    PROPERTY_VALUE_KEY = 'name'
