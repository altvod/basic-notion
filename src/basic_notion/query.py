from __future__ import annotations

from typing import Any, Optional, Sequence, Type, TypeVar

import attr

from basic_notion.filter import PropertyFilter
from basic_notion.sort import Sort


class QuerySerializer:
    @classmethod
    def serialize(cls, query: Query) -> dict:
        data: dict[str, Any] = {
            'database_id': query.database_id,
        }
        if query.filter_obj is not None:
            data['filter'] = {
                "property": query.filter_obj.property_name,
                query.filter_obj.property_type_name: {
                    query.filter_obj.filter_name: query.filter_obj.filter_value,
                },
            }
        if query.sorts_obj is not None:
            data['sorts'] = []
            for sorts_item in query.sorts_obj:
                sorts_item_data = {
                    "direction": sorts_item.direction,
                }
                if sorts_item.property is not None:
                    sorts_item_data['property'] = sorts_item.property
                if sorts_item.timestamp is not None:
                    sorts_item_data['timestamp'] = sorts_item.timestamp
                data['sorts'].append(sorts_item_data)

        return data


_QUERY_TV = TypeVar('_QUERY_TV', bound='Query')


@attr.s(frozen=True)
class Query:
    _database_id: str = attr.ib(kw_only=True)
    _filter: Optional[PropertyFilter] = attr.ib(kw_only=True, default=None)
    _sorts: Optional[Sequence] = attr.ib(kw_only=True, default=None)
    _serializer: QuerySerializer = attr.ib(kw_only=True, factory=QuerySerializer)

    def clone(self, **kwargs: Any) -> Query:
        return attr.evolve(self, **kwargs)

    @property
    def database_id(self) -> str:
        return self._database_id

    @property
    def filter_obj(self) -> Optional[PropertyFilter]:
        return self._filter

    @property
    def sorts_obj(self) -> Optional[Sequence[Sort]]:
        return self._sorts

    @classmethod
    def database(cls: Type[_QUERY_TV], database_id: str) -> _QUERY_TV:
        return cls(database_id=database_id)

    def filter(self, filter: PropertyFilter) -> Query:
        return self.clone(filter=filter)

    def sorts(self, *sorts: Sort) -> Query:
        return self.clone(sorts=sorts)

    def serialize(self) -> dict:
        return self._serializer.serialize(self)
