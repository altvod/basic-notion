from __future__ import annotations

import abc
from typing import Any, ClassVar, Optional, TYPE_CHECKING, Type

import attr

from basic_notion import exc

if TYPE_CHECKING:
    from basic_notion.data_gen import DataGenBase


@attr.s(slots=True)
class NotionItemBase(abc.ABC):
    OBJECT_TYPE_KEY_STR: ClassVar[str] = ''
    OBJECT_TYPE_STR: ClassVar[str] = ''
    DATA_GEN_CLS: ClassVar[Optional[Type[DataGenBase]]] = None

    _data: Optional[dict[str, Any]] = attr.ib(kw_only=True, default=None)

    def __attrs_post_init__(self) -> None:
        if self._data is not None and self.OBJECT_TYPE_KEY_STR and self.OBJECT_TYPE_STR:
            assert self._data[self.OBJECT_TYPE_KEY_STR] == self.OBJECT_TYPE_STR

    @property
    def data(self) -> dict:
        if self._data is None:
            raise exc.ItemHasNoData(f'Object {type(self).__name__} has no data')
        return self._data

    @classmethod
    def generate(cls, *args, **kwargs) -> dict:
        assert cls.DATA_GEN_CLS is not None
        return cls.DATA_GEN_CLS(item_cls=cls).generate(*args, **kwargs)
