# Complete Tutorial: Building AI Agents with AWS Bedrock AgentCore

## Purpose

This tutorial demonstrates how to build, deploy, and manage a **production-ready AI agent** on AWS Bedrock AgentCore using the Strands framework. The agent combines multiple capabilities: calculations, web search, currency conversion, and weather information—all running serverlessly on AWS infrastructure.[^3]

**Topics**:

- Deploy AI agents to AWS without managing infrastructure
- Create custom tools that agents can use autonomously
- Test and invoke deployed agents programmatically
- Update agents with zero downtime
- Clean up resources to avoid costs

## Project Structure

```
strands-agent-project/
├── agent.py                    # Agent logic with custom tools
├── requirements.txt            # Python dependencies
├── deploy.py                   # Deployment automation script
├── test_invoke.py             # Testing script for deployed agent
├── cleanup.py                  # Resource cleanup script
└── .bedrock_agentcore.yaml    # Auto-generated deployment config
```

### File Purposes

**agent.py** - Core agent definition with tools (calculator, web search, currency converter)[^4]

**requirements.txt** - All Python packages needed by the agent[^5]

**deploy.py** - Automated deployment to AWS[^6]

**test_invoke.py** - Invoke and test the deployed agent[^7]

**cleanup.py** - Delete all AWS resources to stop charges[^8]

## Core Concepts

### AgentCore Runtime

**Serverless container platform** for running AI agents with up to 8 hours execution time. It handles:[^3]

- Docker containerization automatically
- Auto-scaling based on load
- Isolated execution environments
- CloudWatch logging and monitoring

### Strands Framework

**Open-source SDK** for building AI agents that can reason, use tools, and make decisions. Key components:[^10]

**Agent** - The AI brain that processes requests and decides which tools to use[^9]

**Tools** - Functions decorated with `@tool` that the agent can call[^11]

**Model** - The LLM backend (Claude, GPT, etc.) that powers reasoning[^12]

### Agent Tools

Your agent has **four tools**:[^4]

1. **calculator** - Performs math operations (prebuilt by Strands)
2. **web_search** - Searches DuckDuckGo for information
3. **convert_currency** - Converts between USD, SGD, EUR, JPY
4. **weather** - Returns current weather (dummy implementation)

## Code Explanation

### agent.py - The Agent Brain

```python
from strands import Agent, tool
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands.models import BedrockModel
from strands_tools import calculator
from ddgs import DDGS

app = BedrockAgentCoreApp()  # Wrapper for AgentCore deployment
```

**Imports explained**:[^4]

- `Agent, tool` - Core Strands components for building agents
- `BedrockAgentCoreApp` - Connects agent to AWS infrastructure
- `BedrockModel` - Interface to AWS Bedrock LLMs (Claude)
- `calculator` - Prebuilt math tool from Strands
- `DDGS` - DuckDuckGo search library

### Custom Tool: Web Search

```python
@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo.
  
    Args:
        query: Search query string
        max_results: Number of results (default: 5)
  
    Returns:
        Formatted search results with titles, URLs, and snippets
    """
    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=max_results)
  
        formatted = []
        for idx, result in enumerate(results, 1):
            formatted.append(
                f"{idx}. **{result['title']}**\n"
                f"   URL: {result['href']}\n"
                f"   {result['body']}\n"
            )
  
        return "\n".join(formatted) if formatted else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"
```

**How it works**:[^4]

- `@tool` decorator registers this as an agent-usable function[^11]
- **Docstring is critical** - the agent reads it to understand when to use this tool[^9]
- **Type hints** help the agent pass correct parameters
- **Error handling** returns error messages instead of crashing

### Custom Tool: Currency Converter

```python
@tool
def convert_currency(amount: float, from_currency: str, to_currency: str):
    """Convert between USD, SGD, EUR, and JPY using exchange rates"""
    rates = {
        "USD": 1.0,
        "SGD": 1.35,
        "EUR": 0.92,
        "JPY": 149.50
    }
  
    if from_currency not in rates or to_currency not in rates:
        return "Currency not supported. Use USD, SGD, EUR, or JPY"
  
    usd_amount = amount / rates[from_currency]
    result = usd_amount * rates[to_currency]
    return f"{amount} {from_currency} = {result:.2f} {to_currency}"
```

**Key points**:[^4]

