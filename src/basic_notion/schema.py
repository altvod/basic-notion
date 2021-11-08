from __future__ import annotations

from typing import Iterable, Mapping

import attr

from basic_notion.property import PageProperty


@attr.s(frozen=True)
class Schema:
    _properties: Mapping[str, PageProperty] = attr.ib()

    @property
    def properties(self) -> Mapping[str, PageProperty]:
        return self._properties

    def __getitem__(self, item: str) -> PageProperty:
        return self._properties[item]

    def __contains__(self, item: str) -> bool:
        return item in self._properties

    def items(self) -> Iterable[tuple[str, PageProperty]]:
        yield from self._properties.items()
