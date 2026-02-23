"""Fast JSON utilities using orjson with fallback to standard json.

This module provides fast JSON serialization/deserialization using orjson when available,
falling back to the standard json module. orjson is 3-5x faster than json.

Usage:
    from thegent.utils.json_utils import json_dumps, json_loads
    
    # Fast serialization
    data = {"key": "value"}
    result = json_dumps(data)
    
    # Fast deserialization  
    parsed = json_loads(result)
"""

from __future__ import annotations

from typing import Any

# Try to use orjson for better performance
try:
    import orjson

    _HAS_ORJSON = True
except ImportError:
    import json

    _HAS_ORJSON = False


def json_dumps(obj: Any, **kwargs: Any) -> str:
    """Serialize obj to a JSON formatted string.
    
    Uses orjson if available (3-5x faster), falls back to json.
    
    Args:
        obj: Object to serialize
        **kwargs: Additional arguments (passed to json.dumps if using fallback)
        
    Returns:
        JSON string
    """
    if _HAS_ORJSON:
        # orjson.dumps returns bytes, decode to str
        return orjson.dumps(obj).decode("utf-8")
    return json.dumps(obj, **kwargs)


def json_loads(s: str | bytes, **kwargs: Any) -> Any:
    """Deserialize s (a string containing a JSON document) to a Python object.
    
    Uses orjson if available (3-5x faster), falls back to json.
    
    Args:
        s: JSON string or bytes
        **kwargs: Additional arguments (passed to json.loads if using fallback)
        
    Returns:
        Deserialized Python object
    """
    if _HAS_ORJSON:
        return orjson.loads(s)
    return json.loads(s, **kwargs)


def json_dump(obj: Any, fp: Any, **kwargs: Any) -> None:
    """Serialize obj as a JSON formatted stream to fp.
    
    Uses orjson if available (3-5x faster), falls back to json.
    
    Args:
        obj: Object to serialize
        fp: File-like object with write() method
        **kwargs: Additional arguments
    """
    if _HAS_ORJSON:
        fp.write(orjson.dumps(obj).decode("utf-8"))
    else:
        json.dump(obj, fp, **kwargs)


def json_load(fp: Any, **kwargs: Any) -> Any:
    """Deserialize fp to a Python object.
    
    Uses orjson if available (3-5x faster), falls back to json.
    
    Args:
        fp: File-like object with read() method
        **kwargs: Additional arguments
        
    Returns:
        Deserialized Python object
    """
    if _HAS_ORJSON:
        return orjson.loads(fp.read())
    return json.load(fp, **kwargs)


# For compatibility - re-export standard json when needed
if not _HAS_ORJSON:
    json = json  # noqa: F811
else:
    # Create a compatibility module
    class _JsonCompat:
        """Compatibility layer for code that expects json module."""

        @staticmethod
        def loads(s: str | bytes, **kwargs: Any) -> Any:
            return json_loads(s, **kwargs)

        @staticmethod
        def dumps(obj: Any, **kwargs: Any) -> str:
            return json_dumps(obj, **kwargs)

        @staticmethod
        def load(fp: Any, **kwargs: Any) -> Any:
            return json_load(fp, **kwargs)

        @staticmethod
        def dump(obj: Any, fp: Any, **kwargs: Any) -> None:
            return json_dump(obj, fp, **kwargs)

    json = _JsonCompat()  # type: ignore[assignment]
