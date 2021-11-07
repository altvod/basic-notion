import attr

from basic_notion.base import NotionItemBase
from basic_notion.attr import ItemAttrDescriptor
from basic_notion.data_gen import ParentDataGen


@attr.s(slots=True)
class Parent(NotionItemBase):
    OBJECT_TYPE_KEY_STR = 'type'
    DATA_GEN_CLS = ParentDataGen


@attr.s(slots=True)
class ParentDatabase(Parent):
    OBJECT_TYPE_STR = 'database_id'

    database_id: ItemAttrDescriptor[str] = ItemAttrDescriptor()


@attr.s(slots=True)
class ParentPage(Parent):
    OBJECT_TYPE_STR = 'page_id'

    page_id: ItemAttrDescriptor[str] = ItemAttrDescriptor()
