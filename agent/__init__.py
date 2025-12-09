"""
AgentHive: A Delegation-Centric Multi-Agent System Framework

AgentHive treats delegation as a first-class primitive, enabling any agent to
spawn and coordinate sub-agents dynamically without a central orchestrator.
"""

__version__ = "0.1.0"
__author__ = "BJTU Security Lab"
__license__ = "MIT"

from .base import BaseLLM, BaseAgent
from .schema import Message
from .llmclient import LLMClient
from .historystrategy import HistoryStrategy
from .tool_base.tool import Tool
from .tool_base.executable_tool import ExecutableTool
from .tool_base.flexible_context import FlexibleContext

__all__ = [
    "BaseLLM",
    "BaseAgent",
    "Message",
    "LLMClient",
    "HistoryStrategy",
    "Tool",
    "ExecutableTool",
    "FlexibleContext",
]
