from __future__ import annotations

import inspect
from typing import Any, ClassVar, Generic, Optional, Type, TypeVar

import attr

from basic_notion.base import NotionItemBase, NotionItemBaseMetaclass
from basic_notion.attr import ItemAttrDescriptor
from basic_notion.parent import Parent, ParentDatabase, ParentPage
from basic_notion.property import PageProperty
from basic_notion.schema import Schema


def _make_schema_for_page_cls(page_cls: type) -> Schema:
    return Schema({
        name: prop
        for name, prop in inspect.getmembers(page_cls)
        if isinstance(prop, PageProperty)
    })


class NotionPageMetaclass(NotionItemBaseMetaclass):
    """Metaclass for NotionPage that adds `schema` to its attributes"""

    def __new__(cls, name: str, bases: tuple[type, ...], dct: dict):
        new_cls = super().__new__(cls, name, bases, dct)
        new_cls.__notion_schema__ = _make_schema_for_page_cls(new_cls)  # type: ignore
        return new_cls


@attr.s(slots=True)
class NotionPage(NotionItemBase, metaclass=NotionPageMetaclass):  # noqa
    """
    Represents a page object returned by the Notion API
    """

    __notion_schema__: Schema  # type: ignore  # defined in metaclass

    OBJECT_TYPE_KEY_STR = 'object'
    OBJECT_TYPE_STR = 'page'

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
    @property
    def schema(cls) -> Schema:
        return cls.__notion_schema__

    @property
    def parent(self) -> Parent:
        parent_type = self.parent_data['type']
        parent: Parent

        # TODO: This would be a great place to use match-case,
        #  but mypy doesn't support it yet: https://github.com/python/mypy/pull/10191

        if parent_type == ParentPage.OBJECT_TYPE_STR:
            parent = ParentPage(data=self.parent_data)
        elif parent_type == ParentDatabase.OBJECT_TYPE_STR:
            parent = ParentDatabase(data=self.parent_data)
        else:
            raise ValueError(f'Unknown parent type: {parent_type}')

        return parent

    # TODO: properties that convert `created_time` and `last_edited_time` into datetimes.
    #  Something wrong with isoformat

    @classmethod
    def _make_inst_prop_dict(cls, kwargs: dict[str, Any]) -> dict:
        data = {}
        for name, prop in cls.schema.items():  # type: ignore
            if name not in kwargs:
                continue
            data[prop.property_name] = prop.make_from_value(
                property_name=prop.property_name, value=kwargs[name],
            ).data
        return data

    @classmethod
    def _make_inst_dict(cls, kwargs: dict[str, Any]) -> dict:
        data = super()._make_inst_dict(kwargs)
        parent = kwargs['parent']
        parent_data: dict
        if isinstance(parent, Parent):
            parent_data = parent.data
        elif isinstance(parent, dict):
            parent_data = parent
        else:
            raise TypeError(type(parent))
        data['parent'] = parent_data
        data['properties'] = cls._make_inst_prop_dict(kwargs)
        return data


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