- Uses hardcoded rates (in production, fetch from API)
- Agent automatically extracts parameters from user queries
- Returns human-readable strings

### Agent Configuration

```python
model = BedrockModel(model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0")

agent = Agent(
    model=model,
    tools=[calculator, weather, web_search, convert_currency],
    system_prompt="You're a helpful assistant."
)
```

**Configuration explained**:[^4]

- **model_id** - Specifies Claude 3.7 Sonnet from AWS Bedrock
- **tools list** - All functions the agent can call
- **system_prompt** - Defines agent's personality and behavior

### Entrypoint for AgentCore

```python
@app.entrypoint
def invoke(payload):
    user_input = payload.get("prompt")
    response = agent(user_input)
    return response.message['content'][^0]['text']
```

**Critical for deployment**:[^4]

- `@app.entrypoint` marks this as the AWS Lambda handler[^13]
- **payload** comes from AWS as a dictionary
- **Must return string or dict** - this becomes the API response
- `agent(user_input)` triggers the full reasoning loop

### Local Testing

```python
if __name__ == "__main__":
    app.run()  # Starts local server on port 8080
```

Test locally before deploying:[^4]

```bash
python agent.py
# In another terminal:
curl -X POST http://localhost:8080/invoke \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is 100 USD in SGD?"}'
```

### requirements.txt - Dependencies

```
strands-agents                          # Core Strands SDK
strands-agents-tools                    # Prebuilt tools like calculator
uv                                      # Fast Python package installer
boto3                                   # AWS SDK
bedrock-agentcore<=0.1.5               # AgentCore runtime library
bedrock-agentcore-starter-toolkit==0.1.14  # CLI and deployment tools
ddgs                                    # DuckDuckGo search
```

**Version pinning**:[^5]

- `<=0.1.5` - Maximum version (avoids breaking changes)
- `==0.1.14` - Exact version (for stability)

## How to Deploy

### Step 1: Prerequisites

```bash
# Install AWS CLI and configure credentials
aws configure

# Install Python packages
pip install -r requirements.txt

# Verify Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

### Step 2: Choose Deployment Method

#### Method A: Using CLI Commands (Recommended for Beginners)

**Test locally first**:[^14]

```bash
# 4. Test locally before deploying
python agent.py  # Runs on localhost:8080
```

**Deploy with CLI**:[^16]

```bash
# 1. Configure (first time)
agentcore configure --entrypoint agent.py --name my_agent

# 2. Launch to AWS
agentcore launch

# 3. Check status
agentcore status
```

**What each command does**:[^15]

- `configure` - Creates `.bedrock_agentcore.yaml` with deployment settings
- `launch` - Builds Docker image, pushes to ECR, deploys to AgentCore
- `status` - Shows deployment state (CREATING → READY)

#### Method B: Using deploy.py Script (Programmatic)

**deploy.py automates the entire process**:[^6]

```python
from bedrock_agentcore_starter_toolkit import Runtime
from boto3.session import Session

boto_session = Session()
region = boto_session.region_name

runtime = Runtime()

runtime.configure(
    entrypoint="agent.py",
    auto_create_execution_role=True,
    auto_create_ecr=True,
    requirements_file="requirements.txt",
    region=region,
    agent_name="my_strands_agent"
)

launch_result = runtime.launch()
print(f"Agent ARN: {launch_result.agent_arn}")
```

**What happens behind the scenes**:[^17]

1. **configure()** creates `.bedrock_agentcore.yaml` with deployment settings
2. **auto_create_execution_role** creates IAM role with Bedrock permissions
3. **auto_create_ecr** creates Elastic Container Registry for Docker images
4. **launch()** builds Docker container, pushes to ECR, deploys to AgentCore

**Run deployment**:

```bash
python deploy.py
```

**Output**:

```
Building container...
Pushing to ECR...
Creating agent runtime...
Agent ARN: arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/my_strands_agent-abc123
```

### Step 3: Monitor Deployment

```bash
# CLI method
agentcore status

# Expected output:
# Agent Runtime Status: READY
# Endpoint: https://xxx.execute-api.us-east-1.amazonaws.com
```

Deployment takes **2-5 minutes** depending on dependencies.[^19]

## How to Test

### Method 1: Using test_invoke.py (Recommended)

**test_invoke.py automatically finds and invokes your agent**:[^7]

```python
import boto3
import json
import yaml
from pathlib import Path

