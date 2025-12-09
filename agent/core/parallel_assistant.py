import json
import threading
from typing import Optional, List, Type, Union, Any, Dict

from agent.base import BaseAgent
from agent.core.builder import AgentConfig, build_agent
from agent.tool_base.flexible_context import FlexibleContext
from agent.tool_base.executable_tool import ExecutableTool


class ParallelBaseAssistant(ExecutableTool):
    name = "ParallelTaskDelegator"
    description = """
    Task Delegator - Used to distribute multiple sub-tasks to parallel sub-agents for processing.
    
    Applicable Scenarios:
    1. Need to decompose a complex task into multiple independent sub-tasks for processing.
    2. There is no strict execution order dependency between sub-tasks.
    3. Recommended for large-scale and complex tasks, allowing parallel execution of multiple sub-tasks to improve analysis efficiency.
    
    """
    parameters = {
        "type": "object",
        "properties": {
            "tasks": { # General 'tasks' parameter, a list of task objects
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "Specific description of the sub-task to be executed. Note that each sub-task description is independent and needs to specify the analysis object."
                        }
                    },
                    "required": ["task"],
                    "description": "Task item containing a single task description."
                },
                "description": "List of independent sub-tasks to be distributed to sub-agents for execution."
            }
        },
        "required": ["tasks"]
    }
    timeout = 9600

    def __init__(
        self,
        context: FlexibleContext,
        agent_class_to_create: Type[BaseAgent] = BaseAgent,
        default_sub_agent_tool_classes: Optional[List[Union[Type[ExecutableTool], ExecutableTool]]] = None,
        default_sub_agent_max_iterations: int = 25,
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

    def _extract_task_list(self, **kwargs: Any) -> List[Dict[str, Any]]:
        return kwargs.get("tasks", [])

    def _prepare_sub_agent_context(self, **kwargs: Any) -> FlexibleContext:
        sub_agent_context = self.context.copy()
        return sub_agent_context

    def _build_sub_agent_prompt(self, **kwargs: Any) -> str:
        task = kwargs.get("task")

        usr_init_msg_content = self.context.get("user_input") if self.context.get("user_input") else "未提供用户初始请求"
        task_content = task if task else "未提供任务描述"

        return (
            f"用户初始请求是:\n{usr_init_msg_content}\n\n"
            f"当前具体任务:\n{task_content}"
        )

    def _execute_single_task_in_thread(self, task_item: Dict[str, Any], task_index: int, results_list: list):
        task_for_error_log: Optional[str] = f"任务 #{task_index + 1}"

        try:
            task_details_with_index = task_item.copy()
            task_details_with_index['task_index'] = task_index

            full_task_prompt = self._build_sub_agent_prompt(
                **task_details_with_index
            )

            try:
                sub_agent_prepared_context = self._prepare_sub_agent_context(
                    **task_details_with_index
                )
            except Exception as e:
                results_list[task_index] = f"错误: {str(e)}"
                return

            sub_agent_instance_name = f"{self.name}_task{task_index+1}"

            sub_agent_config = AgentConfig(
                agent_class=self.agent_class_to_create,
                tool_configs=self.default_sub_agent_tool_classes,
                max_iterations=self.default_sub_agent_max_iterations,
                system_prompt=self.sub_agent_system_prompt,
                agent_instance_name=sub_agent_instance_name
            )

            sub_agent = build_agent(
                agent_config=sub_agent_config,
                context=sub_agent_prepared_context
            )

            result = sub_agent.run(full_task_prompt)
            results_list[task_index] = result

        except Exception as e:
            error_desc_snippet = str(task_for_error_log)[:50]
            error_string_for_result = f"错误: {self.name} 的并行子任务 #{task_index + 1} 执行失败 ({type(e).__name__}): {str(e)}"
            results_list[task_index] = error_string_for_result

            log_error_message = f"Error in {self.name} during parallel sub-task #{task_index + 1} (desc snippet: '{error_desc_snippet}...'): {type(e).__name__} - {str(e)}"
            logger = getattr(self, 'logger', None)
            if logger:
                logger.error(log_error_message, exc_info=True)
            else:
                print(f"ERROR in {self.name} (task #{task_index+1}): {log_error_message}")

    def execute(self, **kwargs: Any) -> str:
        tasks = self._extract_task_list(**kwargs)
        
        if not tasks:
            return json.dumps([], ensure_ascii=False)

        threads = []
        results_list = [None] * len(tasks)

        for i, task_item in enumerate(tasks):
            thread = threading.Thread(
                target=self._execute_single_task_in_thread,
                args=(task_item, i, results_list),
                name=f"SubAgent-{self.name}-{i+1}"
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
            
        final_results_for_json = []
        for i, task_item in enumerate(tasks):
            task_result_or_error = results_list[i]

            task_entry = {
                "task_item": task_item,
                "task_index": i + 1
            }

            if task_result_or_error is None:
                task_entry["error_details"] = "未能获取任务结果 (线程可能未正确返回值)"
            elif isinstance(task_result_or_error, str) and task_result_or_error.startswith("错误:"):
                task_entry["error_message"] = task_result_or_error
            else:
                task_entry["result"] = task_result_or_error
            
            final_results_for_json.append(task_entry)
        
        return json.dumps(final_results_for_json, ensure_ascii=False, indent=2)
