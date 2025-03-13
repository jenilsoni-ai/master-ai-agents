import os
import asyncio
import streamlit as st
from dotenv import load_dotenv
from agents import Agent, Runner, WebSearchTool, FileSearchTool, handoff, trace
from pydantic import BaseModel
from typing import List

# Load environment variables
load_dotenv()

# Define the structured output data model
class ResearchResult(BaseModel):
    title: str
    abstract: str
    domain: str
    citations: List[str]
    details: str

# Define specialized research agents
cs_researcher = Agent(
    name="CS Researcher",
    instructions="""You are a computer science researcher. For the given query, conduct research using the available tools and compile your findings into a ResearchResult object. Include a title, an abstract summarizing the key points, set the domain to 'Computer Science', list citations from the sources used, and provide detailed information in the details field.""",
    model="gpt-4o-mini",
    tools=[WebSearchTool()],
    output_type=ResearchResult
)

biology_researcher = Agent(
    name="Biology Researcher",
    instructions="""You are a biology researcher. For the given query, conduct research using the available tools and compile your findings into a ResearchResult object. Include a title, an abstract summarizing the key points, set the domain to 'Biology', list citations from the sources used, and provide detailed information in the details field.""",
    model="gpt-4o-mini",
    tools=[WebSearchTool()],
    output_type=ResearchResult
)

general_researcher = Agent(
    name="General Researcher",
    instructions="""You are a general researcher. For the given query, conduct research using the available tools and compile your findings into a ResearchResult object. Include a title, an abstract summarizing the key points, set the domain to 'General', list citations from the sources used, and provide detailed information in the details field.""",
    model="gpt-4o-mini",
    tools=[WebSearchTool()],
    output_type=ResearchResult
)

# Define the triage agent
triage_agent = Agent(
    name="Triage Agent",
    instructions="""You are a triage agent. Analyze the user's query and determine which specialized agent should handle it:
    - If the query mentions algorithms, programming, or systems, hand off to the CS Researcher.
    - If the query involves biological concepts or experiments, hand off to the Biology Researcher.
    - For all other queries, hand off to the General Researcher.
    """,
    handoffs=[
        handoff(cs_researcher),
        handoff(biology_researcher),
        handoff(general_researcher)
    ],
    model="gpt-4o-mini"
)

# Define the research execution function
async def run_research(query):
    with trace("Academic Research"):
        result = await Runner.run(triage_agent, query)
    return result.final_output

# Function to update the query input based on sidebar selection
def update_query():
    if st.session_state.selected_query != "Select a query...":
        st.session_state.research_query = st.session_state.selected_query

# Streamlit app configuration
st.set_page_config(page_title="Multi-Domain Research Agent", layout="wide")
st.title("🧑‍🔬 Multi-Domain Research Agent")
st.markdown("""
    Enter a research query below, and the system will automatically delegate it to the appropriate specialized agent 
    (Computer Science, Biology, or General Research) to conduct the research and provide structured results.
""")

# Sidebar with prewritten queries
st.sidebar.markdown("**Sample Queries**")
st.sidebar.markdown("Select a sample query to populate the input field, or type your own query directly in the main area.")
prewritten_queries = [
    "Select a query...",
    "What are the latest advancements in machine learning algorithms? (CS)",
    "Explain the process of photosynthesis in plants. (Biology)",
    "Discuss the impact of climate change on global economies. (General)",
    "How does quantum computing differ from classical computing? (CS)",
    "Describe the role of CRISPR in genetic engineering. (Biology)",
    "What are the ethical implications of artificial intelligence? (General)"
]
st.sidebar.selectbox(
    "Select a sample query:",
    prewritten_queries,
    index=0,
    key="selected_query",
    on_change=update_query
)

# Main input field for the research query, bound to session state
query = st.text_input("Enter your research query:", key="research_query", placeholder="e.g., What are the latest trends in machine learning?")

# Button to start the research
if st.button("Start Research", type="primary"):
    if query:
        with st.spinner("🔍 Conducting research... Please wait."):
            try:
                # Run the asynchronous research function
                result = asyncio.run(run_research(query))
                
                # Display the research results
                st.subheader("📄 Research Results")
                st.markdown(f"**Title**: {result.title}")
                st.markdown(f"**Domain**: {result.domain}")
                st.markdown(f"**Abstract**: {result.abstract}")
                st.markdown("**Citations**:")
                for citation in result.citations:
                    st.markdown(f"- {citation}")
                st.markdown("**Details**:")
                st.write(result.details)
                
                # Optional: Display the result as JSON for debugging
                with st.expander("View Raw JSON"):
                    st.json(result.dict())
            except Exception as e:
                st.error(f"An error occurred during research: {str(e)}")
    else:
        st.warning("Please enter a research query to proceed.")