from __future__ import annotations

from typing import ClassVar, Generic, Optional, Type, TYPE_CHECKING, TypeVar

from basic_notion.property import (
    PageProperty, TextProperty, NumberProperty, CheckboxProperty,
    SelectProperty, MultiSelectProperty, TitleProperty,
)
from basic_notion.utils import get_from_dict

if TYPE_CHECKING:
    from basic_notion.base import NotionItemBase  # noqa


_OWNER_TV = TypeVar('_OWNER_TV', bound='NotionItemBase')
_PROP_VALUE_TV = TypeVar('_PROP_VALUE_TV', bound=PageProperty)


class NotionField(Generic[_PROP_VALUE_TV]):
    """
    Descriptor that represents Notion object attributes.
    The returned value is an instance of the ``PageProperty``
    """

    __slots__ = ('__property_name', '__root_key', '__key')

    PROP_CLS: ClassVar[Type[_PROP_VALUE_TV]]

    __DEFAULT_ROOT_KEY = ('properties',)  # Indicates where to look for the data in the owner object's data

    def __init__(
            self, property_name: Optional[str] = None,
            root_key: tuple[str, ...] = __DEFAULT_ROOT_KEY,
    ) -> None:
        self.__property_name = property_name
        self.__root_key = root_key
        self.__key = root_key
        if property_name is not None:
            self.__key += (property_name,)

    def __set_name__(self, owner: Type[_OWNER_TV], name: str) -> None:
        """
        Set the ``self.__attribute`` to the property's name
        if the attr name wasn't specified explicitly
        """

        if self.__property_name is None:
            self.__property_name = name
        property_name = self.__property_name
        assert property_name is not None
        self.__key = self.__root_key + (property_name,)

    @property
    def _property_name(self) -> str:
        assert self.__property_name is not None
        return self.__property_name

    @property
    def key(self) -> tuple[str, ...]:
        return self.__key

    def __get__(self, instance: Optional[_OWNER_TV], owner: Type[_OWNER_TV]) -> PageProperty:
        value_data: Optional[dict] = None
        if instance is not None:
            value_data = get_from_dict(instance.data, self.__key)

        return self.PROP_CLS(data=value_data, property_name=self._property_name)


class TextField(NotionField[TextProperty]):
    __slots__ = ()

    PROP_CLS = TextProperty


class NumberField(NotionField[NumberProperty]):
    __slots__ = ()

    PROP_CLS = NumberProperty


class CheckboxField(NotionField[CheckboxProperty]):
    __slots__ = ()

    PROP_CLS = CheckboxProperty


class SelectField(NotionField[SelectProperty]):
    __slots__ = ()

    PROP_CLS = SelectProperty


class MultiSelectField(NotionField[MultiSelectProperty]):
    __slots__ = ()

    PROP_CLS = MultiSelectProperty


class TitleField(NotionField[TitleProperty]):
    __slots__ = ()

    PROP_CLS = TitleProperty
