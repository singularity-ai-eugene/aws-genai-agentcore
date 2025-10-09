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

# Parse the nested structure correctly
default_agent_name = config.get('default_agent')  # Gets 'my_agent'

if not default_agent_name:
    raise ValueError("No default_agent specified in config")

# Get agent details from nested 'agents' dictionary
agents_config = config.get('agents', {})
agent_config = agents_config.get(default_agent_name, {})

# Extract name and region
agent_name = agent_config.get('name', default_agent_name)
aws_config = agent_config.get('aws', {})
region = aws_config.get('region', 'us-east-1')

print(f"Looking for agent: {agent_name} in region: {region}")

# Get ARN using control plane API
control_client = boto3.client('bedrock-agentcore-control', region_name=region)

try:
    runtimes_response = control_client.list_agent_runtimes()
    runtimes = runtimes_response.get('agentRuntimes', [])
    
    print(f"Found {len(runtimes)} deployed agent(s)")
    
    agent_arn = None
    for runtime in runtimes:
        runtime_name = runtime.get('agentRuntimeName', '')
        print(f"  - {runtime_name}: {runtime.get('status')}")
        
        if runtime_name == agent_name:
            agent_arn = runtime.get('agentRuntimeArn')
            print(f"\n✓ Found matching agent!")
            break
    
    if not agent_arn:
        raise ValueError(f"Agent '{agent_name}' not found. Available agents: {[r.get('agentRuntimeName') for r in runtimes]}")
    
    print(f"Agent ARN: {agent_arn}\n")
    
    # Invoke the agent
    agentcore_client = boto3.client('bedrock-agentcore', region_name=region)
    
    print("Invoking agent with prompt...")
    response = agentcore_client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        qualifier="DEFAULT",
        payload=json.dumps({"prompt": "Who founded AWS?"})
    )
    
    print("\nAgent response:")
    response_body = response['response']

    # Read the entire stream
    full_response = response_body.read()
    print(f"Raw bytes length: {len(full_response)}")
    print(f"Raw response: {full_response}")

    # Decode and parse
    if full_response:
        decoded = full_response.decode('utf-8')
        print(f"\nDecoded response:\n{decoded}")
        
        # Try parsing as JSON
        try:
            result = json.loads(decoded)
            print(f"\nParsed JSON:\n{json.dumps(result, indent=2)}")
        except json.JSONDecodeError:
            print(f"\nPlain text response:\n{decoded}")
    else:
        print("Empty response received!")
    
except Exception as e:
    print(f"\nError: {e}")
    print("\nTroubleshooting:")
    print("1. Check agent is deployed: agentcore status")
    print("2. Verify agent name matches deployment: agentcore list-runtimes")
    print(f"3. Ensure AWS credentials are configured for region: {region}")
