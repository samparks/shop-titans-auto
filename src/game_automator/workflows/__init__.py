"""Workflow definitions and discovery."""

import importlib
import pkgutil
from typing import Dict, Type

from game_automator.workflows.base import BaseWorkflow


def discover_workflows() -> Dict[str, Type[BaseWorkflow]]:
    """
    Discover all workflow classes in this package.
    Returns dict mapping workflow name to class.
    """
    workflows = {}
    
    # Import all modules in this package
    package_path = __path__
    for _, module_name, _ in pkgutil.iter_modules(package_path):
        if module_name == "base":
            continue
        
        module = importlib.import_module(f".{module_name}", __package__)
        
        # Find BaseWorkflow subclasses
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type) 
                and issubclass(attr, BaseWorkflow) 
                and attr is not BaseWorkflow
            ):
                workflows[attr.name] = attr
    
    return workflows