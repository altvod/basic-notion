import abc
from typing import Any, ClassVar, Optional

import attr

from basic_notion import exc


@attr.s(frozen=True)
class NotionItemBase(abc.ABC):
    OBJECT_TYPE_KEY_STR: ClassVar[str] = ''
    OBJECT_TYPE_STR: ClassVar[str] = ''

    _data: Optional[dict[str, Any]] = attr.ib(kw_only=True, default=None)

    def __attrs_post_init__(self) -> None:
        if self._data is not None and self.OBJECT_TYPE_KEY_STR and self.OBJECT_TYPE_STR:
            assert self._data[self.OBJECT_TYPE_KEY_STR] == self.OBJECT_TYPE_STR

    @property
    def data(self) -> dict:
        if self._data is None:
            raise exc.ItemHasNoData(f'Object {type(self).__name__} has no data')
        return self._data
