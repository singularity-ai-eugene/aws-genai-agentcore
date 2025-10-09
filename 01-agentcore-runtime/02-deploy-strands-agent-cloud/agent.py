from strands import Agent, tool
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands.models import BedrockModel
from strands_tools import calculator  # Prebuilt tools
from ddgs import DDGS  


app = BedrockAgentCoreApp()

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


@tool
def weather():
    """Get weather"""
    return "sunny"

model = BedrockModel(model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0")
agent = Agent(
    model=model,
    tools=[calculator, weather, web_search, convert_currency],
    system_prompt="You're a helpful assistant."
)

@app.entrypoint
def invoke(payload):
    user_input = payload.get("prompt")
    response = agent(user_input)
    return response.message['content'][0]['text']

if __name__ == "__main__":
    app.run()  # Local testing on port 8080
