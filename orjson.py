"""Local compatibility wrapper for JSON operations used across thegent.

This tree mixes true ``orjson`` usage with a legacy contract that expects:
- ``dumps()`` to return bytes
- ``dumps(...).decode().decode()`` to be harmless
- ``dump()`` and ``load()`` helpers to exist
- ``OPT_SORT_KEYS`` and ``OPT_INDENT_2`` flags

The wrapper keeps those call sites working deterministically for tests and CLI
flows without relying on CPython-extension specific behavior.
"""

from __future__ import annotations

import json as _json
from typing import Any, IO

OPT_SORT_KEYS = 1 << 0
OPT_INDENT_2 = 1 << 1

JSONDecodeError = _json.JSONDecodeError


class _DecodedStr(str):
    def decode(self, _encoding: str = "utf-8", _errors: str = "strict") -> "_DecodedStr":
        return self


class _EncodedBytes(bytes):
    def decode(self, encoding: str = "utf-8", errors: str = "strict") -> _DecodedStr:
        return _DecodedStr(super().decode(encoding, errors))


def _normalize_kwargs(*, option: int | None = None, sort_keys: bool = False, indent: int | None = None) -> dict[str, Any]:
    options = option or 0
    normalized_indent = 2 if options & OPT_INDENT_2 else indent
    normalized_sort = bool(sort_keys or options & OPT_SORT_KEYS)
    return {"indent": normalized_indent, "sort_keys": normalized_sort}


def dumps(
    obj: Any,
    /,
    default: Any | None = None,
    option: int | None = None,
    sort_keys: bool = False,
    indent: int | None = None,
    separators: tuple[str, str] | None = None,
) -> _EncodedBytes:
    payload = _json.dumps(
        obj,
        default=default,
        separators=separators,
        **_normalize_kwargs(option=option, sort_keys=sort_keys, indent=indent),
    )
    return _EncodedBytes(payload.encode("utf-8"))


def dump(
    obj: Any,
    fp: IO[str],
    /,
    default: Any | None = None,
    option: int | None = None,
    sort_keys: bool = False,
    indent: int | None = None,
    separators: tuple[str, str] | None = None,
) -> None:
    fp.write(
        dumps(
            obj,
            default=default,
            option=option,
            sort_keys=sort_keys,
            indent=indent,
            separators=separators,
        ).decode()
    )


def loads(data: str | bytes | bytearray, /) -> Any:
    if isinstance(data, (bytes, bytearray)):
        return _json.loads(bytes(data).decode("utf-8"))
    return _json.loads(data)


def load(fp: IO[str], /) -> Any:
    return loads(fp.read())