# Load configuration from .bedrock_agentcore.yaml
config_path = Path(".bedrock_agentcore.yaml")
if not config_path.exists():
    raise FileNotFoundError("No .bedrock_agentcore.yaml found. Deploy your agent first.")

with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Parse nested structure
default_agent_name = config.get('default_agent')
agents_config = config.get('agents', {})
agent_config = agents_config.get(default_agent_name, {})
agent_name = agent_config.get('name', default_agent_name)
aws_config = agent_config.get('aws', {})
region = aws_config.get('region', 'us-east-1')

# Find agent in AWS
control_client = boto3.client('bedrock-agentcore-control', region_name=region)
runtimes_response = control_client.list_agent_runtimes()

agent_arn = None
for runtime in runtimes_response.get('agentRuntimes', []):
    if runtime.get('agentRuntimeName') == agent_name:
        agent_arn = runtime.get('agentRuntimeArn')
        break

# Invoke agent
agentcore_client = boto3.client('bedrock-agentcore', region_name=region)
response = agentcore_client.invoke_agent_runtime(
    agentRuntimeArn=agent_arn,
    qualifier="DEFAULT",
    payload=json.dumps({"prompt": "Who founded AWS?"})
)

# Read response
full_response = response['response'].read()
decoded = full_response.decode('utf-8')
print(decoded)
```

**Run it**:[^7]

```bash
python test_invoke.py
```

**Expected output**:

```
Looking for agent: my_strands_agent in region: us-east-1
Found 1 deployed agent(s)
  - my_strands_agent: READY

Agent ARN: arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/my_strands_agent-abc123

Invoking agent with prompt...

Agent response:
AWS (Amazon Web Services) was founded by Jeff Bezos in 2006...
```

### Method 2: CLI Testing

```bash
# Quick test
agentcore invoke '{"prompt": "What is 50 EUR in JPY?"}'

# Test web search
agentcore invoke '{"prompt": "Search for latest AI news"}'

# Test calculator
agentcore invoke '{"prompt": "Calculate the square root of 144"}'
```

### Method 3: Direct boto3 Invocation

```python
import boto3
import json

client = boto3.client('bedrock-agentcore', region_name='us-east-1')

response = client.invoke_agent_runtime(
    agentRuntimeArn="<paste-your-arn-here>",
    qualifier="DEFAULT",
    payload=json.dumps({"prompt": "Convert 100 USD to SGD"})
)

result = response['response'].read().decode('utf-8')
print(result)
```

## How to Update Agent and Redeploy

### Step 1: Modify agent.py

Add a new tool or change existing code:[^4]

```python
@tool
def get_time():
    """Get current UTC time"""
    from datetime import datetime
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

# Add to agent tools list
agent = Agent(
    model=model,
    tools=[calculator, weather, web_search, convert_currency, get_time],
    system_prompt="You're a helpful assistant."
)
```

### Step 2: Update requirements.txt (if needed)

If you added new dependencies:[^5]

```
strands-agents
strands-agents-tools
boto3
bedrock-agentcore<=0.1.5
bedrock-agentcore-starter-toolkit==0.1.14
ddgs
python-dateutil  # New dependency
```

### Step 3: Redeploy

**Using CLI**:[^18]

```bash
agentcore launch --auto-update-on-conflict
```

**Or using deploy.py**:[^6]

```bash
python deploy.py
```

**What happens**:[^18]

- Builds new Docker image with updated code
- Creates new agent runtime version (V2)
- Updates DEFAULT endpoint to point to V2
- V1 remains available for rollback

### Step 4: Verify Update

```bash
# Check status
agentcore status

# Test new functionality
python test_invoke.py
```

**Zero downtime**: Old version serves traffic until new version is ready.[^3]

## How to Clean Up

### Why Clean Up?

**Cost components**:[^22]

- Agent Runtime: \$0.000027/vCPU-second (charges during execution)
- ECR Storage: \$0.10/GB/month (container images)
- CodeBuild: \$0.005/build minute (only during deployment)

**Delete resources to stop charges**.[^23]

### Method 1: Using cleanup.py (Recommended)

**cleanup.py provides two cleanup strategies**:[^8]

**Strategy 1: cleanup_by_config()** - Uses `.bedrock_agentcore.yaml`

```python
def cleanup_by_config():
    # Reads config file
    # Finds agent in AWS
    # Deletes agent runtime
    # Deletes ECR repository
    # Removes local config files
