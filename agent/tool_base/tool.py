import json
from typing import Dict, Any, Callable, Optional

class Tool:
    def __init__(self, name: str, description: str, function: Callable, parameters: Optional[Dict[str, Any]] = None, timeout: Optional[int] = None):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters if parameters else {}
        self.timeout = timeout

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def format_for_prompt(self) -> str:
        param_str = json.dumps(self.parameters, ensure_ascii=False) if self.parameters else "No parameters"
        if self.parameters:
            try:
                param_str = json.dumps(self.parameters, indent=2, ensure_ascii=False)
            except TypeError:
                 param_str = str(self.parameters)
        return f"- Name: {self.name}\n  Description: {self.description}\n  Parameters (JSON Schema format):\n{param_str}"
