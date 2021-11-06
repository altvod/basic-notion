from typing import Any, Generic, Optional, Type, TypeVar

from basic_notion.base import NotionItemBase


_PROP_ATTR_TV = TypeVar('_PROP_ATTR_TV')


class ItemAttrDescriptor(Generic[_PROP_ATTR_TV]):
    """
    Accesses attributes of Notion objects (pages and page properties).
    """

    __slots__ = ('__key',)

    def __init__(self, key: Optional[tuple[str, ...]] = None):
        self.__key = key

    def __set_name__(self, owner: NotionItemBase, name: str) -> None:
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
