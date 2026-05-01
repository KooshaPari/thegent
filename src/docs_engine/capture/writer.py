"""Writer - STUB."""


class Writer:
    def __init__(self, *args, **kwargs):
        pass

    def write(self, content, *args, **kwargs):
        pass


__all__ = ["Writer", "DocWriter"]


class DocWriter(Writer):
    """Document writer extending base Writer."""

    def write(self, content, *args, **kwargs):
        pass
