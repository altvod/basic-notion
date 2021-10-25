from typing import Any, ClassVar, Generic, Optional, Type, TypeVar, Union

import attr

from basic_notion.base import NotionItemBase
from basic_notion.filter import (
    FilterFactory, TextFilterFactory, NumberFilterFactory, CheckboxFilterFactory,
    SelectFilterFactory, MultiSelectFilterFactory,
)
from basic_notion.sort import SortFactory


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


_PROP_ATTR_TV = TypeVar('_PROP_ATTR_TV')


class PropertyAttrDescr(Generic[_PROP_ATTR_TV]):
    __slots__ = ('__key',)

    def __init__(self, key: Optional[tuple[str, ...]] = None):
        self.__key = key

    def __set_name__(self, owner: PagePropertyBase, name: str) -> None:
        if self.__key is None:
            self.__key = (name,)

    @property
    def _key(self) -> tuple[str, ...]:
        assert self.__key is not None
        return self.__key

    def __get__(self, instance: PagePropertyBase, owner: Type[PagePropertyBase]) -> _PROP_ATTR_TV:
        data: Any = instance.data
        for part in self._key:
            assert isinstance(data, dict)
            data = data[part]
        return data


@attr.s(frozen=True)
class PageProperty(PagePropertyBase):
    id: PropertyAttrDescr[str] = PropertyAttrDescr()
    type: PropertyAttrDescr[str] = PropertyAttrDescr()


_PAG_PROP_ITEM_TV = TypeVar('_PAG_PROP_ITEM_TV', bound=PageProperty)


@attr.s(frozen=True)
class PaginatedProperty(PageProperty, Generic[_PAG_PROP_ITEM_TV]):
    """Paginated property base class"""

    _ITEM_CLS: ClassVar[Type[_PAG_PROP_ITEM_TV]]

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


@attr.s(frozen=True)
class TextProperty(PageProperty):
    """Property of type ``'text'``"""

    _OBJECT_TYPE_STR = 'text'
    _FILTER_FACT_CLS = TextFilterFactory

    content: PropertyAttrDescr[str] = PropertyAttrDescr(key=(_OBJECT_TYPE_STR, 'content'))


@attr.s(frozen=True)
class NumberProperty(PageProperty):
    """Property of type ``'number'``"""

    _OBJECT_TYPE_STR = 'number'
    _FILTER_FACT_CLS = NumberFilterFactory

    number: PropertyAttrDescr[Union[int, float]] = PropertyAttrDescr()


@attr.s(frozen=True)
class CheckboxProperty(PageProperty):
    """Property of type ``'checkbox'``"""

    _OBJECT_TYPE_STR = 'checkbox'
    _FILTER_FACT_CLS = CheckboxFilterFactory

    checkbox: PropertyAttrDescr[Union[int, float]] = PropertyAttrDescr()


@attr.s(frozen=True)
class SelectProperty(PageProperty):
    """Property of type ``'select'``"""

    _OBJECT_TYPE_STR = 'select'
    _FILTER_FACT_CLS = SelectFilterFactory

    option_id: PropertyAttrDescr[str] = PropertyAttrDescr(key=(_OBJECT_TYPE_STR, 'id'))
    name: PropertyAttrDescr[str] = PropertyAttrDescr(key=(_OBJECT_TYPE_STR, 'name'))
    color: PropertyAttrDescr[str] = PropertyAttrDescr(key=(_OBJECT_TYPE_STR, 'color'))


@attr.s(frozen=True)
class MultiSelectProperty(PageProperty):
    """Property of type ``'select'``"""

    _OBJECT_TYPE_STR = 'multi_select'
    _FILTER_FACT_CLS = MultiSelectFilterFactory

    option_id: PropertyAttrDescr[str] = PropertyAttrDescr(key=(_OBJECT_TYPE_STR, 'id'))
    name: PropertyAttrDescr[str] = PropertyAttrDescr(key=(_OBJECT_TYPE_STR, 'name'))
    color: PropertyAttrDescr[str] = PropertyAttrDescr(key=(_OBJECT_TYPE_STR, 'color'))


@attr.s(frozen=True)
class TitleProperty(PaginatedProperty[TextProperty]):
    """Property of type ``'title'``"""

    _OBJECT_TYPE_STR = 'title'
    _ITEM_CLS = TextProperty
    _FILTER_FACT_CLS = TextFilterFactory
