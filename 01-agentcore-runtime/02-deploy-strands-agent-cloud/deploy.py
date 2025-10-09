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
