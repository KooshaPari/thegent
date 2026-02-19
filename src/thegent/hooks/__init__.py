"""Hook enhancements."""

from thegent.hooks.breaker import BreakerSubcommands
from thegent.hooks.changed_files_enhance import ChangedFilesEnhance
from thegent.hooks.config_enhance import ConfigEnhance
from thegent.hooks.debounce import DebounceSubcommand
from thegent.hooks.git_enhance import GitEnhance

__all__ = [
    "GitEnhance",
    "ChangedFilesEnhance",
    "ConfigEnhance",
    "BreakerSubcommands",
    "DebounceSubcommand",
]

from thegent.hooks.incremental import IncrementalSubcommands
from thegent.hooks.learning import LearningSubcommands
from thegent.hooks.fr_index import FRIndexSubcommands
from thegent.hooks.affected_tests import AffectedTestsSubcommand
from thegent.hooks.prewarm_report import PrewarmReportSubcommands

__all__.extend([
    "IncrementalSubcommands",
    "LearningSubcommands",
    "FRIndexSubcommands",
    "AffectedTestsSubcommand",
    "PrewarmReportSubcommands",
])
