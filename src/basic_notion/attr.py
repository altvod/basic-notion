from typing import Any, Generic, Optional, Type, TypeVar

from basic_notion.base import NotionItemBase


_PROP_ATTR_TV = TypeVar('_PROP_ATTR_TV')


class ItemAttrDescriptor(Generic[_PROP_ATTR_TV]):
    """
    Accesses attributes of Notion objects (pages and page properties).
    """

    __slots__ = ('__key', '__name', '__editable')

    def __init__(self, key: Optional[tuple[str, ...]] = None, editable: bool = False):
        self.__key = key
        self.__name: Optional[str] = None
        self.__editable = editable

    def __set_name__(self, owner: NotionItemBase, name: str) -> None:
        self.__name = name
        if self.__key is None:
            self.__key = (name,)

    @property
    def _key(self) -> tuple[str, ...]:
        assert self.__key is not None
        return self.__key

    def __get__(self, instance: NotionItemBase, owner: Type[NotionItemBase]) -> _PROP_ATTR_TV:
        data: Any = instance.data
        for part in self._key:
            assert isinstance(data, dict)
            data = data[part]
        return data

    def __set__(self, instance: NotionItemBase, value: _PROP_ATTR_TV) -> None:
        if not self.__editable:
            raise AttributeError(f'Attribute {self.__name} is not editable')

        data: Any = instance.data
        *parts, last_part = self._key
        for part in parts:
            assert isinstance(data, dict)
            data = data[part]
        assert isinstance(data, dict)
        data[last_part] = value
