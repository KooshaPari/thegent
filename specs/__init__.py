"""
Specs module for extracting and generating specifications, WBS, and PRDs.
"""

from .cross_project_analyzer import CrossProjectAnalyzer
from .markdown_analyzer import MarkdownAnalyzer, ProjectSpecs
from .prd_generator import PRD, PRDGenerator

__all__ = [
    "PRD",
    "CrossProjectAnalyzer",
    "MarkdownAnalyzer",
    "PRDGenerator",
    "ProjectSpecs",
]
