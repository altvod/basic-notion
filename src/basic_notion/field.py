from __future__ import annotations

from typing import ClassVar, Generic, Optional, Type, TYPE_CHECKING, TypeVar, overload

from basic_notion.property import (
    PageProperty, NumberProperty, CheckboxProperty,
    SelectProperty, MultiSelectProperty,
    TitleProperty, RichTextProperty,
    EmailProperty, UrlProperty, PhoneNumberProperty,
    DateProperty,
)
from basic_notion.property_schema import (
    PropertySchema, NumberPropertySchema, CheckboxPropertySchema,
    SelectPropertySchema, MultiSelectPropertySchema,
    TitlePropertySchema, RichTextPropertySchema,
    EmailPropertySchema, UrlPropertySchema, PhoneNumberPropertySchema,
    DatePropertySchema,
)
from basic_notion.utils import get_from_dict

if TYPE_CHECKING:
    from basic_notion.base import NotionItemBase  # noqa


_OWNER_TV = TypeVar('_OWNER_TV', bound='NotionItemBase')
_PROP_SCHEMA_TV = TypeVar('_PROP_SCHEMA_TV', bound=PropertySchema)
_PROP_TV = TypeVar('_PROP_TV', bound=PageProperty)


class NotionField(Generic[_PROP_SCHEMA_TV, _PROP_TV]):
    """
    Descriptor that represents Notion object attributes.
    The returned value is an instance of ``PropertySchema``
    if called on a class and a ``PageProperty`` if called
    on an instance.
    """

    __slots__ = ('__property_name', '__root_key', '__key')

    PROP_SCHEMA_CLS: ClassVar[Type[_PROP_SCHEMA_TV]]
    PROP_CLS: ClassVar[Type[_PROP_TV]]

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

    @overload
    def __get__(self, instance: None, owner: Type[_OWNER_TV]) -> PropertySchema: ...

    @overload
    def __get__(self, instance: Optional[_OWNER_TV], owner: Type[_OWNER_TV]) -> _PROP_TV: ...

    def __get__(self, instance, owner):
        if instance is None:
            return self.PROP_SCHEMA_CLS(property_name=self._property_name)  # TODO: schema data

        value_data = get_from_dict(instance.data, self.__key)
        return self.PROP_CLS(data=value_data, property_name=self._property_name)


class NumberField(NotionField[NumberPropertySchema, NumberProperty]):
    __slots__ = ()

    PROP_SCHEMA_CLS = NumberPropertySchema
    PROP_CLS = NumberProperty


class CheckboxField(NotionField[CheckboxPropertySchema, CheckboxProperty]):
    __slots__ = ()

    PROP_SCHEMA_CLS = CheckboxPropertySchema
    PROP_CLS = CheckboxProperty


class SelectField(NotionField[SelectPropertySchema, SelectProperty]):
    __slots__ = ()

    PROP_SCHEMA_CLS = SelectPropertySchema
    PROP_CLS = SelectProperty


class MultiSelectField(NotionField[MultiSelectPropertySchema, MultiSelectProperty]):
    __slots__ = ()

    PROP_SCHEMA_CLS = MultiSelectPropertySchema
    PROP_CLS = MultiSelectProperty


class TitleField(NotionField[TitlePropertySchema, TitleProperty]):
    __slots__ = ()

    PROP_SCHEMA_CLS = TitlePropertySchema
    PROP_CLS = TitleProperty


class RichTextField(NotionField[RichTextPropertySchema, RichTextProperty]):
    __slots__ = ()

    PROP_SCHEMA_CLS = RichTextPropertySchema
    PROP_CLS = RichTextProperty


class EmailField(NotionField[EmailPropertySchema, EmailProperty]):
    __slots__ = ()

    PROP_SCHEMA_CLS = EmailPropertySchema
    PROP_CLS = EmailProperty


class UrlField(NotionField[UrlPropertySchema, UrlProperty]):
    __slots__ = ()

    PROP_SCHEMA_CLS = UrlPropertySchema
    PROP_CLS = UrlProperty


class PhoneNumberField(NotionField[PhoneNumberPropertySchema, PhoneNumberProperty]):
    __slots__ = ()

    PROP_SCHEMA_CLS = PhoneNumberPropertySchema
    PROP_CLS = PhoneNumberProperty


class DateField(NotionField[DatePropertySchema, DateProperty]):
    __slots__ = ()

    PROP_SCHEMA_CLS = DatePropertySchema
    PROP_CLS = DateProperty
