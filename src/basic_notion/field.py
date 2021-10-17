from typing import ClassVar, Generic, Optional, Type, TypeVar

from basic_notion.base import NotionItem
from basic_notion.property import (
    PageProperty, TextProperty, NumberProperty, CheckboxProperty,
    SelectProperty, MultiSelectProperty, TitleProperty,
)


_OWNER_TV = TypeVar('_OWNER_TV', bound=NotionItem)
_PROP_VALUE_TV = TypeVar('_PROP_VALUE_TV', bound=PageProperty)


class Field(Generic[_PROP_VALUE_TV]):
    """
    Descriptor that represents Notion object attributes.
    The returned value is an instance of the ``PageProperty``
    """

    __slots__ = ('__property_name', '__type_name')

    _PROP_CLS: ClassVar[Type[_PROP_VALUE_TV]]

    def __init__(self, property_name: Optional[str] = None) -> None:
        self.__property_name = property_name

    def __set_name__(self, owner: Type[_OWNER_TV], name: str) -> None:
        """
        Set the ``self.__attribute`` to the property's name
        if the attr name wasn't specified explicitly
        """

        if self.__property_name is None:
            self.__property_name = name

    @property
    def _property_name(self) -> str:
        assert self.__property_name is not None
        return self.__property_name

    def __get__(self, instance: Optional[_OWNER_TV], owner: Type[_OWNER_TV]) -> PageProperty:
        value_data: Optional[dict] = None
        if instance is not None:
            value_data = instance.properties_data[self._property_name]  # noqa

        return self._PROP_CLS(data=value_data, property_name=self._property_name)


class TextField(Field[TextProperty]):
    _PROP_CLS = TextProperty


class NumberField(Field[NumberProperty]):
    _PROP_CLS = NumberProperty


class CheckboxField(Field[CheckboxProperty]):
    _PROP_CLS = CheckboxProperty


class SelectField(Field[SelectProperty]):
    _PROP_CLS = SelectProperty


class MultiSelectField(Field[MultiSelectProperty]):
    _PROP_CLS = MultiSelectProperty


class TitleField(Field[TitleProperty]):
    _PROP_CLS = TitleProperty
