# Strands Agent Runtime - Code Explanation

**Abstract**: This script creates an AI agent powered by AWS Bedrock's Claude model that can perform calculations, check weather, and convert currencies. It accepts JSON input via command line and returns intelligent responses by automatically selecting and using the appropriate tools.[^3]

## Script Breakdown

### Imports

```python
from strands import Agent, tool
from strands_tools import calculator
import argparse
import json
from strands.models import BedrockModel
```

**What each does**:[^2]

- `Agent` - The AI agent that orchestrates everything
- `tool` - Decorator that registers functions as agent tools
- `calculator` - Pre-built tool for math operations
- `argparse` - Handles command line arguments
- `BedrockModel` - Connects to AWS Bedrock's Claude models

### Custom Tools

```python
@tool
def weather():
    """Get weather"""
    return "sunny"
```

**Syntax breakdown**:[^9]

- `@tool` decorator tells Strands "this function is a tool the agent can use"
- Docstring (`"""Get weather"""`) is **critical** - the AI reads this to decide when to call the tool
- Return value can be string, dict, number, or list

```python
@tool
def convert_currency(amount: float, from_currency: str, to_currency: str):
    """Convert between USD, SGD, EUR, and JPY using exchange rates"""
    # Implementation...
```

**Parameters with type hints**:[^9]

- `amount: float` - The agent knows this needs a number
- `from_currency: str` - String parameter
- Type hints help the agent pass correct data types

### Model Configuration

```python
model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
model = BedrockModel(model_id=model_id)
```

**What happens**: Creates connection to Claude on AWS Bedrock. The model is the "brain" that decides which tools to use.[^3]

### Agent Setup

```python
agent = Agent(
    model=model,
    tools=[calculator, weather, convert_currency],
    system_prompt="You're a helpful assistant..."
)
```

**Key concepts**:[^2]

- `model` - Which AI model powers the agent
- `tools` - List of all functions the agent can call (mix of pre-built and custom)
- `system_prompt` - Instructions that shape the agent's personality and capabilities

### Main Function

```python
def strands_agent_bedrock(payload):
    user_input = payload.get("prompt")
    response = agent(user_input)
    return response.message['content'][^0]['text']
```

**Flow**:[^3]

1. Extract user's question from payload
2. Call agent with `agent(user_input)` - this triggers the agent loop
3. Agent decides what tools to use, calls them, and generates response
4. Navigate response structure to get final text

### Command Line Interface

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", type=str)
    args = parser.parse_args()
  
    response = strands_agent_bedrock(json.loads(args.payload))
    print(response)
```

**What this does**:[^11]

- `if __name__ == "__main__"` - Only runs when script is executed directly
- `parser.add_argument("payload", type=str)` - Expects one string argument
- `json.loads(args.payload)` - Converts JSON string to Python dict
- `print(response)` - Outputs agent's answer

## How to Run

```bash
python strands_claude.py '{"prompt": "Convert 100 USD to SGD"}'
python strands_claude.py '{"prompt": "What is 50 * 3.14?"}'
python strands_claude.py '{"prompt": "What is the weather?"}'
```

## Agent Loop Concept

When you call the agent:[^3]

1. Agent receives: "Convert 100 USD to SGD"
2. Agent thinks: "I need the convert_currency tool"
3. Agent calls: `convert_currency(100, "USD", "SGD")`
4. Agent receives result: "100 USD = 135.00 SGD"
5. Agent responds to user with natural language

**Key insight**: You don't manually call tools - the agent intelligently selects them based on your system prompt and tool docstrings.[^3]

## Customization Quick Reference

**Add new tool**: Write function, add `@tool` decorator, add descriptive docstring, include in `tools=[]` list.[^9]

**Change model**: Modify `model_id` to different Bedrock model.[^2]

**Adjust behavior**: Edit `system_prompt` to change personality or capabilities.[^2]
`<span style="display:none">`[^8]

<div align="center">⁂</div>

[^1]: https://github.com/strands-agents/docs
    
[^2]: https://github.com/strands-agents/sdk-python
    
[^3]: https://aws.amazon.com/blogs/opensource/introducing-strands-agents-an-open-source-ai-agents-sdk/
    
[^4]: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-building-agents.html
    
[^5]: https://pypi.org/project/strands-agents-tools/
    
[^6]: https://jettro.dev/strands-the-new-agent-framework-supported-by-amazon-1b3ecccb0209
    
[^7]: https://dev.to/aws/building-strands-agents-with-a-few-lines-of-code-observability-and-with-langfuse-4bc4
    
[^8]: https://langfuse.com/integrations/frameworks/strands-agents
    
[^9]: https://python.langchain.com/docs/how_to/custom_tools/
    
[^10]: https://realpython.com/command-line-interfaces-python-argparse/
    
[^11]: https://docs.python.org/3/library/argparse.html
