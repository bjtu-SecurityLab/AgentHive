from agent.schema import Message
from typing import List, Optional, Callable

class HistoryStrategy:
    def apply(self, messages: List[Message]) -> List[Message]:
        return messages.copy()

class KeepLastN(HistoryStrategy):
    def __init__(self, n: int):
        if not isinstance(n, int) or n <= 0:
            raise ValueError("n must be a positive integer for KeepLastN")
        self.n = n

    def apply(self, messages: List[Message]) -> List[Message]:
        return messages[-self.n:]


class CompactToolHistory(HistoryStrategy):
    DEFAULT_KEEP_CHARS_COUNT = 1000
    DEFAULT_TOOL_TYPE = ["tool_result"]
    DEFAULT_SUMMARY_PREFIX = "Tool Result: "
    DEFAULT_SUMMARY_SUFFIX = "...result omitted"

    def __init__(self,
                 keep_chars_count: int = DEFAULT_KEEP_CHARS_COUNT,
                 tool_message_types: List[str] = None,
                 keep_last_n: Optional[int] = None):
        if not isinstance(keep_chars_count, int) or keep_chars_count < 0:
            raise ValueError("keep_chars_count must be a non-negative integer")
        self.keep_chars_count = keep_chars_count
        self.tool_message_types = tool_message_types or self.DEFAULT_TOOL_TYPE
        self.keep_last_n = keep_last_n

    def apply(self, messages: List[Message]) -> List[Message]:
        if self.keep_last_n is not None and self.keep_last_n > 0 and self.keep_last_n < len(messages):
            messages = messages[-self.keep_last_n:]
            
        result = []
        for msg in messages:
            msg_type = msg.get('type')
            if isinstance(msg_type, str) and msg_type in self.tool_message_types:
                content_str = msg.content
                is_truncated = len(content_str) > self.keep_chars_count
                kept_content = content_str[:self.keep_chars_count]
                summary = (
                    f"{self.DEFAULT_SUMMARY_PREFIX}"
                    f"{kept_content}"
                    f"{self.DEFAULT_SUMMARY_SUFFIX if is_truncated else ']'}"
                )
                result.append(Message(role=msg.role, content=summary, type=msg.type))
            else:
                result.append(msg)
        return result


class KeepLatestTool(HistoryStrategy):
    DEFAULT_KEEP_CHARS_COUNT = 1000
    DEFAULT_TOOL_TYPE = ["tool_result"]
    DEFAULT_SUMMARY_PREFIX = "Previous Tool Result: "
    DEFAULT_SUMMARY_SUFFIX = "..."

    def __init__(self,
                 keep_chars_count: int = DEFAULT_KEEP_CHARS_COUNT,
                 tool_message_type: str = DEFAULT_TOOL_TYPE,
                 keep_last_n: Optional[int] = None):
        if not isinstance(keep_chars_count, int) or keep_chars_count < 0:
            raise ValueError("keep_chars_count must be a non-negative integer")
        self.keep_chars_count = keep_chars_count
        self.tool_message_type = tool_message_type
        self.keep_last_n = keep_last_n

    def apply(self, messages: List[Message]) -> List[Message]:
        if self.keep_last_n is not None and self.keep_last_n > 0 and self.keep_last_n < len(messages):
            messages = messages[-self.keep_last_n:]
            
        result = []
        last_tool_msg_index = -1
        for i in range(len(messages) - 1, -1, -1):
            msg_type = messages[i].get('type')
            if isinstance(msg_type, str) and msg_type in self.tool_message_type:
                last_tool_msg_index = i
                break

        for i, msg in enumerate(messages):
            msg_type = msg.get('type')
            if isinstance(msg_type, str) and msg_type == self.tool_message_type and i != last_tool_msg_index:
                content_str = msg.content
                is_truncated = len(content_str) > self.keep_chars_count
                kept_content = content_str[:self.keep_chars_count]
                summary = (
                    f"{self.DEFAULT_SUMMARY_PREFIX}"
                    f"{kept_content}"
                    f"{self.DEFAULT_SUMMARY_SUFFIX if is_truncated else ']'}"
                )
                result.append(Message(role=msg.role, content=summary, type=msg.type))
            else:
                result.append(msg)
        return result
