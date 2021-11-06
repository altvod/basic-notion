from typing import Any, ClassVar, Generic, Optional, Type, TypeVar, Union

import attr

from basic_notion.base import NotionItemBase
from basic_notion.filter import (
    FilterFactory, TextFilterFactory, NumberFilterFactory, CheckboxFilterFactory,
    SelectFilterFactory, MultiSelectFilterFactory,
)
from basic_notion.sort import SortFactory
from basic_notion.attr import ItemAttrDescriptor


_FILTER_FACT_TV = TypeVar('_FILTER_FACT_TV', bound=FilterFactory)
_CONTENT_TV = TypeVar('_CONTENT_TV')


@attr.s(frozen=True)
class PagePropertyBase(NotionItemBase, Generic[_FILTER_FACT_TV]):
    """
    Base class for properties of Notion objects.
    """

    _OBJECT_TYPE_KEY_STR = 'type'
    _FILTER_FACT_CLS: ClassVar[Optional[Type[_FILTER_FACT_TV]]] = None

    _property_name: str = attr.ib(kw_only=True, default=None)

    @property
    def _content_data(self) -> Any:
        return self.data[self._OBJECT_TYPE_STR]

    @property
    def property_name(self) -> str:
        return self._property_name

    @property
    def filter(self) -> _FILTER_FACT_TV:
        if self._FILTER_FACT_CLS is None:
            raise TypeError(f'Filters are not defined for {self._OBJECT_TYPE_STR!r} properties')
        return self._FILTER_FACT_CLS(
            property_name=self._property_name,
            property_type_name=self._OBJECT_TYPE_STR,
        )

    @property
    def sort(self) -> SortFactory:
        return SortFactory(property_name=self._property_name)

    def get_text(self) -> str:
        return ''


@attr.s(frozen=True)
class PageProperty(PagePropertyBase):
    id: ItemAttrDescriptor[str] = ItemAttrDescriptor()
    type: ItemAttrDescriptor[str] = ItemAttrDescriptor()


_PAG_PROP_ITEM_TV = TypeVar('_PAG_PROP_ITEM_TV', bound=PageProperty)


@attr.s(frozen=True)
class PaginatedProperty(PageProperty, Generic[_PAG_PROP_ITEM_TV]):
    """Paginated property base class"""

    _ITEM_CLS: ClassVar[Type[_PAG_PROP_ITEM_TV]]

    _text_sep: str = attr.ib(kw_only=True, default=',')

    @property
    def _content_data_list(self) -> list[dict]:
        data = self._content_data
        assert isinstance(data, list)
        return data

    @property
    def items(self) -> list[_PAG_PROP_ITEM_TV]:
        return [
            self._ITEM_CLS(data=item_data, property_name=self._property_name)
            for item_data in self._content_data_list
        ]

    @property
    def one_item(self) -> _PAG_PROP_ITEM_TV:
        items = self.items
        assert len(items) == 1
        return items[0]

    def get_text(self) -> str:
        return self._text_sep.join([item.get_text() for item in self.items])


@attr.s(frozen=True)
class TextProperty(PageProperty):
    """Property of type ``'text'``"""

    _OBJECT_TYPE_STR = 'text'
    _FILTER_FACT_CLS = TextFilterFactory

    content: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=(_OBJECT_TYPE_STR, 'content'))

    def get_text(self) -> str:
        return self.content


@attr.s(frozen=True)
class NumberProperty(PageProperty):
    """Property of type ``'number'``"""

    _OBJECT_TYPE_STR = 'number'
    _FILTER_FACT_CLS = NumberFilterFactory

    number: ItemAttrDescriptor[Union[int, float]] = ItemAttrDescriptor()

    def get_text(self) -> str:
        return str(self.number)


@attr.s(frozen=True)
class CheckboxProperty(PageProperty):
    """Property of type ``'checkbox'``"""

    _OBJECT_TYPE_STR = 'checkbox'
    _FILTER_FACT_CLS = CheckboxFilterFactory

    checkbox: ItemAttrDescriptor[Union[int, float]] = ItemAttrDescriptor()


@attr.s(frozen=True)
class SelectProperty(PageProperty):
    """Property of type ``'select'``"""

    _OBJECT_TYPE_STR = 'select'
    _FILTER_FACT_CLS = SelectFilterFactory

    option_id: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=(_OBJECT_TYPE_STR, 'id'))
    name: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=(_OBJECT_TYPE_STR, 'name'))
    color: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=(_OBJECT_TYPE_STR, 'color'))

    def get_text(self) -> str:
        return self.name


@attr.s(frozen=True)
class MultiSelectPropertyItem(PageProperty):
    """Item of a multi-select list property"""

    _OBJECT_TYPE_KEY_STR = ''  # no attribute containing the object type
    _OBJECT_TYPE_STR = ''

    option_id: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=('id',))
    name: ItemAttrDescriptor[str] = ItemAttrDescriptor()
    color: ItemAttrDescriptor[str] = ItemAttrDescriptor()

    def get_text(self) -> str:
        return self.name


@attr.s(frozen=True)
class MultiSelectProperty(PaginatedProperty[MultiSelectPropertyItem]):
    """Property of type ``'multi_select'``"""

    _OBJECT_TYPE_STR = 'multi_select'
    _ITEM_CLS = MultiSelectPropertyItem
    _FILTER_FACT_CLS = MultiSelectFilterFactory


@attr.s(frozen=True)
class TitleProperty(PaginatedProperty[TextProperty]):
    """Property of type ``'title'``"""

    _OBJECT_TYPE_STR = 'title'
    _ITEM_CLS = TextProperty
    _FILTER_FACT_CLS = TextFilterFactory
