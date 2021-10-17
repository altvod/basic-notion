from __future__ import annotations

from typing import Any, Optional

import attr

from basic_notion.filter import PropertyFilter


class QuerySerializer:
    @classmethod
    def serialize(cls, query: Query) -> dict:
        data: dict[str, Any] = {
            'database_id': query.database_id,
        }
        if query.filter_obj:
            data['filter'] = {
                "property": query.filter_obj.property_name,
                query.filter_obj.property_type_name: {
                    query.filter_obj.filter_name: query.filter_obj.filter_value,
                },
            }

        return data


@attr.s(frozen=True)
class Query:
    _database_id: str = attr.ib()
    _filter: Optional[PropertyFilter] = attr.ib(kw_only=True, default=None)
    _serializer: QuerySerializer = attr.ib(kw_only=True, factory=QuerySerializer)

    def clone(self, **kwargs: Any) -> Query:
        return attr.evolve(self, **kwargs)

    @property
    def database_id(self) -> str:
        return self._database_id

    @property
    def filter_obj(self) -> Optional[PropertyFilter]:
        return self._filter

    def filter(self, filter: PropertyFilter) -> Query:
        return self.clone(filter=filter)

    def serialize(self) -> dict:
        return self._serializer.serialize(self)
