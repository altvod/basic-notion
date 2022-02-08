from __future__ import annotations

from typing import Any, ClassVar, Generic, Type, TypeVar, Union

import attr

from basic_notion.base import NotionItemBase
from basic_notion.filter import (
    FilterFactory, TextFilterFactory, NumberFilterFactory, CheckboxFilterFactory,
    SelectFilterFactory, MultiSelectFilterFactory, DateFilterFactory
)
from basic_notion.property import (
    PageProperty, PropertyList,
    TextProperty,
    NumberProperty, CheckboxProperty,
    SelectProperty, MultiSelectProperty,
    TitleProperty, RichTextProperty,
    EmailProperty, UrlProperty, PhoneNumberProperty,
    DateProperty,
)
from basic_notion.sort import SortFactory
from basic_notion.attr import ItemAttrDescriptor


_FILTER_FACT_TV = TypeVar('_FILTER_FACT_TV', bound=FilterFactory)
_PROP_TV = TypeVar('_PROP_TV', bound=Union[PageProperty, PropertyList])


@attr.s(slots=True)
class PropertySchema(NotionItemBase, Generic[_PROP_TV, _FILTER_FACT_TV]):
    OBJECT_TYPE_KEY_STR = 'type'
    PROP_CLS: ClassVar[Type[PageProperty]]
    FILTER_FACT_CLS: ClassVar[Type[_FILTER_FACT_TV]]
    IS_LIST: ClassVar[bool] = False

    _property_name: str = attr.ib(kw_only=True)

    id: ItemAttrDescriptor[str] = ItemAttrDescriptor()
    type: ItemAttrDescriptor[str] = ItemAttrDescriptor()

    def __attrs_post_init__(self) -> None:
        if not self._data:
            self._data = self.make_data()

    @property
    def property_name(self) -> str:
        """Name of the property within the Notion Page object"""
        return self._property_name

    @property
    def filter(self) -> _FILTER_FACT_TV:
        """Create a ``FilterFactory`` tailored for this property"""
        if self.FILTER_FACT_CLS is None:
            raise TypeError(f'Filters are not defined for {self.OBJECT_TYPE_STR!r} properties')
        return self.FILTER_FACT_CLS(
            property_name=self._property_name,
            property_type_name=self.OBJECT_TYPE_STR,
        )

    @property
    def sort(self) -> SortFactory:
        """Create a ``SortFactory`` tailored for this property"""
        return SortFactory(property_name=self._property_name)

    @classmethod
    def make_data(cls) -> dict:
        return {cls.OBJECT_TYPE_STR: cls.make_internal_data()}

    @classmethod
    def make(cls, **kwargs: Any):
        return cls(
            property_name=kwargs['property_name'],
            data=cls.make_data(),
        )

    @classmethod
    def make_internal_data(cls) -> dict[str, Any]:
        return {}

    def make_prop_from_value(self, value: Any) -> _PROP_TV:
        if self.IS_LIST:
            return PropertyList.make_from_value(  # type: ignore
                item_cls=self.PROP_CLS,
                property_name=self._property_name, value=value,
            )
        return self.PROP_CLS.make_from_value(  # type: ignore
            property_name=self._property_name, value=value,
        )

    def __call__(self, *args: Any, **kwargs: Any) -> _PROP_TV:
        if len(args) == 1 and not kwargs:
            return self.make_prop_from_value(args[0])
        elif not args:
            return self.make_prop_from_value(kwargs)
        else:
            raise TypeError(
                f'Invalid arguments for {type(self).__call__}: '
                'expected either one positional argument or any '
                'number of keyword arguments'
            )


@attr.s(slots=True)
class TextListSchema(PropertySchema[PropertyList[TextProperty], TextFilterFactory]):
    """Paginated text schema"""

    OBJECT_TYPE_STR = 'text'
    PROP_CLS = TextProperty
    FILTER_FACT_CLS = TextFilterFactory
    IS_LIST = True


