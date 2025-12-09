# AgentHive

<div align="center">

**A Delegation-Centric Multi-Agent System Framework for LLM-based Autonomous Systems**

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

[English](#) | [中文](#)

</div>

---

## 📖 Overview

Large-language-model (LLM) agents excel at reasoning and tool use, yet existing multi-agent systems (MAS) rely on static, hand-crafted topologies that fail on open-ended, evolving tasks. **AgentHive** introduces a delegation-centric MAS framework that treats delegation as a first-class primitive: any agent may spawn and coordinate sub-agents, enabling decentralized control without a central orchestrator.

Through **recursive delegation**, AgentHive dynamically forms task-adaptive structures—trees, forests, and star topologies—without predefined agent graphs. The framework has been evaluated across four real-world domains, demonstrating that MAS emerge automatically from task demands.

<div align="center">
  <img src="asserts/compare.png" alt="AgentHive vs Traditional MAS" width="800"/>
  <p><i>Comparison: AgentHive's dynamic delegation vs traditional static topologies</i></p>
</div>

### ✨ Key Features

- 🎯 **First-Class Delegation**: Any agent can spawn and coordinate sub-agents dynamically
- 🌳 **Dynamic Topology**: Automatically forms task-adaptive structures (trees, forests, star patterns)
- 🔄 **Recursive Coordination**: Enables deep task decomposition and parallel execution
- 🚀 **Decentralized Control**: No central orchestrator required
- 🎨 **Expressive & Adaptive**: Agents explore more deeply and cover a wider solution space
- 🛠️ **Flexible Tool System**: Easy integration of custom tools and capabilities

---

## 🏗️ Architecture

AgentHive consists of several core components:

<div align="center">
  <img src="asserts/arch.png" alt="AgentHive Architecture" width="800"/>
  <p><i>AgentHive system architecture showing delegation-based agent spawning</i></p>
</div>

### Core Components

```
agent/
├── base.py                 # Base LLM and Agent implementations
├── schema.py              # Message and data schemas
├── llmclient.py           # LLM client interface
├── historystrategy.py     # Conversation history management
├── core/
│   ├── base_assistant.py      # Base delegation assistant
│   ├── parallel_assistant.py  # Parallel task delegation
│   ├── builder.py             # Agent and assistant builders
│   └── assitants.py           # Assistant implementations
└── tool_base/
    ├── tool.py                # Base tool interface
    ├── executable_tool.py     # Executable tool abstraction
    └── flexible_context.py    # Shared context management
```

### Key Abstractions

- **BaseAgent**: Core agent with LLM reasoning and tool execution
- **BaseAssistant**: Task delegation primitive for spawning sub-agents
- **ParallelBaseAssistant**: Parallel task execution across multiple sub-agents
- **FlexibleContext**: Shared context for inter-agent communication
- **ExecutableTool**: Standard interface for agent capabilities

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- OpenAI API key or compatible LLM endpoint

### Installation

```bash
# Clone the repository
git clone https://github.com/bjtu-SecurityLab/AgentHive.git
cd AgentHive

# Install dependencies
pip install -r requirements.txt  # if available
# or install core dependencies:
pip install openai asyncio
```

### Quick Start

```python
from agent.base import BaseAgent
from agent.core.builder import AgentConfig, AssistantToolConfig, build_agent
from agent.core.base_assistant import BaseAssistant
from agent.tool_base.flexible_context import FlexibleContext

# Create a shared context
context = FlexibleContext()
context.set("user_input", "Your task description here")

# Configure an agent with delegation capability
agent_config = AgentConfig(
    agent_class=BaseAgent,
    tool_configs=[
        AssistantToolConfig(
            assistant_class=BaseAssistant,
            sub_agent_config=AgentConfig(
                agent_class=BaseAgent,
                max_iterations=10
            )
        )
    ],
    system_prompt="You are a helpful AI assistant that can delegate tasks.",
    max_iterations=25
)

# Build and run the agent
agent = build_agent(agent_config, context)
result = agent.run("Solve this complex task")
print(result)
```

---

## 💡 How It Works

### Delegation as a First-Class Primitive

Unlike traditional MAS frameworks with fixed topologies, AgentHive allows any agent to:

1. **Spawn Sub-Agents**: Create specialized agents for specific subtasks
2. **Coordinate Execution**: Manage sequential or parallel task execution
3. **Share Context**: Pass information between parent and child agents
4. **Aggregate Results**: Combine outputs from multiple sub-agents

### Dynamic Structure Formation

```
Task → Agent₁
        ├─→ Agent₂ (subtask A)
        │    ├─→ Agent₄ (sub-subtask A1)
        │    └─→ Agent₅ (sub-subtask A2)
        └─→ Agent₃ (subtask B)
             └─→ Agent₆ (sub-subtask B1)
```

This tree structure emerges naturally from task requirements without pre-configuration.

---

## 📊 Evaluation & Results

AgentHive has been evaluated across **four real-world domains**, showing that:

- ✅ Multi-agent structures emerge automatically from task demands
- ✅ Performance gains from expressive, adaptive MAS
- ✅ Agents explore more deeply and cover wider solution spaces
- ✅ Successful handling of open-ended, evolving tasks

*(Detailed benchmarks and domain-specific results available in the paper)*

---

## 🛠️ Advanced Usage

### Creating Custom Tools

```python
from agent.tool_base.executable_tool import ExecutableTool
from agent.tool_base.flexible_context import FlexibleContext

class MyCustomTool(ExecutableTool):
    name = "MyTool"
    description = "Description of what this tool does"
    parameters = {
        "type": "object",
        "properties": {
            "input": {"type": "string", "description": "Input parameter"}
        },
        "required": ["input"]
    }
    
    def execute(self, **kwargs):
        input_val = kwargs.get("input")
        # Your tool logic here
        return f"Processed: {input_val}"
```

### Parallel Task Execution

```python
from agent.core.parallel_assistant import ParallelBaseAssistant

# Configure parallel delegation
parallel_config = AssistantToolConfig(
    assistant_class=ParallelBaseAssistant,
    sub_agent_config=AgentConfig(
        agent_class=BaseAgent,
        max_iterations=10
    ),
    description="Execute multiple subtasks in parallel"
)
```

---

## 📚 Documentation

- **Core Concepts**: Understanding delegation and dynamic topology
- **API Reference**: Detailed class and method documentation
- **Examples**: Sample use cases and implementations
- **Best Practices**: Guidelines for effective agent design

*(Documentation coming soon)*

---

## 🤝 Contributing

We welcome contributions! Please feel free to:

- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📧 Contact

For questions, suggestions, or collaborations:

- **GitHub**: [bjtu-SecurityLab/AgentHive](https://github.com/bjtu-SecurityLab/AgentHive)
- **Issues**: [GitHub Issues](https://github.com/bjtu-SecurityLab/AgentHive/issues)

---

## 📖 Citation

If you use AgentHive in your research, please cite:


---

<div align="center">

**Built with ❤️ by BJTU Security Lab**

⭐ Star us on GitHub if you find this project useful!

</div>