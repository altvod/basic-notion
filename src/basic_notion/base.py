import abc
from typing import Any, ClassVar, Optional

import attr

from basic_notion import exc


@attr.s(frozen=True)
class NotionItemBase(abc.ABC):
    _OBJECT_TYPE_KEY_STR: ClassVar[str] = ''
    _OBJECT_TYPE_STR: ClassVar[str] = ''

    _data: Optional[dict[str, Any]] = attr.ib(kw_only=True, default=None)

    def __attrs_post_init__(self) -> None:
        if self._data is not None and self._OBJECT_TYPE_KEY_STR and self._OBJECT_TYPE_STR:
            assert self._data[self._OBJECT_TYPE_KEY_STR] == self._OBJECT_TYPE_STR

    @property
    def data(self) -> dict:
        if self._data is None:
            raise exc.ItemHasNoData(f'Object {type(self).__name__} has no data')
        return self._data
