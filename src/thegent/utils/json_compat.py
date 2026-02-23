"""JSON compatibility layer - drop-in replacement for stdlib json using orjson.

This module provides a compatible interface to stdlib json while using orjson
under the hood for significant performance improvements (3-5x faster).

Usage:
    from thegent.utils.json_compat import json
    # Now use json.loads(), json.dumps(), etc. as normal

Note:
    - orjson.dumps() returns bytes, this wrapper decodes to str for compatibility
    - orjson.loads() accepts both bytes and str, works with either
"""

from __future__ import annotations

from typing import Any

import orjson

# Re-export orjson options for advanced usage
OPT_INDENT_2 = orjson.OPT_INDENT_2
OPT_SORT_KEYS = orjson.OPT_SORT_KEYS
OPT_NAIVE_UTC = orjson.OPT_NAIVE_UTC
OPT_UTC_Z = orjson.OPT_UTC_Z
OPT_SERIALIZE_NUMPY = orjson.OPT_SERIALIZE_NUMPY
OPT_SERIALIZE_UUID = orjson.OPT_SERIALIZE_UUID
OPT_NON_STR_KEYS = orjson.OPT_NON_STR_KEYS


def dumps(
    obj: Any,
    *,
    default: Any = None,
    indent: bool | None = None,
    sort_keys: bool = False,
    **kwargs: Any,
) -> str:
    """Serialize obj to a JSON formatted string.
    
    Args:
        obj: Object to serialize
        default: Function to call for objects that can't be serialized
        indent: If True, indent output (equivalent to OPT_INDENT_2)
        sort_keys: If True, sort dictionary keys
        **kwargs: Additional options passed to orjson
        
    Returns:
        JSON string
    """
    opts = orjson.OPT_NON_STR_KEYS
    if indent:
        opts |= orjson.OPT_INDENT_2
    if sort_keys:
        opts |= orjson.OPT_SORT_KEYS
    
    # Convert kwargs to orjson options
    for kw in ['skipkeys', 'allow_nan', 'cls', 'separators']:
        kwargs.pop(kw, None)  # Ignore stdlib-only kwargs
    
    try:
        result = orjson.dumps(obj, option=opts, default=default)
        return result.decode('utf-8')
    except TypeError as e:
        # Re-raise with more helpful message
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable: {e}")


def dumps_bytes(obj: Any, **kwargs: Any) -> bytes:
    """Serialize obj to JSON bytes (direct orjson, no decode).
    
    Use this for maximum performance when you don't need string output.
    """
    opts = orjson.OPT_NON_STR_KEYS
    return orjson.dumps(obj, option=opts, **kwargs)


def loads(s: str | bytes | bytearray | memoryview) -> Any:
    """Deserialize s (a str, bytes or bytearray containing a JSON document) to a Python object.
    
    Args:
        s: JSON string or bytes
        
    Returns:
        Deserialized Python object
    """
    return orjson.loads(s)


def dump(obj: Any, fp: Any, **kwargs: Any) -> None:
    """Serialize obj as a JSON formatted stream to fp.
    
    Args:
        obj: Object to serialize
        fp: File-like object with write() method
        **kwargs: Additional arguments passed to dumps()
    """
    fp.write(dumps(obj, **kwargs))


def load(fp: Any) -> Any:
    """Deserialize fp (a file-like object containing a JSON document) to a Python object.
    
    Args:
        fp: File-like object with read() method
        
    Returns:
        Deserialized Python object
    """
    return loads(fp.read())


# Aliases for compatibility
dump = dump
load = load


class JSONDecodeError(ValueError):
    """Exception raised by json decoding errors."""
    
    def __init__(self, msg: str, doc: str | None = None, pos: int | None = None):
        super().__init__(msg)
        self.msg = msg
        self.doc = doc
        self.pos = pos


# Map orjson exceptions to stdlib-compatible errors
JSONDecodeError.__module__ = 'json'


def __getattr__(name: str) -> Any:
    """Provide compatibility for stdlib json module attributes."""
    if name == 'JSONDecoder':
        return None  # Not needed with orjson
    elif name == 'JSONEncoder':
        return None
    elif name == 'decoder':
        return None
    elif name == 'encoder':
        return None
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
