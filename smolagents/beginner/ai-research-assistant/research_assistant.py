"""
Beginner Research Assistant using Hugging Face Smol Agents

- Uses DuckDuckGoSearchTool for web search
- Uses HfApiModel (public LLM) for summarization
- Prompts user for a research question and returns answer with sources
- Prompts user for Hugging Face access token (input masked with asterisks) and authenticates if provided
"""

from smolagents import ToolCallingAgent, DuckDuckGoSearchTool, HfApiModel
from huggingface_hub import login
import os
import pwinput

def main():
    print("\n=== Beginner Research Assistant (Smol Agents) ===\n")
    # Prompt for Hugging Face access token (input masked with asterisks)
    token = pwinput.pwinput(prompt="Enter your Hugging Face access token: ", mask='*').strip()
    if token:
        login(token=token)
        print("Authenticated with Hugging Face Hub.\n")
    else:
        print("Proceeding without authentication.\n")

    # Initialize the web search tool
    search_tool = DuckDuckGoSearchTool()

    # Use a public model known to work with the Inference API
    model = HfApiModel("HuggingFaceH4/zephyr-7b-beta")

    # Create the agent
    agent = ToolCallingAgent(
        tools=[search_tool],
        model=model,
        max_steps=3,
    )

    query = input("Enter your research question: ")
    print("\nResearching...\n")
    
    # Run the agent
    answer = agent.run(query)
    print("\n=== Answer ===\n")
    print(answer)

if __name__ == "__main__":
    main() 