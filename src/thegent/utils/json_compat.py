"""JSON compatibility layer.

Provides orjson with json-compatible API.
Use this instead of json for 3-5x performance improvement.
"""

try:
    import orjson

    def dumps(obj, **kwargs):
        """Serialize obj to JSON string.

        Args:
            obj: Object to serialize
            **kwargs: Additional options (indent, sort_keys supported)

        Returns:
            str: JSON string
        """
        opts = 0
        if kwargs.get("sort_keys"):
            opts |= orjson.OPT_SORT_KEYS
        if kwargs.get("indent"):
            opts |= orjson.OPT_INDENT_2

        result = orjson.dumps(obj, option=opts)
        return result.decode("utf-8")

    def loads(s):
        """Deserialize JSON string to object.

        Args:
            s: JSON string or bytes

        Returns:
            Deserialized object
        """
        if isinstance(s, str):
            s = s.encode("utf-8")
        return orjson.loads(s)

    def dump(obj, fp, **kwargs):
        """Serialize obj to file.

        Args:
            obj: Object to serialize
            fp: File-like object with write()
            **kwargs: Additional options
        """
        fp.write(dumps(obj, **kwargs))

    def load(fp):
        """Deserialize file to object.

        Args:
            fp: File-like object with read()

        Returns:
            Deserialized object
        """
        return loads(fp.read())

    JSON = type("JSONModule", (), {
        "dumps": staticmethod(dumps),
        "loads": staticmethod(loads),
        "dump": staticmethod(dump),
        "load": staticmethod(load),
    })()

except ImportError:
    import json
    JSON = json
    dumps = json.dumps
    loads = json.loads
    dump = json.dump
    load = json.load


__all__ = ["JSON", "dump", "dumps", "load", "loads"]
