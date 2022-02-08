from __future__ import annotations

import datetime
from typing import Any, ClassVar, Generic, Iterator, Optional, Type, TypeVar, Union

import attr

from basic_notion.base import NotionItemBase
from basic_notion.attr import ItemAttrDescriptor
from basic_notion.utils import set_to_dict, serialize_date, deserialize_date


_CONTENT_TV = TypeVar('_CONTENT_TV')
_PROP_TV = TypeVar('_PROP_TV', bound='PagePropertyBase')


@attr.s(slots=True)
class PagePropertyBase(NotionItemBase):
    """
    Base class for properties of Notion objects.
    """

    OBJECT_TYPE_KEY_STR = 'type'
    MAKE_FROM_SINGLE_ATTR: ClassVar[Optional[str]] = None

    _property_name: str = attr.ib(kw_only=True, default='')

    @property
    def _content_data(self) -> Any:
        return self.data[self.OBJECT_TYPE_STR]

    @property
    def property_name(self) -> str:
        """Name of the property within the Notion Page object"""
        return self._property_name

    def get_text(self) -> str:
        """Return a text representation of the property's content"""
        return ''

    @classmethod
    def make_from_value(cls: Type[_PROP_TV], property_name: str, value: Any) -> _PROP_TV:
        """Build full instance data from its simplified form"""

        if isinstance(value, cls):
            return cls(property_name=property_name, data=value.data)

        if isinstance(value, dict):
            return cls.make(property_name=property_name, **value)

        assert cls.MAKE_FROM_SINGLE_ATTR is not None
        key = cls.attr_keys[cls.MAKE_FROM_SINGLE_ATTR]  # type: ignore
        data: dict[str, Any] = {}
        if cls.OBJECT_TYPE_STR and cls.OBJECT_TYPE_KEY_STR:
            data[cls.OBJECT_TYPE_KEY_STR] = cls.OBJECT_TYPE_STR

        # Get attr descriptor and its `set_converter` callable
        # (if it exists) to convert the value into its serializable form
        prop = getattr(cls, cls.MAKE_FROM_SINGLE_ATTR)
        set_converter = prop.set_converter
        if set_converter is not None:
            value = set_converter(value)

        set_to_dict(data, key, value)
        return cls(property_name=property_name, data=data)

    @classmethod
    def make(cls: Type[_PROP_TV], **kwargs: Any) -> _PROP_TV:
        """Make property instance from keyword arguments"""

        data = cls._make_inst_dict(kwargs)
        return cls(data=data, property_name=kwargs['property_name'])


@attr.s(slots=True)
class PageProperty(PagePropertyBase):
    id: ItemAttrDescriptor[str] = ItemAttrDescriptor()
    type: ItemAttrDescriptor[str] = ItemAttrDescriptor()


DEFAULT_TEXT_SEP = ''
DEFAULT_LIST_TEXT_SEP = ', '

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


_PAG_PROP_TV = TypeVar('_PAG_PROP_TV', bound='PaginatedProperty')


@attr.s(slots=True)
class PaginatedProperty(PageProperty, Generic[_PAG_PROP_ITEM_TV]):
    """Paginated property base class"""

    ITEM_CLS: ClassVar[Type[_PAG_PROP_ITEM_TV]]

    _text_sep: str = attr.ib(kw_only=True, default=DEFAULT_TEXT_SEP)

    @property
    def text_sep(self) -> str:
        return self._text_sep

    @property
    def _content_data_list(self) -> list[dict]:
        data = self._content_data
        assert isinstance(data, list)
        return data

    @property
    def items(self) -> PropertyList[_PAG_PROP_ITEM_TV]:
        return PropertyList(data=self._content_data_list, item_cls=self.ITEM_CLS, text_sep=self._text_sep)

    @items.setter
    def items(self, value: PropertyList) -> None:
        self.data[self.OBJECT_TYPE_STR] = value.data

    @property
    def one_item(self) -> _PAG_PROP_ITEM_TV:
        items = self.items
        assert len(items) == 1
        return items[0]

    def get_text(self) -> str:
        return self.items.get_text()

    @classmethod
    def make_from_value(cls: Type[_PAG_PROP_TV], property_name: str, value: Any) -> _PAG_PROP_TV:
        if isinstance(value, cls):
            return cls(property_name=property_name, data=value.data, text_sep=value.text_sep)

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
    MAKE_FROM_SINGLE_ATTR = 'content'

    content: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=(OBJECT_TYPE_STR, 'content'), editable=True)
    annotations: ItemAttrDescriptor[dict] = ItemAttrDescriptor()
    href: ItemAttrDescriptor[Optional[str]] = ItemAttrDescriptor(editable=True)
    plain_text: ItemAttrDescriptor[str] = ItemAttrDescriptor(derived=True)

    # The insides of `annotations`:
    _anno = 'annotations'
    bold: ItemAttrDescriptor[dict] = ItemAttrDescriptor(key=(_anno, 'bold'), editable=True)
    italic: ItemAttrDescriptor[dict] = ItemAttrDescriptor(key=(_anno, 'italic'), editable=True)
    strikethrough: ItemAttrDescriptor[dict] = ItemAttrDescriptor(key=(_anno, 'strikethrough'), editable=True)
    underline: ItemAttrDescriptor[dict] = ItemAttrDescriptor(key=(_anno, 'underline'), editable=True)
    code: ItemAttrDescriptor[dict] = ItemAttrDescriptor(key=(_anno, 'code'), editable=True)
    color: ItemAttrDescriptor[dict] = ItemAttrDescriptor(key=(_anno, 'color'), editable=True)

    def get_text(self) -> str:
        return self.content


