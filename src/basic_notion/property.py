from typing import Any, ClassVar, Generic, Optional, Type, TypeVar, Union

import attr

from basic_notion.base import NotionItemBase
from basic_notion.filter import (
    FilterFactory, TextFilterFactory, NumberFilterFactory, CheckboxFilterFactory,
    SelectFilterFactory, MultiSelectFilterFactory,
)


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


@attr.s(frozen=True)
class PageProperty(PagePropertyBase):
    @property
    def id(self) -> str:
        return self.data['id']

    @property
    def type(self) -> str:
        return self.data['type']


@attr.s(frozen=True)
class ComplexPageProperty(PageProperty):
    @property
    def _content_data_dict(self) -> dict:
        data = self._content_data
        assert isinstance(data, dict)
        return data


@attr.s(frozen=True)
class SimpleStringPageProperty(PageProperty):
    @property
    def _content_data_str(self) -> str:
        data = self._content_data
        assert isinstance(data, str)
        return data


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
class TextProperty(ComplexPageProperty):
    """Property of type ``'text'``"""

    _OBJECT_TYPE_STR = 'text'
    _FILTER_FACT_CLS = TextFilterFactory

    @property
    def content(self) -> str:
        return self._content_data_dict['content']


@attr.s(frozen=True)
class NumberProperty(PageProperty):
    """Property of type ``'number'``"""

    _OBJECT_TYPE_STR = 'number'
    _FILTER_FACT_CLS = NumberFilterFactory

    @property
    def value(self) -> Union[int, float]:
        value = self._content_data
        assert isinstance(value, (int, float))
        return value


@attr.s(frozen=True)
class CheckboxProperty(PageProperty):
    """Property of type ``'checkbox'``"""

    _OBJECT_TYPE_STR = 'checkbox'
    _FILTER_FACT_CLS = CheckboxFilterFactory

    @property
    def value(self) -> bool:
        value = self._content_data
        assert isinstance(value, bool)
        return value


@attr.s(frozen=True)
class SelectProperty(ComplexPageProperty):
    """Property of type ``'select'``"""

    _OBJECT_TYPE_STR = 'select'
    _FILTER_FACT_CLS = SelectFilterFactory

    @property
    def option_id(self) -> str:
        return self._content_data_dict['id']

    @property
    def name(self) -> str:
        return self._content_data_dict['name']

    @property
    def color(self) -> str:
        return self._content_data_dict['color']


@attr.s(frozen=True)
class MultiSelectProperty(ComplexPageProperty):
    """Property of type ``'select'``"""

    _OBJECT_TYPE_STR = 'multi_select'
    _FILTER_FACT_CLS = MultiSelectFilterFactory

    @property
    def option_id(self) -> str:
        return self._content_data_dict['id']

    @property
    def name(self) -> str:
        return self._content_data_dict['name']

    @property
    def color(self) -> str:
        return self._content_data_dict['color']


@attr.s(frozen=True)
class TitleProperty(PaginatedProperty[TextProperty]):
    """Property of type ``'title'``"""

    _OBJECT_TYPE_STR = 'title'
    _ITEM_CLS = TextProperty
    _FILTER_FACT_CLS = TextFilterFactory
