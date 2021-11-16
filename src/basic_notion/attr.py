from __future__ import annotations

from typing import Any, Callable, Generic, Optional, TYPE_CHECKING, Type, TypeVar, overload

from basic_notion.utils import get_from_dict, set_to_dict

if TYPE_CHECKING:
    from basic_notion.base import NotionItemBase


_PROP_ATTR_TV = TypeVar('_PROP_ATTR_TV')
_ATTR_TV = TypeVar('_ATTR_TV', bound='ItemAttrDescriptor')


class ItemAttrDescriptor(Generic[_PROP_ATTR_TV]):
    """
    Accesses attributes of Notion objects
    (of pages and page properties).
    """

    __slots__ = (
        '__key', '__name', '__editable', '__derived',
        '__clear_on_set', '__get_converter', '__set_converter',
    )

    def __init__(
            self,
            key: Optional[tuple[str, ...]] = None,
            editable: bool = False,
            derived: bool = False,
            clear_on_set: bool = True,
            get_converter: Optional[Callable[[Any], _PROP_ATTR_TV]] = None,
            set_converter: Optional[Callable[[_PROP_ATTR_TV], Any]] = None,
    ):
        if editable and derived:
            raise ValueError('Attribute cannot be editable and derived at the same time')
        self.__key = key
        self.__name: Optional[str] = None
        self.__editable = editable
        self.__derived = derived
        self.__clear_on_set = clear_on_set

        if not editable and set_converter is not None:
            raise ValueError('Cannot use set_converter with non-editable attrs')
        self.__get_converter = get_converter
        self.__set_converter = set_converter

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
    def set_converter(self) -> Optional[Callable[[_PROP_ATTR_TV], Any]]:
        return self.__set_converter

    @property
    def derived(self) -> bool:
        return self.__derived

    @overload
    def __get__(self: _ATTR_TV, instance: None, owner: Type[NotionItemBase]) -> _ATTR_TV: ...

    @overload
    def __get__(self, instance: NotionItemBase, owner: Type[NotionItemBase]) -> _PROP_ATTR_TV: ...

    def __get__(self, instance, owner):
        if instance is None:
            return self

        value = get_from_dict(instance.data, self.key)
        if self.__get_converter is not None:
            value = self.__get_converter(value)
        return value

    def __set__(self, instance: Optional[NotionItemBase], value: _PROP_ATTR_TV) -> None:
        if instance is None:
            raise TypeError('Cannot set attribute value without instance')

        if not self.__editable:
            raise AttributeError(f'Attribute {self.__name} is not editable')

        try:
            if self.__set_converter is not None:
                value = self.__set_converter(value)

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
