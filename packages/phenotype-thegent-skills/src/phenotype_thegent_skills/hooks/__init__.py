"""Hook enhancements."""

from phenotype_thegent_skills.hooks.breaker import BreakerSubcommands
from phenotype_thegent_skills.hooks.changed_files_enhance import ChangedFilesEnhance
from phenotype_thegent_skills.hooks.config_enhance import ConfigEnhance
from phenotype_thegent_skills.hooks.debounce import DebounceSubcommand
from phenotype_thegent_skills.hooks.git_enhance import GitEnhance

__all__ = [
    "BreakerSubcommands",
    "ChangedFilesEnhance",
    "ConfigEnhance",
    "DebounceSubcommand",
    "GitEnhance",
]

from phenotype_thegent_skills.hooks.affected_tests import AffectedTestsSubcommand
from phenotype_thegent_skills.hooks.fr_index import FRIndexSubcommands
from phenotype_thegent_skills.hooks.incremental import IncrementalSubcommands
from phenotype_thegent_skills.hooks.learning import LearningSubcommands
from phenotype_thegent_skills.hooks.prewarm_report import PrewarmReportSubcommands

__all__.extend(
    [
        "AffectedTestsSubcommand",
        "FRIndexSubcommands",
        "IncrementalSubcommands",
        "LearningSubcommands",
        "PrewarmReportSubcommands",
    ]
)