```

**Strategy 2: cleanup_from_launch_result()** - Uses deployment info

```python
def cleanup_from_launch_result():
    # Gets launch_result from runtime
    # Deletes using agent_id and ecr_uri
```

**Run cleanup**:[^8]

```bash
python cleanup.py
```

**Expected output**:

```
============================================================
AWS Bedrock AgentCore Cleanup Script
============================================================
Starting cleanup from config in region: us-east-1
   Agent name: my_strands_agent

Finding agent runtime...
   Found runtime: abc123-def456

Deleting agent runtime: abc123-def456
   Agent runtime deletion initiated

Deleting ECR repository from URI: 123456789012.dkr.ecr.us-east-1.amazonaws.com/bedrock-agentcore-my_strands_agent:v1
   ECR repository deleted: bedrock-agentcore-my_strands_agent

Cleaning up local files...
   Deleted .bedrock_agentcore.yaml
   Deleted Dockerfile
   Deleted .dockerignore

Cleanup complete!

Verifying cleanup in region: us-east-1

Checking agent runtimes...
   No agent runtimes found

Checking ECR repositories...
   No bedrock-agentcore ECR repositories found

============================================================
Cleanup script finished
============================================================
```

### Method 2: CLI Cleanup

```bash
# Delete agent
agentcore delete

# Verify deletion
agentcore status  # Should show "not found"

# Manually delete ECR (if needed)
aws ecr delete-repository \
  --repository-name bedrock-agentcore-my_strands_agent \
  --force \
  --region us-east-1
```

### Verification

**Check all resources are deleted**:[^8]

```python
# cleanup.py includes verify_cleanup() function
def verify_cleanup():
    # Lists remaining agent runtimes
    # Lists remaining ECR repositories
    # Confirms cleanup success
```

## Complete Execution Flow

### 1. Initial Setup (One Time)

```bash
# Clone or create project
mkdir strands-agent-project
cd strands-agent-project

# Copy files
# - agent.py
# - requirements.txt
# - deploy.py
# - test_invoke.py
# - cleanup.py

# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials
aws configure
```

### 2. Development Cycle

```bash
# Test locally
python agent.py
# Agent runs on http://localhost:8080

# In another terminal
curl -X POST http://localhost:8080/invoke \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test query"}'
```

### 3. Deploy to AWS

**Option A: CLI commands**:[^16]

```bash
# 1. Configure (first time)
agentcore configure --entrypoint agent.py --name my_agent

# 2. Launch to AWS
agentcore launch

# 3. Check status
agentcore status
```

**Option B: Python script**:[^6]

```bash
# Deploy
python deploy.py

# Output:
# Agent ARN: arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/my_strands_agent-abc123

# Wait for READY status
agentcore status
```

### 4. Testing

```bash
# Test deployed agent
python test_invoke.py

# Or use CLI
agentcore invoke '{"prompt": "What is 2+2?"}'
```

### 5. Updates

```bash
# Modify agent.py
vim agent.py

# Redeploy with CLI
agentcore launch

# Or with script
python deploy.py

# Test changes
python test_invoke.py
```

### 6. Cleanup

```bash
# Delete all resources
python cleanup.py

# Verify deletion
agentcore status  # Should show "not found"
```

## Deployment Commands Summary

```bash
# Test locally before deploying
python agent.py  # Runs on localhost:8080

# First-time deployment
agentcore configure --entrypoint agent.py --name my_agent
agentcore launch

# Check deployment status
agentcore status

# Update existing agent
agentcore launch --auto-update-on-conflict

# Test deployed agent
agentcore invoke '{"prompt": "Your question here"}'

# View logs
agentcore logs --follow

# Clean up
agentcore delete
```

## Troubleshooting

### Empty Response from Agent

**Check CloudWatch logs**:[^24]

```bash
agentcore logs --follow
```

**Common causes**:[^24]

- Agent entrypoint not returning data
- Model credentials missing
- Tool execution error

### Deployment Fails

**Check IAM permissions**:

```bash
aws sts get-caller-identity
```

**Verify Bedrock access**:

```bash
aws bedrock list-foundation-models --region us-east-1
```

### High Costs

**Check active resources**:

```bash
# List agent runtimes
aws bedrock-agentcore-control list-agent-runtimes --region us-east-1

