#Import necessary libraries and modules
import os
from textwrap import dedent
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from firecrawl import FirecrawlApp
from agno.playground import Playground, serve_playground_app
from agno.storage.sqlite import SqliteStorage
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

#Define Firecrawl deep research function
def firecrawl_deep_research(query: str) -> str:
    """
    Perform a deep research on the given query using FireCrawl API.
    This function utilizes the FireCrawl service to conduct comprehensive web research
    on a given topic and returns formatted results with citations.

    Args:
        query (str): The search query to research.

    Returns:
        str: Formatted research results including analysis and sources.
            Format: Analysis text followed by numbered list of sources with URLs.

    Raises:
        Exception: If API call fails or response data is invalid.
    """

    # Initialize Firecrawl client with API key
    firecrawl = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    
    # Configure research parameters to control depth and scope
    params = {
        "maxDepth": 1,  # Limit research iterations for faster results
        "timeLimit": 30,  # Maximum time in seconds for research
        "maxUrls": 3  # Maximum number of sources to analyze
    }

    # Define callback for real-time research progress updates
    def on_activity(activity):
        print(f"**[{activity['type']}]** {activity['message']}")
        
    # Execute research with error handling
    try:
        # Perform deep research using FireCrawl API
        results = firecrawl.deep_research(
            query=query,
            params=params,
            on_activity=on_activity
        )
        
        # Validate response data structure
        if not results.get('data') or not results['data'].get('finalAnalysis'):
            return "Error: No analysis data available from the research."
            
        # Extract analysis and source information
        analysis = results['data']['finalAnalysis']
        sources = results['data'].get('sources', [])
        
        # Format output with analysis and numbered source list
        formatted_output = analysis + "\n\nSources:\n"
        for i, source in enumerate(sources, 1):
            formatted_output += f"{i}. {source.get('title', 'Source')}: {source['url']}\n"
        
        return formatted_output
        
    except Exception as e:
        return f"Error during research: {str(e)}"


# Initialize the Deep Research Agent
deep_research_agent = Agent(
    name="Deep Research Agent",
    model=OpenAIChat(id="gpt-4o", api_key=OPENAI_API_KEY),
    tools=[firecrawl_deep_research],
    description="I am a research agent that can perform in-depth analysis on any topic using web sources.",
    instructions="When a user asks a question, use the firecrawl_deep_research tool to gather comprehensive information and provide a detailed response with citations.",
    storage=SqliteStorage(
        table_name="agent_sessions",
        db_file="tmp/agents.db"
    ),
    add_history_to_messages=True,
    expected_output=dedent("""
        1. Clear and detailed explanation
        2. Key findings and insights
        3. Relevant examples or evidence
        4. Citations to sources
    """),
)

# Create and configure the Playground application
app = Playground(agents=[deep_research_agent]).get_app()

# Run the application when executed as main script
if __name__ == "__main__":
    serve_playground_app("deep_research_agent:app", reload=True)