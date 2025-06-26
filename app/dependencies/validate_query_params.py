import json
import re
from typing import Any, Callable, Coroutine, Dict, Type, cast

from benedict import benedict  # type: ignore
from fastapi import HTTPException, Request
from pydantic import BaseModel, ValidationError
from starlette.datastructures import QueryParams


def build_nested_structure(data: QueryParams) -> Dict[str, Any]:
    result = benedict()

    for key, value in data.items():
        keys = re.findall(r"([^\[\]]+)", key)

        path = create_path(keys)

        result[path] = value

    return cast(Dict[str, Any], json.loads(result.to_json()))


def create_path(params: list[str]) -> str:
    path_parts = []
    for item in params:
        if str(item).isdigit():
            path_parts.append(f"[{item}]")
        else:
            path_parts.append(f".{item}" if path_parts else item)
    return "".join(path_parts)


async def parse_query_with_validation(
    request: Request,
    model: Type[BaseModel],
) -> BaseModel:
    try:
        raw_params = build_nested_structure(request.query_params)
        return model(**raw_params)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors()) from e


def validate_query_params(
    model: Type[BaseModel],
) -> Callable[[Request], Coroutine[Any, Any, BaseModel]]:
    async def dependency(request: Request) -> BaseModel:
        return await parse_query_with_validation(request, model)

    return dependency

