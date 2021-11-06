import attr

from basic_notion.base import NotionItemBase
from basic_notion.attr import ItemAttrDescriptor


@attr.s(frozen=True)
class Parent(NotionItemBase):
    _OBJECT_TYPE_KEY_STR = 'type'


@attr.s(frozen=True)
class ParentDatabase(Parent):
    _OBJECT_TYPE_STR = 'database_id'

    database_id: ItemAttrDescriptor[str] = ItemAttrDescriptor()


@attr.s(frozen=True)
class ParentPage(Parent):
    _OBJECT_TYPE_STR = 'page_id'

    page_id: ItemAttrDescriptor[str] = ItemAttrDescriptor()
