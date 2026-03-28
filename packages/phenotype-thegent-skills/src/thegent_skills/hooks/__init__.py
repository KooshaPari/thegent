"""Hook enhancements."""

from thegent_skills.hooks.breaker import BreakerSubcommands
from thegent_skills.hooks.changed_files_enhance import ChangedFilesEnhance
from thegent_skills.hooks.config_enhance import ConfigEnhance
from thegent_skills.hooks.debounce import DebounceSubcommand
from thegent_skills.hooks.git_enhance import GitEnhance

__all__ = [
    "BreakerSubcommands",
    "ChangedFilesEnhance",
    "ConfigEnhance",
    "DebounceSubcommand",
    "GitEnhance",
]

from thegent_skills.hooks.affected_tests import AffectedTestsSubcommand
from thegent_skills.hooks.fr_index import FRIndexSubcommands
from thegent_skills.hooks.incremental import IncrementalSubcommands
from thegent_skills.hooks.learning import LearningSubcommands
from thegent_skills.hooks.prewarm_report import PrewarmReportSubcommands

__all__.extend(
    [
        "AffectedTestsSubcommand",
        "FRIndexSubcommands",
        "IncrementalSubcommands",
        "LearningSubcommands",
        "PrewarmReportSubcommands",
    ]
)
