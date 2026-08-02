import os
import sys
from hermes_agent import AIAgent

def run():
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY or OPENAI_API_KEY is missing.")
        sys.exit(1)

    print("Initializing Hermes Agent on Render...")

    agent = AIAgent(
        skip_memory=True
    )

    response = agent.run("Hermes Agent is running successfully on Render!")
    print(f"Agent Output: {response}")

if __name__ == "__main__":
    run()
