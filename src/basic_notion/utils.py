import datetime
from typing import Any, Optional

import ciso8601


def get_from_dict(dct: dict, key: tuple[str, ...]) -> Any:
    """Get value from dict using a multi-part key"""

    data: Any = dct
    for part in key:
        assert isinstance(data, dict)
        data = data[part]
    return data


def set_to_dict(dct: dict, key: tuple[str, ...], value: Any) -> None:
    """Set value to dict using a multi-part key"""

    data = dct
    *parts, last_part = key
    for part in parts:
        if part not in data:
            data[part] = {}
        new_data = data[part]
        data = new_data

    data[last_part] = value


def del_from_dict(dct: dict, key: tuple[str, ...]) -> None:
    """Delete value from dict using a multi-part key"""

    data = dct
    *parts, last_part = key
    for part in parts:
        if part not in data:
            data[part] = {}
        new_data = data[part]
        data = new_data

    if last_part in data:
        del data[last_part]


def serialize_date(value: Any) -> Optional[str]:
    """A flexible converter for datetime.datetime -> str"""

    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, datetime.datetime):
        return datetime.datetime.isoformat(value)
    raise TypeError(f'Invalid type {type(value)} for date property')


def deserialize_date(value: Any) -> Optional[datetime.datetime]:
    """A flexible converter for str -> datetime.datetime"""

    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        return value
    if isinstance(value, str):
        # datetime.datetime.fromisoformat(...) can't parse Notion's dates,
        # and, anyway, this is faster
        return ciso8601.parse_datetime(value)
    raise TypeError(f'Invalid type {type(value)} for date property')
