import boto3
import time
from pathlib import Path
from bedrock_agentcore_starter_toolkit import Runtime
from boto3.session import Session

def cleanup_from_launch_result():
    """
    Clean up AgentCore resources using launch_result from deployment.
    This works when you have just deployed and still have launch_result in memory.
    """
    boto_session = Session()
    region = boto_session.region_name
    
    print(f"Starting cleanup in region: {region}")
    
    # Get launch result from recent deployment
    runtime = Runtime()
    
    try:
        # Launch or get existing deployment info
        launch_result = runtime.launch()
        
        print(f"\nFound deployment:")
        print(f"   ECR URI: {launch_result.ecr_uri}")
        print(f"   Agent ID: {launch_result.agent_id}")
        print(f"   Repository: {launch_result.ecr_uri.split('/')[1]}")
        
        # Create AWS clients
        agentcore_control_client = boto3.client(
            'bedrock-agentcore-control',
            region_name=region
        )
        ecr_client = boto3.client(
            'ecr',
            region_name=region
        )
        
        # 1. Delete Agent Runtime
        print("\nDeleting agent runtime...")
        try:
            runtime_delete_response = agentcore_control_client.delete_agent_runtime(
                agentRuntimeId=launch_result.agent_id,
            )
            print(f"   Agent runtime deletion initiated")
            print(f"   Status: {runtime_delete_response.get('status', 'DELETING')}")
            
            # Wait for deletion to complete
            print("   Waiting for runtime deletion...")
            time.sleep(15)
            
        except Exception as e:
            print(f"   Error deleting runtime: {e}")
        
        # 2. Delete ECR Repository
        print("\nDeleting ECR repository...")
        try:
            repository_name = launch_result.ecr_uri.split('/')[1]
            response = ecr_client.delete_repository(
                repositoryName=repository_name,
                force=True
            )
            print(f"   ECR repository deleted: {repository_name}")
            print(f"   Repository ARN: {response['repository']['repositoryArn']}")
            
        except Exception as e:
            print(f"   Error deleting ECR repository: {e}")
        
        # 3. Clean up local config files
        print("\nCleaning up local files...")
        local_files = [
            '.bedrock_agentcore.yaml',
            'Dockerfile',
            '.dockerignore',
            'agent_config.json'
        ]
        for file in local_files:
            file_path = Path(file)
            if file_path.exists():
                file_path.unlink()
                print(f"   Deleted {file}")
        
        print("\nCleanup complete!")
        print("\nCost savings:")
        print("   - Agent runtime charges: STOPPED")
        print("   - ECR storage charges: STOPPED")
        
        return True
        
    except Exception as e:
        print(f"\nCleanup failed: {e}")
        return False


