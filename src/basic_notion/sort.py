from enum import Enum, unique
from typing import Optional

import attr


@unique
class SortDirection(Enum):
    ascending = 'ascending'
    descending = 'descending'


@attr.s(frozen=True)
class Sort:
    property: Optional[str] = attr.ib(kw_only=True)
    timestamp: Optional[str] = attr.ib(kw_only=True, default=None)
    direction: str = attr.ib(kw_only=True, default=SortDirection.ascending.name)


@attr.s(frozen=True)
class SortFactory:
    _property_name: str = attr.ib(kw_only=True)

    @property
    def ascending(self) -> Sort:
        return Sort(property=self._property_name, direction=SortDirection.ascending.name)

    @property
    def descending(self) -> Sort:
        return Sort(property=self._property_name, direction=SortDirection.descending.name)
