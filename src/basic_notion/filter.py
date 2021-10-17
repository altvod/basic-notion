from typing import Any, Generic, Optional, Type, TypeVar, Union

import attr


NUMBER = Union[int, float]

_FILTER_VALUE_TV = TypeVar('_FILTER_VALUE_TV')


@attr.s(frozen=True)
class PropertyFilter:
    property_name: str = attr.ib(kw_only=True)
    property_type_name: str = attr.ib(kw_only=True)
    filter_name: str = attr.ib(kw_only=True)
    filter_value: Any = attr.ib(kw_only=True)


@attr.s(frozen=True)
class FilterFactory:
    _property_name: str = attr.ib(kw_only=True)
    _property_type_name: str = attr.ib(kw_only=True)

    @property
    def property_name(self) -> str:
        return self._property_name

    @property
    def property_type_name(self) -> str:
        return self._property_type_name


@attr.s(frozen=True)
class FilterGen(Generic[_FILTER_VALUE_TV]):
    _property_name: str = attr.ib(kw_only=True)
    _property_type_name: str = attr.ib(kw_only=True)
    _filter_name: str = attr.ib(kw_only=True)

    def __call__(self, filter_value: _FILTER_VALUE_TV) -> PropertyFilter:
        return PropertyFilter(
            property_name=self._property_name,
            property_type_name=self._property_type_name,
            filter_name=self._filter_name,
            filter_value=filter_value,
        )


@attr.s(slots=True)
class FilterGenDescriptor(Generic[_FILTER_VALUE_TV]):
    _filter_name: Optional[str] = attr.ib(kw_only=True, default=None)

    def __set_name__(self, owner: type, name: str) -> None:
        self._filter_name = name

    def __get__(self, instance: FilterFactory, owner: Type[FilterFactory]) -> FilterGen[_FILTER_VALUE_TV]:
        assert self._filter_name is not None
        return FilterGen(
            property_name=instance.property_name,
            property_type_name=instance.property_type_name,
            filter_name=self._filter_name,
        )


@attr.s(frozen=True)
class TextFilterFactory(FilterFactory):
    equals: FilterGen[str] = FilterGenDescriptor()
    does_not_equal: FilterGen[str] = FilterGenDescriptor()
    contains: FilterGen[str] = FilterGenDescriptor()
    does_not_contain: FilterGen[str] = FilterGenDescriptor()
    starts_with: FilterGen[str] = FilterGenDescriptor()
    ends_with: FilterGen[str] = FilterGenDescriptor()
    is_empty: FilterGen[bool] = FilterGenDescriptor()
    is_not_empty: FilterGen[bool] = FilterGenDescriptor()


@attr.s(frozen=True)
class NumberFilterFactory(FilterFactory):
    equals: FilterGen[NUMBER] = FilterGenDescriptor()
    does_not_equal: FilterGen[NUMBER] = FilterGenDescriptor()
    greater_than: FilterGen[NUMBER] = FilterGenDescriptor()
    less_than: FilterGen[NUMBER] = FilterGenDescriptor()
    greater_than_or_equal_to: FilterGen[NUMBER] = FilterGenDescriptor()
    less_than_or_equal_to: FilterGen[NUMBER] = FilterGenDescriptor()
    is_empty: FilterGen[bool] = FilterGenDescriptor()
    is_not_empty: FilterGen[bool] = FilterGenDescriptor()


@attr.s(frozen=True)
class CheckboxFilterFactory(FilterFactory):
    equals: FilterGen[bool] = FilterGenDescriptor()
    does_not_equal: FilterGen[bool] = FilterGenDescriptor()


@attr.s(frozen=True)
class SelectFilterFactory(FilterFactory):
    equals: FilterGen[str] = FilterGenDescriptor()
    does_not_equal: FilterGen[str] = FilterGenDescriptor()
    is_empty: FilterGen[bool] = FilterGenDescriptor()
    is_not_empty: FilterGen[bool] = FilterGenDescriptor()


@attr.s(frozen=True)
class MultiSelectFilterFactory(FilterFactory):
    equals: FilterGen[str] = FilterGenDescriptor()
    does_not_equal: FilterGen[str] = FilterGenDescriptor()
    is_empty: FilterGen[bool] = FilterGenDescriptor()
    is_not_empty: FilterGen[bool] = FilterGenDescriptor()


@attr.s(frozen=True)
class FilesFilterFactory(FilterFactory):
    is_empty: FilterGen[bool] = FilterGenDescriptor()
    is_not_empty: FilterGen[bool] = FilterGenDescriptor()