@attr.s(slots=True)
class NumberProperty(PageProperty):
    """Property of type ``'number'``"""

    OBJECT_TYPE_STR = 'number'
    MAKE_FROM_SINGLE_ATTR = 'number'

    number: ItemAttrDescriptor[Union[int, float]] = ItemAttrDescriptor(editable=True)

    def get_text(self) -> str:
        return str(self.number)


@attr.s(slots=True)
class CheckboxProperty(PageProperty):
    """Property of type ``'checkbox'``"""

    OBJECT_TYPE_STR = 'checkbox'
    MAKE_FROM_SINGLE_ATTR = 'checkbox'

    checkbox: ItemAttrDescriptor[bool] = ItemAttrDescriptor(editable=True)


@attr.s(slots=True)
class SelectProperty(PageProperty):
    """Property of type ``'select'``"""

    OBJECT_TYPE_STR = 'select'
    MAKE_FROM_SINGLE_ATTR = 'name'

    option_id: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=(OBJECT_TYPE_STR, 'id'), derived=True)
    name: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=(OBJECT_TYPE_STR, 'name'), editable=True)
    color: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=(OBJECT_TYPE_STR, 'color'), derived=True)

    def get_text(self) -> str:
        return self.name


@attr.s(slots=True)
class MultiSelectPropertyItem(PageProperty):
    """Item of a multi-select list property"""

    OBJECT_TYPE_KEY_STR = ''  # no attribute containing the object type
    OBJECT_TYPE_STR = ''
    MAKE_FROM_SINGLE_ATTR = 'name'

    option_id: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=('id',), derived=True)
    name: ItemAttrDescriptor[str] = ItemAttrDescriptor(editable=True)
    color: ItemAttrDescriptor[str] = ItemAttrDescriptor(derived=True)

    def get_text(self) -> str:
        return self.name


@attr.s(slots=True)
class MultiSelectProperty(PaginatedProperty[MultiSelectPropertyItem]):
    """Property of type ``'multi_select'``"""

    OBJECT_TYPE_STR = 'multi_select'
    ITEM_CLS = MultiSelectPropertyItem

    _text_sep: str = attr.ib(kw_only=True, default=DEFAULT_LIST_TEXT_SEP)

    def set_names(self, value: list[str]) -> None:
        self.items = PropertyList.make_from_value(
            item_cls=self.ITEM_CLS,
            value=value,
            property_name=self.property_name,
        )


@attr.s(slots=True)
class TitleProperty(PaginatedProperty[TextProperty]):
    """Property of type ``'title'``"""

    OBJECT_TYPE_STR = 'title'
    ITEM_CLS = TextProperty


@attr.s(slots=True)
class RichTextProperty(PaginatedProperty[TextProperty]):
    """Property of type ``'rich_text'``"""

    OBJECT_TYPE_STR = 'rich_text'
    ITEM_CLS = TextProperty


@attr.s(slots=True)
class UrlProperty(PageProperty):
    """Property of type ``'checkbox'``"""

    OBJECT_TYPE_STR = 'url'
    MAKE_FROM_SINGLE_ATTR = 'url'

    url: ItemAttrDescriptor[Union[int, float]] = ItemAttrDescriptor(editable=True)

    def get_text(self) -> str:
        return str(self.url)


@attr.s(slots=True)
class EmailProperty(PageProperty):
    """Property of type ``'checkbox'``"""

    OBJECT_TYPE_STR = 'email'
    MAKE_FROM_SINGLE_ATTR = 'email'

    email: ItemAttrDescriptor[Union[int, float]] = ItemAttrDescriptor(editable=True)

    def get_text(self) -> str:
        return str(self.email)


@attr.s(slots=True)
class PhoneNumberProperty(PageProperty):
    """Property of type ``'phone_number'``"""

    OBJECT_TYPE_STR = 'phone_number'
    MAKE_FROM_SINGLE_ATTR = 'phone_number'

    phone_number: ItemAttrDescriptor[Union[int, float]] = ItemAttrDescriptor(editable=True)

    def get_text(self) -> str:
        return str(self.phone_number)


@attr.s(slots=True)
class DateProperty(PageProperty):
    """Property of type ``'date'``"""

    OBJECT_TYPE_STR = 'date'
    MAKE_FROM_SINGLE_ATTR = 'start'

    start: ItemAttrDescriptor[Optional[datetime.datetime]] = ItemAttrDescriptor(
        key=(OBJECT_TYPE_STR, 'start'), editable=True,
        get_converter=deserialize_date, set_converter=serialize_date)
    start_str: ItemAttrDescriptor[Optional[str]] = ItemAttrDescriptor(
        key=(OBJECT_TYPE_STR, 'start'), editable=True)
    end: ItemAttrDescriptor[Optional[datetime.datetime]] = ItemAttrDescriptor(
        key=(OBJECT_TYPE_STR, 'end'), editable=True,
        get_converter=deserialize_date, set_converter=serialize_date)
    end_str: ItemAttrDescriptor[Optional[str]] = ItemAttrDescriptor(
        key=(OBJECT_TYPE_STR, 'end'), editable=True)

    def get_text(self) -> str:
        return f'{self.start_str} - {self.end_str}'.replace('None', '...')
