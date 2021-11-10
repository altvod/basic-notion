from __future__ import annotations

from typing import Generic, Optional, TYPE_CHECKING, Type, TypeVar

from basic_notion.utils import get_from_dict, set_to_dict, del_from_dict

if TYPE_CHECKING:
    from basic_notion.base import NotionItemBase


_PROP_ATTR_TV = TypeVar('_PROP_ATTR_TV')


class ItemAttrDescriptor(Generic[_PROP_ATTR_TV]):
    """
    Accesses attributes of Notion objects (pages and page properties).
    """

    __slots__ = (
        '__key', '__name', '__editable', '__derived',
        '__clear_on_set',
    )

    def __init__(
            self, key: Optional[tuple[str, ...]] = None,
            editable: bool = False, derived: bool = False,
            clear_on_set: bool = True,
    ):
        if editable and derived:
            raise ValueError('Attribute cannot be editable and derived at the same time')
        self.__key = key
        self.__name: Optional[str] = None
        self.__editable = editable
        self.__derived = derived
        self.__clear_on_set = clear_on_set

    def __set_name__(self, owner: NotionItemBase, name: str) -> None:
        self.__name = name
        if self.__key is None:
            self.__key = (name,)

    @property
    def key(self) -> tuple[str, ...]:
        if self.__key is None:
            raise AttributeError('Key is not specified')
        return self.__key

    @property
    def editable(self) -> bool:
        return self.__editable

    @property
    def derived(self) -> bool:
        return self.__derived

    def __get__(self, instance: NotionItemBase, owner: Type[NotionItemBase]) -> _PROP_ATTR_TV:
        return get_from_dict(instance.data, self.key)

    def __set__(self, instance: NotionItemBase, value: _PROP_ATTR_TV) -> None:
        if not self.__editable:
            raise AttributeError(f'Attribute {self.__name} is not editable')

        try:
            old_value = get_from_dict(instance.data, self.key)
            if value == old_value:
                # Nothing to do
                return
        except KeyError:
            # The value wasn't there to begin with, so just set it
            pass

        set_to_dict(instance.data, self.key, value)
        if self.__clear_on_set:
            # Clear non-editable (derived) attributes to avoid value conflicts on update
            instance.clear_derived_attrs()
