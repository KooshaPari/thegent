import os
import platform

from thegent.platform import detect_platform, Platform

def test_detect_platform():
    p = detect_platform()
    assert isinstance(p, Platform)
    if platform.system().lower() == "darwin":
        assert p == Platform.MACOS
