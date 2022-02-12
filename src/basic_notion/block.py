from __future__ import annotations

import datetime
import inspect
from typing import Any, ClassVar, Optional

from basic_notion.base import NotionItemBaseMetaclass, NotionItemBase
from basic_notion.schema import Schema
from basic_notion.property_schema import PropertySchema, TextListSchema
from basic_notion.attr import ItemAttrDescriptor
from basic_notion.property import PropertyList, TextProperty
from basic_notion.field import NotionField
from basic_notion.utils import deserialize_date


def _make_schema_for_block_cls(page_cls: type) -> Schema:
    return Schema({
        name: prop
        for name, prop in inspect.getmembers(page_cls)
        if isinstance(prop, PropertySchema)
    })


class NotionBlockMetaclass(NotionItemBaseMetaclass):
    """Metaclass for NotionBlock that adds `schema` to its attributes"""

    def __new__(cls, name: str, bases: tuple[type, ...], dct: dict):
        new_cls = super().__new__(cls, name, bases, dct)
        new_cls.__notion_schema__ = _make_schema_for_block_cls(new_cls)  # type: ignore
        return new_cls


class NotionBlock(NotionItemBase, metaclass=NotionBlockMetaclass):
    __notion_schema__: Schema = None  # type: ignore  # defined in metaclass

    OBJECT_TYPE_KEY_STR = 'object'
    OBJECT_TYPE_STR = 'block'
    BLOCK_TYPE_STR: ClassVar[str]

    id: ItemAttrDescriptor[str] = ItemAttrDescriptor()
    type: ItemAttrDescriptor[str] = ItemAttrDescriptor(editable=False)
    archived: ItemAttrDescriptor[bool] = ItemAttrDescriptor(editable=True)
    created_time: ItemAttrDescriptor[Optional[datetime.datetime]] = ItemAttrDescriptor(
        derived=True, get_converter=deserialize_date)
    created_time_str: ItemAttrDescriptor[str] = ItemAttrDescriptor(derived=True)
    last_edited_time: ItemAttrDescriptor[Optional[datetime.datetime]] = ItemAttrDescriptor(
        derived=True, get_converter=deserialize_date)
    last_edited_time_str: ItemAttrDescriptor[str] = ItemAttrDescriptor(derived=True)

    @property
    def _custom_data(self) -> dict:
        return self.data[self.BLOCK_TYPE_STR]

    @classmethod
    @property
    def schema(cls) -> Schema:
        return cls.__notion_schema__

    @classmethod
    def _make_inst_prop_dict(cls, kwargs: dict[str, Any]) -> dict:
        data = {}
        for name, prop_sch in cls.schema.items():  # type: ignore
            if name not in kwargs:
                continue
            data[prop_sch.property_name] = prop_sch.make_prop_from_value(value=kwargs[name]).data
        return data

    @classmethod
    def _make_inst_dict(cls, kwargs: dict[str, Any]) -> dict:
        data = super()._make_inst_dict(kwargs)
        data['type'] = cls.BLOCK_TYPE_STR
        data[cls.BLOCK_TYPE_STR] = data.get(cls.BLOCK_TYPE_STR, {})
        data[cls.BLOCK_TYPE_STR].update(cls._make_inst_prop_dict(kwargs))
        return data

    @classmethod
    def make_as_children_data(cls, block_id: str, **kwargs) -> dict:
        return {
            'block_id': block_id,
            'children': [cls.make(**kwargs).data],
        }


class TextListField(NotionField[TextListSchema, PropertyList[TextProperty]]):
    __slots__ = ()

    PROP_SCHEMA_CLS = TextListSchema
    PROP_CLS = TextProperty
    IS_LIST = True


class _BlockWithText(NotionBlock):
    BLOCK_TYPE_STR = 'paragraph'

    text: TextListField = TextListField(root_key=(BLOCK_TYPE_STR,))


class ParagraphBlock(NotionBlock):
    BLOCK_TYPE_STR = 'paragraph'

    text: TextListField = TextListField(root_key=(BLOCK_TYPE_STR,))


class Heading1Block(NotionBlock):
    BLOCK_TYPE_STR = 'heading_1'

    text: TextListField = TextListField(root_key=(BLOCK_TYPE_STR,))


class Heading2Block(NotionBlock):
    BLOCK_TYPE_STR = 'heading_2'

    text: TextListField = TextListField(root_key=(BLOCK_TYPE_STR,))


class Heading3Block(NotionBlock):
    BLOCK_TYPE_STR = 'heading_3'

    text: TextListField = TextListField(root_key=(BLOCK_TYPE_STR,))


class CalloutBlock(NotionBlock):
    BLOCK_TYPE_STR = 'callout'

    text: TextListField = TextListField(root_key=(BLOCK_TYPE_STR,))
    # TODO: icon


class BulletedListItemBlock(NotionBlock):
    BLOCK_TYPE_STR = 'bulleted_list_item'

    text: TextListField = TextListField(root_key=(BLOCK_TYPE_STR,))


class NumberedListItemBlock(NotionBlock):
    BLOCK_TYPE_STR = 'numbered_list_item'

    text: TextListField = TextListField(root_key=(BLOCK_TYPE_STR,))


class ToDoBlock(NotionBlock):
    BLOCK_TYPE_STR = 'to_do'

    text: TextListField = TextListField(root_key=(BLOCK_TYPE_STR,))
    checked: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=(BLOCK_TYPE_STR, 'checked'), editable=True)


class ToggleBlock(NotionBlock):
    BLOCK_TYPE_STR = 'toggle'

    text: TextListField = TextListField(root_key=(BLOCK_TYPE_STR,))


class CodeBlock(NotionBlock):
    BLOCK_TYPE_STR = 'code'

    text: TextListField = TextListField(root_key=(BLOCK_TYPE_STR,))
    caption: TextListField = TextListField(root_key=(BLOCK_TYPE_STR,))
    language: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=(BLOCK_TYPE_STR, 'language'), editable=True)


class ChildPageBlock(NotionBlock):
    BLOCK_TYPE_STR = 'child_page'

    title: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=(BLOCK_TYPE_STR, 'title'), editable=True)


class ChildDatabaseBlock(NotionBlock):
    BLOCK_TYPE_STR = 'child_database'

    title: ItemAttrDescriptor[str] = ItemAttrDescriptor(key=(BLOCK_TYPE_STR, 'title'), editable=True)
