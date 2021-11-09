from typing import Any


def get_from_dict(dct: dict, key: tuple[str, ...]) -> Any:
    data: Any = dct
    for part in key:
        assert isinstance(data, dict)
        data = data[part]
    return data


def set_to_dict(dct: dict, key: tuple[str, ...], value: Any) -> None:
    data = dct
    *parts, last_part = key
    for part in parts:
        new_data: dict[str, Any] = {}
        data[part] = new_data
        data = new_data

    data[last_part] = value
