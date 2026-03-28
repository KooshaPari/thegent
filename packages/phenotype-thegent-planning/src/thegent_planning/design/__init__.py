"""Design language and naming conventions."""

# Import modules as they are implemented
try:
    from thegent_planning.design.design_language import DesignLanguage
except ImportError:
    DesignLanguage = None

try:
    from thegent_planning.design.naming import NamingConvention
except ImportError:
    NamingConvention = None

__all__ = [
    "DesignLanguage",
    "NamingConvention",
]
