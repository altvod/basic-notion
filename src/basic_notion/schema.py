from __future__ import annotations

from typing import Iterable, Mapping

import attr

from basic_notion.property_schema import PropertySchema, get_property_schema_cls


@attr.s(frozen=True)
class Schema:
    _properties: Mapping[str, PropertySchema] = attr.ib(factory=dict)

    @property
    def properties(self) -> Mapping[str, PropertySchema]:
        return self._properties

    def __getitem__(self, item: str) -> PropertySchema:
        return self._properties[item]

    def __contains__(self, item: str) -> bool:
        return item in self._properties

    def items(self) -> Iterable[tuple[str, PropertySchema]]:
        yield from self._properties.items()

    def make_spec(self) -> dict[str, dict]:
        return {
            prop.property_name: prop.data
            for prop in self._properties.values()
        }


def load_schema_from_dict(raw_data: dict) -> Schema:
    data = {
        name: get_property_schema_cls(prop_data['type'])(
            property_name=name,
            data=prop_data,
        )
        for name, prop_data in raw_data.items()
        if 'type' in prop_data
    }
    return Schema(properties=data)
