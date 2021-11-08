from typing import Any, ClassVar, Generic, Optional, Type, TypeVar, Union

import attr

from basic_notion.base import NotionItemBase
from basic_notion.filter import (
    FilterFactory, TextFilterFactory, NumberFilterFactory, CheckboxFilterFactory,
    SelectFilterFactory, MultiSelectFilterFactory,
)
from basic_notion.sort import SortFactory
from basic_notion.attr import ItemAttrDescriptor
from basic_notion.data_gen import (
    PaginatedPropertyDataGen, TextPropertyDataGen,
    CheckboxPropertyDataGen, NumberPropertyDataGen,
    SelectPropertyDataGen, UrlPropertyDataGen,
    EmailPropertyDataGen, PhoneNumberPropertyDataGen,
)


_FILTER_FACT_TV = TypeVar('_FILTER_FACT_TV', bound=FilterFactory)
_CONTENT_TV = TypeVar('_CONTENT_TV')


@attr.s(slots=True)
class PagePropertyBase(NotionItemBase, Generic[_FILTER_FACT_TV]):
    """
    Base class for properties of Notion objects.
    """

    OBJECT_TYPE_KEY_STR = 'type'
    FILTER_FACT_CLS: ClassVar[Optional[Type[_FILTER_FACT_TV]]] = None

    _property_name: str = attr.ib(kw_only=True, default=None)

    @property
    def _content_data(self) -> Any:
        return self.data[self.OBJECT_TYPE_STR]

    @property
    def property_name(self) -> str:
        return self._property_name

    @property
    def filter(self) -> _FILTER_FACT_TV:
        if self.FILTER_FACT_CLS is None:
            raise TypeError(f'Filters are not defined for {self.OBJECT_TYPE_STR!r} properties')
        return self.FILTER_FACT_CLS(
            property_name=self._property_name,
            property_type_name=self.OBJECT_TYPE_STR,
        )

    @property
    def sort(self) -> SortFactory:
        return SortFactory(property_name=self._property_name)

    def get_text(self) -> str:
        return ''


@attr.s(slots=True)
class PageProperty(PagePropertyBase):
    id: ItemAttrDescriptor[str] = ItemAttrDescriptor()
    type: ItemAttrDescriptor[str] = ItemAttrDescriptor()


_PAG_PROP_ITEM_TV = TypeVar('_PAG_PROP_ITEM_TV', bound=PageProperty)


@attr.s(slots=True)
class PaginatedProperty(PageProperty, Generic[_PAG_PROP_ITEM_TV]):
    """Paginated property base class"""

    ITEM_CLS: ClassVar[Type[_PAG_PROP_ITEM_TV]]
    DATA_GEN_CLS = PaginatedPropertyDataGen

    _text_sep: str = attr.ib(kw_only=True, default=',')

    @property
    def _content_data_list(self) -> list[dict]:
        data = self._content_data
        assert isinstance(data, list)
        return data

    @property
    def items(self) -> list[_PAG_PROP_ITEM_TV]:
        return [
            self.ITEM_CLS(data=item_data, property_name=self._property_name)
            for item_data in self._content_data_list
        ]

    @property
    def one_item(self) -> _PAG_PROP_ITEM_TV:
        items = self.items
        assert len(items) == 1
        return items[0]

    def get_text(self) -> str:
        return self._text_sep.join([item.get_text() for item in self.items])


@attr.s(slots=True)
class TextProperty(PageProperty):
    """Property of type ``'text'``"""

    OBJECT_TYPE_STR = 'text'
    FILTER_FACT_CLS = TextFilterFactory
    DATA_GEN_CLS = TextPropertyDataGen

    content: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=(OBJECT_TYPE_STR, 'content'))

    def get_text(self) -> str:
        return self.content


@attr.s(slots=True)
class NumberProperty(PageProperty):
    """Property of type ``'number'``"""

    OBJECT_TYPE_STR = 'number'
    FILTER_FACT_CLS = NumberFilterFactory
    DATA_GEN_CLS = NumberPropertyDataGen

    number: ItemAttrDescriptor[Union[int, float]] = ItemAttrDescriptor()

    def get_text(self) -> str:
        return str(self.number)


@attr.s(slots=True)
class CheckboxProperty(PageProperty):
    """Property of type ``'checkbox'``"""

    OBJECT_TYPE_STR = 'checkbox'
    FILTER_FACT_CLS = CheckboxFilterFactory
    DATA_GEN_CLS = CheckboxPropertyDataGen

    checkbox: ItemAttrDescriptor[Union[int, float]] = ItemAttrDescriptor()


@attr.s(slots=True)
class SelectProperty(PageProperty):
    """Property of type ``'select'``"""

    OBJECT_TYPE_STR = 'select'
    FILTER_FACT_CLS = SelectFilterFactory
    DATA_GEN_CLS = SelectPropertyDataGen

    option_id: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=(OBJECT_TYPE_STR, 'id'))
    name: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=(OBJECT_TYPE_STR, 'name'))
    color: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=(OBJECT_TYPE_STR, 'color'))

    def get_text(self) -> str:
        return self.name


@attr.s(slots=True)
class MultiSelectPropertyItem(PageProperty):
    """Item of a multi-select list property"""

    OBJECT_TYPE_KEY_STR = ''  # no attribute containing the object type
    OBJECT_TYPE_STR = ''
    DATA_GEN_CLS = SelectPropertyDataGen

    option_id: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=('id',))
    name: ItemAttrDescriptor[str] = ItemAttrDescriptor()
    color: ItemAttrDescriptor[str] = ItemAttrDescriptor()

    def get_text(self) -> str:
        return self.name


@attr.s(slots=True)
class MultiSelectProperty(PaginatedProperty[MultiSelectPropertyItem]):
    """Property of type ``'multi_select'``"""

    OBJECT_TYPE_STR = 'multi_select'
    ITEM_CLS = MultiSelectPropertyItem
    FILTER_FACT_CLS = MultiSelectFilterFactory


@attr.s(slots=True)
class TitleProperty(PaginatedProperty[TextProperty]):
    """Property of type ``'title'``"""

    OBJECT_TYPE_STR = 'title'
    ITEM_CLS = TextProperty
    FILTER_FACT_CLS = TextFilterFactory


@attr.s(slots=True)
class UrlProperty(PageProperty):
    """Property of type ``'checkbox'``"""

    OBJECT_TYPE_STR = 'url'
    FILTER_FACT_CLS = TextFilterFactory
    DATA_GEN_CLS = UrlPropertyDataGen

    url: ItemAttrDescriptor[Union[int, float]] = ItemAttrDescriptor()

    def get_text(self) -> str:
        return str(self.url)


@attr.s(slots=True)
class EmailProperty(PageProperty):
    """Property of type ``'checkbox'``"""

    OBJECT_TYPE_STR = 'email'
    FILTER_FACT_CLS = TextFilterFactory
    DATA_GEN_CLS = EmailPropertyDataGen

    email: ItemAttrDescriptor[Union[int, float]] = ItemAttrDescriptor()

    def get_text(self) -> str:
        return str(self.email)


@attr.s(slots=True)
class PhoneNumberProperty(PageProperty):
    """Property of type ``'phone_number'``"""

    OBJECT_TYPE_STR = 'phone_number'
    FILTER_FACT_CLS = TextFilterFactory
    DATA_GEN_CLS = PhoneNumberPropertyDataGen

    phone_number: ItemAttrDescriptor[Union[int, float]] = ItemAttrDescriptor()

    def get_text(self) -> str:
        return str(self.phone_number)
