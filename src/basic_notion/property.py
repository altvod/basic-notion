from __future__ import annotations

from typing import Any, ClassVar, Generic, Iterator, Optional, Type, TypeVar, Union

import attr

from basic_notion.base import NotionItemBase
from basic_notion.filter import (
    FilterFactory, TextFilterFactory, NumberFilterFactory, CheckboxFilterFactory,
    SelectFilterFactory, MultiSelectFilterFactory,
)
from basic_notion.sort import SortFactory
from basic_notion.attr import ItemAttrDescriptor
from basic_notion.utils import get_from_dict, set_to_dict


_FILTER_FACT_TV = TypeVar('_FILTER_FACT_TV', bound=FilterFactory)
_CONTENT_TV = TypeVar('_CONTENT_TV')
_PROP_TV = TypeVar('_PROP_TV', bound='PagePropertyBase')


@attr.s(slots=True)
class PagePropertyBase(NotionItemBase, Generic[_FILTER_FACT_TV]):
    """
    Base class for properties of Notion objects.
    """

    OBJECT_TYPE_KEY_STR = 'type'
    FILTER_FACT_CLS: ClassVar[Optional[Type[_FILTER_FACT_TV]]] = None

    _property_name: str = attr.ib(kw_only=True, default='')

    @property
    def _content_data(self) -> Any:
        return self.data[self.OBJECT_TYPE_STR]

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

    def get_text(self) -> str:
        """Return a text representation of the property's content"""
        return ''

    @classmethod
    def make_from_value(cls: Type[_PROP_TV], property_name: str, value: Any) -> _PROP_TV:
        if isinstance(value, dict):
            return cls.make(property_name=property_name, **value)
        editable_keys: dict[str, tuple[str, ...]] = cls.editable_keys  # type: ignore
        assert len(editable_keys) == 1
        key = next(iter(editable_keys.values()))
        data: dict[str, Any] = {}
        if cls.OBJECT_TYPE_STR and cls.OBJECT_TYPE_KEY_STR:
            data[cls.OBJECT_TYPE_KEY_STR] = cls.OBJECT_TYPE_STR

        set_to_dict(data, key, value)
        return cls(property_name=property_name, data=data)

    @classmethod
    def make(cls: Type[_PROP_TV], **kwargs: Any) -> _PROP_TV:
        data = cls._make_inst_dict(kwargs)
        return cls(data=data, property_name=kwargs['property_name'])

    def make_spec(self) -> dict[str, dict]:
        return {self.OBJECT_TYPE_STR: self.make_internal_spec()}

    def make_internal_spec(self) -> dict[str, Any]:
        return {}


@attr.s(slots=True)
class PageProperty(PagePropertyBase):
    id: ItemAttrDescriptor[str] = ItemAttrDescriptor()
    type: ItemAttrDescriptor[str] = ItemAttrDescriptor()


DEFAULT_TEXT_SEP = ','

_PAG_PROP_ITEM_TV = TypeVar('_PAG_PROP_ITEM_TV', bound=PageProperty)


@attr.s
class PropertyList(Generic[_PAG_PROP_ITEM_TV]):
    _data: list[dict] = attr.ib(kw_only=True)
    _item_cls: Type[_PAG_PROP_ITEM_TV] = attr.ib(kw_only=True)
    _text_sep: str = attr.ib(kw_only=True, default=DEFAULT_TEXT_SEP)

    @property
    def data(self) -> list[dict]:
        return self._data

    def __iter__(self) -> Iterator[_PAG_PROP_ITEM_TV]:
        return iter(self._item_cls(data=item) for item in self._data)

    def __getitem__(self, item: Union[int]) -> _PAG_PROP_ITEM_TV:
        if not isinstance(item, int):
            raise TypeError(f'{type(self).__name__} can only be indexed by int')
        return self._item_cls(data=self._data[item])

    def __len__(self) -> int:
        return len(self._data)

    def get_text(self) -> str:
        return self._text_sep.join([item.get_text() for item in self])

    @classmethod
    def make_from_value(
            cls, item_cls: Type[_PAG_PROP_ITEM_TV],
            property_name: str, value: Any,
            text_sep: str = DEFAULT_TEXT_SEP,
    ) -> PropertyList[_PAG_PROP_ITEM_TV]:
        assert isinstance(value, list)
        data = [
            item_cls.make_from_value(
                property_name=property_name, value=item,
            ).data  # type: ignore
            for item in value
        ]
        return cls(item_cls=item_cls, text_sep=text_sep, data=data)


