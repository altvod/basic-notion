from __future__ import annotations

from typing import Any

import attr

from basic_notion.base import NotionItemBase
from basic_notion.attr import ItemAttrDescriptor


@attr.s(slots=True)
class Parent(NotionItemBase):
    OBJECT_TYPE_KEY_STR = 'type'


@attr.s(slots=True)
class ParentDatabase(Parent):
    OBJECT_TYPE_STR = 'database_id'

    database_id: ItemAttrDescriptor[str] = ItemAttrDescriptor()

    @classmethod
    def make(cls, **kwargs: Any) -> ParentDatabase:
        return cls(data={'database_id': kwargs['database_id']})


@attr.s(slots=True)
class ParentPage(Parent):
    OBJECT_TYPE_STR = 'page_id'

    page_id: ItemAttrDescriptor[str] = ItemAttrDescriptor()

    @classmethod
    def make(cls, **kwargs: Any) -> ParentPage:
        return cls(data={'page_id': kwargs['page_id']})
