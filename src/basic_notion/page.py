from typing import ClassVar, Generic, Optional, Type, TypeVar

import attr

from basic_notion.base import NotionItemBase
from basic_notion.attr import ItemAttrDescriptor


@attr.s(frozen=True)
class NotionPage(NotionItemBase):
    """
    Represents a page object returned by the Notion API
    """

    _OBJECT_TYPE_KEY_STR = 'object'
    _OBJECT_TYPE_STR = 'page'

    id: ItemAttrDescriptor[str] = ItemAttrDescriptor()
    archived: ItemAttrDescriptor[bool] = ItemAttrDescriptor()
    url: ItemAttrDescriptor[str] = ItemAttrDescriptor()
    created_time: ItemAttrDescriptor[str] = ItemAttrDescriptor()
    last_edited_time: ItemAttrDescriptor[str] = ItemAttrDescriptor()
    cover: ItemAttrDescriptor[Optional[str]] = ItemAttrDescriptor()
    icon: ItemAttrDescriptor[Optional[str]] = ItemAttrDescriptor()
    # For usage by fields
    properties_data: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=('properties',))

    # TODO: properties that convert `ct` and `let` into datetimes. Something wrong with isoformat


_RESULT_ITEM_TV = TypeVar('_RESULT_ITEM_TV', bound=NotionPage)


@attr.s(frozen=True)
class NotionPageList(NotionItemBase, Generic[_RESULT_ITEM_TV]):
    """
    Represents a page object list returned by the Notion API
    """

    _ITEM_CLS: ClassVar[Optional[Type[_RESULT_ITEM_TV]]] = None
    _OBJECT_TYPE_KEY_STR = 'object'
    _OBJECT_TYPE_STR = 'list'

    @classmethod
    def _get_item_cls(cls) -> Type[_RESULT_ITEM_TV]:
        assert cls._ITEM_CLS is not None
        return cls._ITEM_CLS

    def _make_result_item(self, data: dict) -> _RESULT_ITEM_TV:
        return self._get_item_cls()(data=data)

    @classmethod
    @property
    def item(cls) -> Type[_RESULT_ITEM_TV]:
        return cls._get_item_cls()

    def items(self) -> list[_RESULT_ITEM_TV]:
        return [
            self._make_result_item(data=item_data)
            for item_data in self.data['results']
        ]