# List ECR repositories
aws ecr describe-repositories --region us-east-1
```

**Delete unused resources**:[^8]

```bash
python cleanup.py
```

## Key Takeaways

**Agent Architecture**: Tools are the agent's hands—define them with clear docstrings[^4]

**Deployment**: AgentCore handles infrastructure—you focus on agent logic[^3]

**Testing**: Always test locally first with `python agent.py`[^4]

**Updates**: Zero-downtime updates with automatic versioning[^3]

**Cleanup**: Always clean up to avoid unnecessary costs[^8]

## Next Steps

**Add more tools**: File operations, database queries, API calls[^25]

**Multi-agent systems**: Orchestrate multiple specialized agents[^27]

**Production setup**: Add OAuth authentication, custom domains[^29]

**Monitoring**: Set up CloudWatch dashboards and alarms[^2]

---

**Quick Commands Reference**:

```bash
python agent.py              # Test locally
agentcore configure          # First-time setup
agentcore launch            # Deploy to AWS
agentcore status            # Check deployment
python test_invoke.py       # Test deployed agent
python cleanup.py           # Clean up resources
agentcore logs --follow     # View logs
```

<div align="center">⁂</div>

[^1]: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html
    
[^2]: https://aws.amazon.com/bedrock/agentcore/
    
[^3]: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-how-it-works.html
    
[^4]: agent.py
    
[^5]: requirements.txt
    
[^6]: deploy.py
    
[^7]: test_invoke.py
    
[^8]: cleanup.py
    
[^9]: https://aws.amazon.com/blogs/opensource/introducing-strands-agents-an-open-source-ai-agents-sdk/
    
[^10]: https://jettro.dev/strands-the-new-agent-framework-supported-by-amazon-1b3ecccb0209
    
[^11]: https://dev.to/aws/building-strands-agents-with-a-few-lines-of-code-custom-tools-and-mcp-integration-3c1c
    
[^12]: https://dev.to/aws-builders/building-ai-agents-with-amazon-bedrock-agentcore-runtime-a-complete-setup-guide-50oh
    
[^13]: https://aws.github.io/bedrock-agentcore-starter-toolkit/user-guide/runtime/quickstart.html
    
[^14]: https://dev.to/aws-builders/from-demos-to-business-value-taking-agents-to-production-with-amazon-bedrock-agentcore-2pdj
    
[^15]: https://codesignal.com/learn/courses/deploying-agents-aws-with-bedrock-agentcore/lessons/deploying-agents-with-agentcore
    
[^16]: https://aws.github.io/bedrock-agentcore-starter-toolkit/api-reference/cli.html
    
[^17]: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/getting-started-starter-toolkit.html
    
[^18]: https://dev.to/aws-builders/how-i-combined-strands-agents-bedrock-agentcore-runtime-and-agentcore-browser-to-automate-aws-docs-50nd
    
[^19]: https://caylent.com/blog/amazon-bedrock-agent-core-redefining-agent-infrastructure-as-undifferentiated-heavy-lifting
    
[^20]: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/update_agent_runtime.html
    
[^21]: https://aihub.hkuspace.hku.hk/2025/08/14/securely-launch-and-scale-your-agents-and-tools-on-amazon-bedrock-agentcore-runtime/
    
[^22]: https://codesignal.com/learn/courses/deploying-agents-aws-with-bedrock-agentcore/lessons/managing-agentcore-resources-1
    
[^23]: https://docs.aws.amazon.com/bedrock/latest/userguide/agent-tutorial-step6.html
    
[^24]: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-troubleshooting.html
    
[^25]: https://github.com/strands-agents/tools
    
[^26]: https://aws.amazon.com/blogs/devops/multi-agent-collaboration-with-strands/
    
[^27]: https://aws.amazon.com/blogs/opensource/introducing-strands-agents-1-0-production-ready-multi-agent-orchestration-made-simple/
    
[^28]: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-oauth.html
    
[^29]: https://aws.amazon.com/blogs/machine-learning/set-up-custom-domain-names-for-amazon-bedrock-agentcore-runtime-agents/
    
[^30]: https://dev.to/aws/first-impressions-with-amazon-bedrock-agentcore-5dje
