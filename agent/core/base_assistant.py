import json
import traceback
from typing import Optional, List, Type, Union, Any, Dict

from agent.base import BaseAgent
from agent.core.builder import AgentConfig, build_agent
from agent.tool_base.flexible_context import FlexibleContext
from agent.tool_base.executable_tool import ExecutableTool


class BaseAssistant(ExecutableTool):
    name = "TaskDelegator"
    description = """
    Task Delegator - Used to delegate a sub-task to a sub-agent for processing.
    
    Applicable Scenarios:
    When the next analysis task can only be determined after obtaining the analysis results of a single task.

    """
    parameters = {
        "type": "object",
        "properties": {
            "task": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Specific description of the sub-task to be executed, noting the analysis object."
                    }
                },
                "required": ["task"],
                "description": "Task item containing a single task description."
            }
        },
        "required": ["task"]
    }

    timeout = 9600

    def __init__(
        self,
        context: FlexibleContext,
        agent_class_to_create: Type[BaseAgent] = BaseAgent,
        default_sub_agent_tool_classes: Optional[List[Union[Type[ExecutableTool], ExecutableTool]]] = None,
        default_sub_agent_max_iterations: int = 10,
        sub_agent_system_prompt: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        super().__init__(context)
        self.agent_class_to_create = agent_class_to_create
        self.default_sub_agent_tool_classes = default_sub_agent_tool_classes if default_sub_agent_tool_classes is not None else []
        self.default_sub_agent_max_iterations = default_sub_agent_max_iterations
        self.sub_agent_system_prompt = sub_agent_system_prompt

        if name is not None:
            self.name = name
        if description is not None:
            self.description = description

        if timeout is not None:
            self.timeout = timeout

    def _get_sub_agent_task_details(self, **kwargs: Any) -> Dict[str, Any]:
        task = kwargs.get("task", "")
        if not isinstance(task, str):
            return {"task": ""}
        return {"task": task}

    def _prepare_sub_agent_context(self, sub_agent_context: FlexibleContext, **task_details: Any) -> FlexibleContext:
        return sub_agent_context

    def _build_sub_agent_prompt(self, usr_init_msg: Optional[str], **task_details: Any) -> str:
        task = task_details.get("task")

        usr_init_msg_content = usr_init_msg if usr_init_msg else "No user initial request provided"
        task_content = task if task else "No task provided"

        return (
            f"User initial request:\n{usr_init_msg_content}\n"
            f"Current specific task:\n{task_content}"
        )

    def execute(self, **kwargs: Any) -> str:
        run_in_background = kwargs.get("run_in_background", False)
        if run_in_background:
            self.is_background_task = True
        
        usr_init_msg = self.context.get("user_input")
        task_for_error_log: Optional[str] = "Unknown task"

        try:
            task_details = self._get_sub_agent_task_details(**kwargs)
            task = task_details.get("task")
            task_for_error_log = str(task) if task else "Not extracted"

            if not task:
                return "Error: Failed to extract 'task' for sub-agent from task input."

            full_task_prompt = self._build_sub_agent_prompt(usr_init_msg, **task_details)

            sub_agent_base_context = self.context.copy()
            try:
                sub_agent_prepared_context = self._prepare_sub_agent_context(sub_agent_base_context, **task_details)
            except Exception as e:
                return f"Error: {str(e)}"

            sub_agent_instance_name = f"{self.name}_sub_agent"

            sub_agent_config = AgentConfig(
                agent_class=self.agent_class_to_create,
                tool_configs=self.default_sub_agent_tool_classes,
                system_prompt=self.sub_agent_system_prompt,
                max_iterations=self.default_sub_agent_max_iterations,
                agent_instance_name=sub_agent_instance_name,
            )

            sub_agent = build_agent(
                agent_config=sub_agent_config,
                context=sub_agent_prepared_context,
            )

            result_from_sub_agent = sub_agent.run(full_task_prompt)
            return result_from_sub_agent

        except Exception as e:
            error_snippet = task_for_error_log[:70]
            error_message_for_return = f"Error: {self.name} failed to execute subtask (task snippet: '{error_snippet}'): {type(e).__name__} - {str(e)}"

            log_error_message = f"Error in {self.name} during sub-task preparation or delegation (task snippet: '{error_snippet}...'): {type(e).__name__} - {str(e)}"
            logger = getattr(self, 'logger', None)
            if logger:
                logger.error(log_error_message, exc_info=True)
            else:
                print(f"ERROR in {self.name}: {log_error_message}")
                print(traceback.format_exc())
            return f"An error occurred while executing the subtask: {error_message_for_return}"
