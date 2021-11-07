from __future__ import annotations

import inspect
from typing import ClassVar, Generic, Optional, Type, TypeVar, TYPE_CHECKING

import attr

from basic_notion.base import NotionItemBase
from basic_notion.attr import ItemAttrDescriptor
from basic_notion.parent import ParentDatabase, ParentPage
from basic_notion.data_gen import PageDataGen

if TYPE_CHECKING:
    from basic_notion.parent import Parent
    from basic_notion.property import PageProperty


@attr.s(slots=True)
class NotionPage(NotionItemBase):
    """
    Represents a page object returned by the Notion API
    """

    OBJECT_TYPE_KEY_STR = 'object'
    OBJECT_TYPE_STR = 'page'
    DATA_GEN_CLS = PageDataGen

    id: ItemAttrDescriptor[str] = ItemAttrDescriptor()
    archived: ItemAttrDescriptor[bool] = ItemAttrDescriptor(editable=True)
    url: ItemAttrDescriptor[str] = ItemAttrDescriptor()
    created_time: ItemAttrDescriptor[str] = ItemAttrDescriptor()
    last_edited_time: ItemAttrDescriptor[str] = ItemAttrDescriptor()
    cover: ItemAttrDescriptor[Optional[str]] = ItemAttrDescriptor()
    icon: ItemAttrDescriptor[Optional[str]] = ItemAttrDescriptor()

    # For internal usage
    properties_data: ItemAttrDescriptor[dict[str, dict]] = ItemAttrDescriptor(key=('properties',))
    parent_data: ItemAttrDescriptor[dict[str, dict]] = ItemAttrDescriptor(key=('parent',))

    @classmethod
    def get_class_fields(cls) -> dict[str, PageProperty]:
        from basic_notion.property import PageProperty
        return {
            name: prop
            for name, prop in inspect.getmembers(cls)
            if isinstance(prop, PageProperty)
        }

    @property
    def parent(self) -> Parent:
        parent_type = self.parent_data['type']
        parent: Parent

        # TODO: This would be a great place to use match-case,
        #   but mypy doesn't support it yet: https://github.com/python/mypy/pull/10191

        if parent_type == ParentPage.OBJECT_TYPE_STR:
            parent = ParentPage(data=self.parent_data)
        elif parent_type == ParentDatabase.OBJECT_TYPE_STR:
            parent = ParentDatabase(data=self.parent_data)
        else:
            raise ValueError(f'Unknown parent type: {parent_type}')

        return parent

    # TODO: properties that convert `ct` and `let` into datetimes. Something wrong with isoformat


_RESULT_ITEM_TV = TypeVar('_RESULT_ITEM_TV', bound=NotionPage)


@attr.s(slots=True)
class NotionPageList(NotionItemBase, Generic[_RESULT_ITEM_TV]):
    """
    Represents a page object list returned by the Notion API
    """

    ITEM_CLS: ClassVar[Optional[Type[_RESULT_ITEM_TV]]] = None
    OBJECT_TYPE_KEY_STR = 'object'
    OBJECT_TYPE_STR = 'list'

    @classmethod
    def _get_item_cls(cls) -> Type[_RESULT_ITEM_TV]:
        assert cls.ITEM_CLS is not None
        return cls.ITEM_CLS

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
