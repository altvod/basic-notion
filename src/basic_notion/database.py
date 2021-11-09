from __future__ import annotations

from typing import Any, Optional, Union

import attr

from basic_notion.base import NotionItemBase
from basic_notion.attr import ItemAttrDescriptor
from basic_notion.parent import ParentPage
from basic_notion.property import PropertyList, TextProperty
from basic_notion.schema import Schema


@attr.s(slots=True)
class NotionDatabase(NotionItemBase):
    id: ItemAttrDescriptor[str] = ItemAttrDescriptor()
    url: ItemAttrDescriptor[str] = ItemAttrDescriptor()
    created_time: ItemAttrDescriptor[str] = ItemAttrDescriptor()
    last_edited_time: ItemAttrDescriptor[str] = ItemAttrDescriptor()
    cover: ItemAttrDescriptor[Optional[str]] = ItemAttrDescriptor()
    icon: ItemAttrDescriptor[Optional[str]] = ItemAttrDescriptor()

    # For internal usage
    title_data: ItemAttrDescriptor[list[dict]] = ItemAttrDescriptor(key=('title',))
    properties_data: ItemAttrDescriptor[dict[str, dict]] = ItemAttrDescriptor(key=('properties',))
    parent_data: ItemAttrDescriptor[dict[str, dict]] = ItemAttrDescriptor(key=('parent',))

    @property
    def parent(self) -> ParentPage:
        return ParentPage(data=self.parent_data)

    @property
    def title(self) -> PropertyList[TextProperty]:
        return PropertyList(item_cls=TextProperty, data=self.title_data)

    @property
    def schema(self) -> Schema:
        raise NotImplementedError  # TODO

    @classmethod
    def _make_inst_dict(cls, kwargs: dict[str, Any]) -> dict:
        raw_title: Union[PropertyList[TextProperty], list[str]] = kwargs.get('title', [])
        raw_parent: Union[ParentPage, dict] = kwargs['parent']
        schema = kwargs.get('properties', Schema())

        title: PropertyList[TextProperty]
        if isinstance(raw_title, PropertyList):
            title = raw_title
        else:
            title = PropertyList.make_from_value(
                item_cls=TextProperty,
                property_name='title',
                value=kwargs.get('title', [])
            )

        parent: ParentPage
        if isinstance(raw_parent, ParentPage):
            parent = raw_parent
        else:
            parent = ParentPage(data=raw_parent)

        properties_data = schema.make_spec()

        return {
            'title': title.data,
            'parent': parent.data,
            'properties': properties_data,
        }
