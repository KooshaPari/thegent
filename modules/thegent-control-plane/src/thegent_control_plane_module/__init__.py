"""Control-plane module boundary for thegent."""


def get_control_plane_package():
    """Return the canonical control-plane package module."""
    import thegent_platform as platform_pkg

    return platform_pkg


__all__ = ["get_control_plane_package"]
