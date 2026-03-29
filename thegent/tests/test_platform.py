import platform

from thegent.thegent_platform import Platform, detect_platform


def test_detect_platform():
    p = detect_platform()
    assert isinstance(p, Platform)
    if platform.system().lower() == "darwin":
        assert p == Platform.MACOS