@attr.s(slots=True)
class NumberPropertySchema(PropertySchema[NumberProperty, NumberFilterFactory]):
    """Schema of ``'number'`` property"""

    OBJECT_TYPE_STR = 'number'
    PROP_CLS = NumberProperty
    FILTER_FACT_CLS = NumberFilterFactory


@attr.s(slots=True)
class CheckboxPropertySchema(PropertySchema[CheckboxProperty, CheckboxFilterFactory]):
    """Schema of ``'checkbox'`` property"""

    OBJECT_TYPE_STR = 'checkbox'
    PROP_CLS = CheckboxProperty
    FILTER_FACT_CLS = CheckboxFilterFactory


@attr.s(slots=True)
class SelectPropertySchema(PropertySchema[SelectProperty, SelectFilterFactory]):
    """Schema of ``'select'`` property"""

    OBJECT_TYPE_STR = 'select'
    PROP_CLS = SelectProperty
    FILTER_FACT_CLS = SelectFilterFactory


@attr.s(slots=True)
class MultiSelectPropertySchema(PropertySchema[MultiSelectProperty, MultiSelectFilterFactory]):
    """Schema of ``'multi_select'`` property"""

    OBJECT_TYPE_STR = 'multi_select'
    PROP_CLS = MultiSelectProperty
    FILTER_FACT_CLS = MultiSelectFilterFactory


@attr.s(slots=True)
class TitlePropertySchema(PropertySchema[TitleProperty, TextFilterFactory]):
    """Schema of ``'title'`` property"""

    OBJECT_TYPE_STR = 'title'
    PROP_CLS = TitleProperty
    FILTER_FACT_CLS = TextFilterFactory


@attr.s(slots=True)
class RichTextPropertySchema(PropertySchema[RichTextProperty, TextFilterFactory]):
    """Schema of ``'rich_text'`` property"""

    OBJECT_TYPE_STR = 'rich_text'
    PROP_CLS = RichTextProperty
    FILTER_FACT_CLS = TextFilterFactory


@attr.s(slots=True)
class UrlPropertySchema(PropertySchema[UrlProperty, TextFilterFactory]):
    """Schema of ``'url'`` property"""

    OBJECT_TYPE_STR = 'url'
    PROP_CLS = UrlProperty
    FILTER_FACT_CLS = TextFilterFactory


@attr.s(slots=True)
class EmailPropertySchema(PropertySchema[EmailProperty, TextFilterFactory]):
    """Schema of ``'email'`` property"""

    OBJECT_TYPE_STR = 'email'
    PROP_CLS = EmailProperty
    FILTER_FACT_CLS = TextFilterFactory


@attr.s(slots=True)
class PhoneNumberPropertySchema(PropertySchema[PhoneNumberProperty, TextFilterFactory]):
    """Schema of ``'phone_number'`` property"""

    OBJECT_TYPE_STR = 'phone_number'
    PROP_CLS = PhoneNumberProperty
    FILTER_FACT_CLS = TextFilterFactory


@attr.s(slots=True)
class DatePropertySchema(PropertySchema[DateProperty, DateFilterFactory]):
    """Schema of ``'date'`` property"""

    OBJECT_TYPE_STR = 'date'
    PROP_CLS = DateProperty
    FILTER_FACT_CLS = DateFilterFactory


_PROPERTY_SCHEMA_CLS_REGISTRY: dict[str, Type[PropertySchema]] = {
    cls.OBJECT_TYPE_STR: cls  # type: ignore
    for cls in [
        NumberPropertySchema,
        CheckboxPropertySchema,
        SelectPropertySchema,
        MultiSelectPropertySchema,
        TitlePropertySchema,
        RichTextPropertySchema,
        EmailPropertySchema,
        PhoneNumberPropertySchema,
        UrlPropertySchema,
        DatePropertySchema,
    ]
}


def get_property_schema_cls(property_type_name: str) -> Type[PropertySchema]:
    return _PROPERTY_SCHEMA_CLS_REGISTRY[property_type_name]
