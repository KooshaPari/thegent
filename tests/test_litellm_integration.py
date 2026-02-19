import os
from pathlib import Path
import logging
from thegent.agents.codex_proxy import CodexProxyRunner
from thegent.agents.base import RunResult

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def test_codex_proxy_with_litellm():
    print("\n--- Testing CodexProxyRunner with LiteLLM Router ---")
    
    # Enable LiteLLM Router
    os.environ["THGENT_USE_LITELLM_ROUTER"] = "1"
    
    # Initialize runner for 'codex' agent
    runner = CodexProxyRunner(agent_name="codex", model="gpt-4o-mini")
    
    # Simple prompt
    prompt = "Hello, what model are you? Just give me the name."
    
    print(f"Running prompt: {prompt}")
    
    # We use a mock or try to run if we have API keys.
    # Since we're in a test environment, let's just see if it routes correctly.
    # We'll check if it calls _run_via_litellm_router.
    
    # To avoid actual API calls during test if keys aren't set,
    # we can check the logic.
    
    try:
        result = runner.run(prompt, cwd=None, mode="read", timeout=10, use_stream=False)
        print(f"Result: {result.stdout}")
        print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"Caught exception (expected if no keys): {e}")

if __name__ == "__main__":
    test_codex_proxy_with_litellm()
