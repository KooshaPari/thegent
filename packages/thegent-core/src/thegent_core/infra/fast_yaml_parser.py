"""Compatibility bridge for legacy thegent_core YAML parser imports."""

from thegent.infra.fast_yaml_parser import yaml_dump, yaml_load

__all__ = ["yaml_dump", "yaml_load"]