def cleanup_by_config():
    """
    Alternative cleanup method using existing .bedrock_agentcore.yaml config.
    Use this when you don't have launch_result in memory.
    """
    boto_session = Session()
    region = boto_session.region_name
    
    print(f"Starting cleanup from config in region: {region}")
    
    # Read config file
    config_path = Path('.bedrock_agentcore.yaml')
    if not config_path.exists():
        print("No .bedrock_agentcore.yaml found. Nothing to clean up.")
        return False
    
    import yaml
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    default_agent = config.get('default_agent')
    agent_config = config.get('agents', {}).get(default_agent, {})
    agent_name = agent_config.get('name', default_agent)
    aws_config = agent_config.get('aws', {})
    region = aws_config.get('region', region)
    
    print(f"   Agent name: {agent_name}")
    
    # Create AWS clients
    agentcore_control_client = boto3.client(
        'bedrock-agentcore-control',
        region_name=region
    )
    ecr_client = boto3.client(
        'ecr',
        region_name=region
    )
    
    # 1. Find and delete agent runtime
    print("\nFinding agent runtime...")
    try:
        runtimes_response = agentcore_control_client.list_agent_runtimes()
        runtimes = runtimes_response.get('agentRuntimes', [])
        
        agent_id = None
        ecr_uri = None
        
        for runtime in runtimes:
            if runtime['agentRuntimeName'] == agent_name:
                agent_id = runtime['agentRuntimeId']
                artifact = runtime.get('agentRuntimeArtifact', {})
                container_config = artifact.get('containerConfiguration', {})
                ecr_uri = container_config.get('containerUri', '')
                print(f"   Found runtime: {agent_id}")
                break
        
        if not agent_id:
            print(f"   Agent '{agent_name}' not found (may already be deleted)")
        else:
            # Delete runtime
            print(f"\nDeleting agent runtime: {agent_id}")
            agentcore_control_client.delete_agent_runtime(
                agentRuntimeId=agent_id
            )
            print("   Agent runtime deletion initiated")
            time.sleep(15)
            
            # Delete ECR repository
            if ecr_uri:
                print(f"\nDeleting ECR repository from URI: {ecr_uri}")
                repository_name = ecr_uri.split('/')[1].split(':')[0]
                try:
                    ecr_client.delete_repository(
                        repositoryName=repository_name,
                        force=True
                    )
                    print(f"   ECR repository deleted: {repository_name}")
                except Exception as e:
                    print(f"   Error deleting ECR: {e}")
            else:
                print(f"\nAttempting to delete ECR repository: bedrock-agentcore-{agent_name}")
                try:
                    ecr_client.delete_repository(
                        repositoryName=f"bedrock-agentcore-{agent_name}",
                        force=True
                    )
                    print(f"   ECR repository deleted")
                except Exception as e:
                    print(f"   Error deleting ECR: {e}")
    
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    # 2. Clean up local files
    print("\nCleaning up local files...")
    local_files = [
        '.bedrock_agentcore.yaml',
        'Dockerfile',
        '.dockerignore',
        'agent_config.json'
    ]
    for file in local_files:
        file_path = Path(file)
        if file_path.exists():
            file_path.unlink()
            print(f"   Deleted {file}")
    
    print("\nCleanup complete!")
    return True


def verify_cleanup():
    """Verify all resources are deleted"""
    boto_session = Session()
    region = boto_session.region_name
    
    print(f"\nVerifying cleanup in region: {region}")
    
    agentcore_control_client = boto3.client(
        'bedrock-agentcore-control',
        region_name=region
    )
    ecr_client = boto3.client('ecr', region_name=region)
    
    # Check agent runtimes
    print("\nChecking agent runtimes...")
    try:
        runtimes = agentcore_control_client.list_agent_runtimes()
        runtime_count = len(runtimes.get('agentRuntimes', []))
        if runtime_count == 0:
            print("   No agent runtimes found")
        else:
            print(f"   {runtime_count} agent runtime(s) still exist:")
            for runtime in runtimes['agentRuntimes']:
                print(f"      - {runtime['agentRuntimeName']}: {runtime['status']}")
    except Exception as e:
        print(f"   Error checking runtimes: {e}")
    
    # Check ECR repositories
    print("\nChecking ECR repositories...")
    try:
        repos = ecr_client.describe_repositories()
        bedrock_repos = [r for r in repos.get('repositories', []) 
                        if 'bedrock-agentcore' in r['repositoryName']]
        if not bedrock_repos:
            print("   No bedrock-agentcore ECR repositories found")
        else:
            print(f"   {len(bedrock_repos)} repository(ies) still exist:")
            for repo in bedrock_repos:
                print(f"      - {repo['repositoryName']}")
    except Exception as e:
        print(f"   Error checking ECR: {e}")


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("AWS Bedrock AgentCore Cleanup Script")
    print("=" * 60)
    
    # Try cleanup from config first
    success = cleanup_by_config()
    
    if not success:
        print("\nConfig-based cleanup failed. This is normal if:")
        print("   - Agent was already deleted")
        print("   - No .bedrock_agentcore.yaml exists")
    
    # Verify cleanup
    verify_cleanup()
    
    print("\n" + "=" * 60)
    print("Cleanup script finished")
    print("=" * 60)
