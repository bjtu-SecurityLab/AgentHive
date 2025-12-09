"""
Compatibility shim: re-export BaseAssistant and ParallelBaseAssistant
from their new modules to preserve `from agent.core.assitants import ...` imports.
"""

from .base_assistant import BaseAssistant
from .parallel_assistant import ParallelBaseAssistant

__all__ = ["BaseAssistant", "ParallelBaseAssistant"]