@attr.s(slots=True)
class PaginatedProperty(PageProperty, Generic[_PAG_PROP_ITEM_TV]):
    """Paginated property base class"""

    ITEM_CLS: ClassVar[Type[_PAG_PROP_ITEM_TV]]

    _text_sep: str = attr.ib(kw_only=True, default=DEFAULT_TEXT_SEP)

    @property
    def _content_data_list(self) -> list[dict]:
        data = self._content_data
        assert isinstance(data, list)
        return data

    @property
    def items(self) -> PropertyList[_PAG_PROP_ITEM_TV]:
        return PropertyList(data=self._content_data_list, item_cls=self.ITEM_CLS, text_sep=self._text_sep)

    @property
    def one_item(self) -> _PAG_PROP_ITEM_TV:
        items = self.items
        assert len(items) == 1
        return items[0]

    def get_text(self) -> str:
        return self.items.get_text()

    @classmethod
    def make_from_value(cls: Type[_PROP_TV], property_name: str, value: Any) -> _PROP_TV:
        assert isinstance(value, list)
        data = {
            cls.OBJECT_TYPE_KEY_STR: cls.OBJECT_TYPE_STR,
            cls.OBJECT_TYPE_STR: PropertyList.make_from_value(
                item_cls=cls.ITEM_CLS,  # type: ignore
                value=value,
                property_name=property_name,
            ).data
        }
        return cls(property_name=property_name, data=data)


@attr.s(slots=True)
class TextProperty(PageProperty):
    """Property of type ``'text'``"""

    OBJECT_TYPE_STR = 'text'
    FILTER_FACT_CLS = TextFilterFactory

    content: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=(OBJECT_TYPE_STR, 'content'), editable=True)

    def get_text(self) -> str:
        return self.content


@attr.s(slots=True)
class NumberProperty(PageProperty):
    """Property of type ``'number'``"""

    OBJECT_TYPE_STR = 'number'
    FILTER_FACT_CLS = NumberFilterFactory

    number: ItemAttrDescriptor[Union[int, float]] = ItemAttrDescriptor(editable=True)

    def get_text(self) -> str:
        return str(self.number)


@attr.s(slots=True)
class CheckboxProperty(PageProperty):
    """Property of type ``'checkbox'``"""

    OBJECT_TYPE_STR = 'checkbox'
    FILTER_FACT_CLS = CheckboxFilterFactory

    checkbox: ItemAttrDescriptor[bool] = ItemAttrDescriptor(editable=True)


@attr.s(slots=True)
class SelectProperty(PageProperty):
    """Property of type ``'select'``"""

    OBJECT_TYPE_STR = 'select'
    FILTER_FACT_CLS = SelectFilterFactory

    option_id: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=(OBJECT_TYPE_STR, 'id'))
    name: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=(OBJECT_TYPE_STR, 'name'), editable=True)
    color: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=(OBJECT_TYPE_STR, 'color'))

    def get_text(self) -> str:
        return self.name


@attr.s(slots=True)
class MultiSelectPropertyItem(PageProperty):
    """Item of a multi-select list property"""

    OBJECT_TYPE_KEY_STR = ''  # no attribute containing the object type
    OBJECT_TYPE_STR = ''

    option_id: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=('id',))
    name: ItemAttrDescriptor[str] = ItemAttrDescriptor(editable=True)
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

    url: ItemAttrDescriptor[Union[int, float]] = ItemAttrDescriptor(editable=True)

    def get_text(self) -> str:
        return str(self.url)


@attr.s(slots=True)
class EmailProperty(PageProperty):
    """Property of type ``'checkbox'``"""

    OBJECT_TYPE_STR = 'email'
    FILTER_FACT_CLS = TextFilterFactory

    email: ItemAttrDescriptor[Union[int, float]] = ItemAttrDescriptor(editable=True)

    def get_text(self) -> str:
        return str(self.email)


@attr.s(slots=True)
class PhoneNumberProperty(PageProperty):
    """Property of type ``'phone_number'``"""

    OBJECT_TYPE_STR = 'phone_number'
    FILTER_FACT_CLS = TextFilterFactory

    phone_number: ItemAttrDescriptor[Union[int, float]] = ItemAttrDescriptor(editable=True)

    def get_text(self) -> str:
        return str(self.phone_number)
