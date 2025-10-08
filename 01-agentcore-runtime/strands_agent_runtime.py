from strands import Agent, tool
from strands_tools import calculator
import argparse
import json
from strands.models import BedrockModel

# Custom tool
@tool
def weather():
    """Get weather"""
    return "sunny"

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
    
    # Convert to USD first, then to target currency
    usd_amount = amount / rates[from_currency]
    result = usd_amount * rates[to_currency]
    
    return f"{amount} {from_currency} = {result:.2f} {to_currency}"


# Model setup
model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
model = BedrockModel(model_id=model_id)

# Agent setup
agent = Agent(
    model=model,
    tools=[calculator, weather, convert_currency],
    system_prompt="You're a helpful assistant. You can do simple math calculation, convert exchange rates and tell the weather."
)

def strands_agent_bedrock(payload):
    """Invoke the agent with a payload"""
    user_input = payload.get("prompt")
    response = agent(user_input)
    return response.message['content'][0]['text']

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", type=str)
    args = parser.parse_args()
    
    response = strands_agent_bedrock(json.loads(args.payload))
    print(response)
