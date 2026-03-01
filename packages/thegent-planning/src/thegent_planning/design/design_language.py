"""Design language system with platform-specific tokens."""

from dataclasses import dataclass
from typing import Any

from rich.theme import Theme

from thegent.thg_platform import Platform, detect_platform

__all__ = ["DesignLanguage", "DesignToken"]


@dataclass
class DesignToken:
    """Design token definition."""

    name: str
    value: Any
    category: str
    platform: str | None = None


class DesignLanguage:
    """Design language system.

    This class manages design tokens (colors, typography, spacing) and
    applies them consistently across all components, with platform-specific
    overrides where appropriate.

    Examples:
        >>> design = DesignLanguage()
        >>> primary_color = design.get_token("color.primary")
        >>> system_font = design.get_token("font.system", platform="macos")
    """

    def __init__(self) -> None:
        """Initialize design language system."""
        self.tokens: dict[str, DesignToken] = {}
        self._register_tokens()

    def _register_tokens(self) -> None:
        """Register design tokens."""
        # Colors
        self.tokens["color.primary"] = DesignToken(name="color.primary", value="#4CAF50", category="color")
        self.tokens["color.error"] = DesignToken(name="color.error", value="#F44336", category="color")
        self.tokens["color.warning"] = DesignToken(name="color.warning", value="#FF9800", category="color")
        self.tokens["color.success"] = DesignToken(name="color.success", value="#4CAF50", category="color")
        self.tokens["color.info"] = DesignToken(name="color.info", value="#2196F3", category="color")

        # Spacing
        self.tokens["spacing.unit"] = DesignToken(name="spacing.unit", value=4, category="spacing")
        self.tokens["spacing.small"] = DesignToken(name="spacing.small", value=8, category="spacing")
        self.tokens["spacing.medium"] = DesignToken(name="spacing.medium", value=16, category="spacing")
        self.tokens["spacing.large"] = DesignToken(name="spacing.large", value=24, category="spacing")

        # Typography
        self.tokens["font.mono"] = DesignToken(
            name="font.mono", value="'Courier New', monospace", category="typography"
        )

        # Platform-specific tokens
        plat = detect_platform()
        if plat == Platform.MACOS:
            self.tokens["font.system"] = DesignToken(
                name="font.system", value="SF Pro", category="typography", platform="macos"
            )
        elif plat == Platform.WINDOWS:
            self.tokens["font.system"] = DesignToken(
                name="font.system", value="Segoe UI", category="typography", platform="windows"
            )
        else:  # Linux
            self.tokens["font.system"] = DesignToken(
                name="font.system", value="Ubuntu", category="typography", platform="linux"
            )

    def get_token(self, name: str, platform: str | None = None) -> Any | None:
        """Get design token value.

        Args:
            name: Token name (e.g., "color.primary")
            platform: Platform override, or None to use detected platform

        Returns:
            Token value, or None if not found
        """
        token = self.tokens.get(name)
        if not token:
            return None

        # Platform-specific override
        if platform:
            platform_token_name = f"{name}.{platform}"
            platform_token = self.tokens.get(platform_token_name)
            if platform_token:
                return platform_token.value

        return token.value

    def apply_to_cli(self) -> None:
        """Apply design language to CLI.

        Configures a Rich Theme map from design tokens and stores it in
        ``self.cli_theme`` for CLI surfaces to consume.
        """
        plat = detect_platform()
        platform_name = {
            Platform.MACOS: "macos",
            Platform.WINDOWS: "windows",
            Platform.LINUX: "linux",
        }.get(plat, "linux")

        primary = self._required_token("color.primary")
        error = self._required_token("color.error")
        warning = self._required_token("color.warning")
        success = self._required_token("color.success")
        info = self._required_token("color.info")
        mono = self._required_token("font.mono")
        system_font = self.get_token("font.system", platform=platform_name)
        if system_font is None:
            raise KeyError(f"Missing required token: font.system ({platform_name})")

        styles = {
            "primary": f"bold {primary}",
            "error": f"bold {error}",
            "warning": f"bold {warning}",
            "success": f"bold {success}",
            "info": info,
            "code": "bold cyan",
            "body": "white",
        }
        self.cli_theme = Theme(styles)
        self.cli_typography = {"mono": mono, "system": system_font}

    def _required_token(self, name: str) -> Any:
        value = self.get_token(name)
        if value is None:
            raise KeyError(f"Missing required token: {name}")
        return value
