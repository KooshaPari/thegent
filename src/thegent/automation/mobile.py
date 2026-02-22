"""Mobile automation module for Android/iOS with simulator support."""

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class MobilePlatform(Enum):
    ANDROID = "android"
    IOS = "ios"


class DeviceType(Enum):
    SIMULATOR = "simulator"
    EMULATOR = "emulator"
    REAL_DEVICE = "real_device"


@dataclass
class DeviceConfig:
    platform: MobilePlatform
    device_type: DeviceType
    device_id: str | None = None
    device_name: str | None = None
    os_version: str | None = None
    app_path: Path | None = None
    app_package: str | None = None
    auto_grant_permissions: bool = True
    auth_profile: str | None = None


@dataclass
class AuthProfile:
    name: str
    cookies: dict = field(default_factory=dict)
    account_credentials: dict = field(default_factory=dict)


class MobileAutomationManager:
    def __init__(self):
        self._auth_profiles: dict[str, AuthProfile] = {}
        logger.info("MobileAutomationManager initialized")

    def save_auth_profile(self, name: str, profile: AuthProfile) -> None:
        self._auth_profiles[name] = profile

    def get_auth_profile(self, name: str) -> AuthProfile | None:
        return self._auth_profiles.get(name)


_mobile_manager: MobileAutomationManager | None = None


def get_mobile_manager() -> MobileAutomationManager:
    global _mobile_manager
    if _mobile_manager is None:
        _mobile_manager = MobileAutomationManager()
    return _mobile_manager
