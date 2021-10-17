import abc
from enum import Enum, unique
from typing import ClassVar, Generic, Optional, Type, TypeVar

import attr

from basic_notion import exc


@unique
class PropertyType(Enum):
    select = 'select'
    text = 'text'


@attr.s(frozen=True)
class NotionItemBase(abc.ABC):
    _OBJECT_TYPE_KEY_STR: ClassVar[str] = 'object'
    _OBJECT_TYPE_STR: ClassVar[str]

    _data: Optional[dict] = attr.ib(kw_only=True, default=None)

    def __attrs_post_init__(self) -> None:
        if self._data is not None:
            assert self._data[self._OBJECT_TYPE_KEY_STR] == self._OBJECT_TYPE_STR

    @property
    def data(self) -> dict:
        if self._data is None:
            raise exc.ItemHasNoData(f'Object {type(self).__name__} has no data')
        return self._data


@attr.s(frozen=True)
class NotionItem(NotionItemBase):
    @property
    def properties_data(self) -> dict:
        return self.data['properties']


@attr.s(frozen=True)
class NotionPage(NotionItem):
    """
    Represents a page object returned by the Notion API
    """

    _OBJECT_TYPE_STR = 'page'


_RESULT_ITEM_TV = TypeVar('_RESULT_ITEM_TV', bound=NotionPage)


@attr.s(frozen=True)
class NotionList(NotionItemBase, Generic[_RESULT_ITEM_TV]):
    """
    Represents a page object list returned by the Notion API
    """

    _ITEM_CLS: ClassVar[Type[_RESULT_ITEM_TV]] = NotionPage
    _OBJECT_TYPE_STR = 'list'

    def _make_result_item(self, data: dict) -> _RESULT_ITEM_TV:
        return self._ITEM_CLS(data=data)

    @classmethod
    @property
    def item(cls) -> Type[_RESULT_ITEM_TV]:
        return cls._ITEM_CLS

    def items(self) -> list[_RESULT_ITEM_TV]:
        return [
            self._make_result_item(data=item_data)
            for item_data in self.data['results']
        ]
