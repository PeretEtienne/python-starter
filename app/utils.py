from typing import Annotated, Literal, Optional, Tuple, TypeVar, cast, get_args

from fastapi import Query

T = TypeVar("T")


def not_none(obj: Optional[T]) -> T:
    if obj is None:
        raise ValueError("Expected non-null value.")
    return obj


SortDirection = Literal["asc", "desc"]


def parse_sort(
    sort: Annotated[str | None, Query()] = None,
) -> list[Tuple[str, SortDirection]]:
    if not sort:
        return []
    result: list[Tuple[str, SortDirection]] = []
    for part in sort.split(";"):
        try:
            key, direction = part.split(",")
            result.append((key.strip(), parse_direction(direction)))
        except Exception as err:
            raise ValueError("Sort must be like: name,asc;age,desc") from err
    return result


def parse_direction(value: str) -> SortDirection:
    value = value.strip().lower()
    if value not in get_args(SortDirection):
        raise ValueError
    return cast(SortDirection, value)
