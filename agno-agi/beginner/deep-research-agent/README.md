# 🔍 Deep Research Agent

A powerful research agent built with Agno AGI that performs comprehensive web research on any topic using the FireCrawl API. The agent provides detailed analysis with proper citations and source attribution.

## ✨ Features

- **In-depth Web Research**: Utilizes FireCrawl API to conduct thorough research across multiple web sources
- **Automated Analysis**: Generates clear and detailed explanations with key findings and insights
- **Source Attribution**: Includes numbered citations with URLs for all research sources
- **Interactive Playground**: Built-in web interface for easy interaction with the research agent
- **Persistent Storage**: Maintains chat history using SQLite database

## 🛠️ Prerequisites

- Python 3.7+
- Node.js 14+ (for the frontend UI)
- OpenAI API Key
- FireCrawl API Key

## 📥 Installation

1. Clone the repository:
```bash
git clone https://github.com/jenilsoni-ai/master-ai-agents.git
cd master-ai-agents/agno-agi/beginner/deep-research-agent
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your API keys:
```
OPENAI_API_KEY='your_openai_api_key'
FIRECRAWL_API_KEY='your_firecrawl_api_key'
```

## 🚀 Usage

You'll need to run both the backend server and frontend UI in separate terminals:

1. Start the backend server (Terminal 1):
```bash
python deep_research_agent.py
```

2. Start the frontend UI (Terminal 2):
```bash
cd agent-ui
npm install    # Only needed first time
npm run dev
```

3. Open your browser and navigate to the URL shown in Terminal 2 (typically http://localhost:3000)

4. Enter your research query in the chat interface

5. Review the detailed research results with citations

## ⚙️ Customizing Research Parameters

You can customize the research behavior by modifying the parameters in the `firecrawl_deep_research` function in `deep_research_agent.py`:

```python
params = {
    "maxDepth": 1,    # Number of research iterations (1-3)
    "timeLimit": 30, # Maximum research time in seconds (30-300)
    "maxUrls": 3    # Maximum number of sources to analyze (3-10)
}
```

### Parameter Details

- **maxDepth**: Controls how deep the research goes
  - 1: Quick surface-level research
  - 2: Moderate depth (recommended)
  - 3: Deep comprehensive research

- **timeLimit**: Maximum time for research in seconds
  - 30: Quick results
  - 120: Standard research
  - 300: In-depth research

- **maxUrls**: Number of sources to analyze
  - 3: Basic research with key sources
  - 5: Balanced research (recommended)
  - 10: Comprehensive multi-source analysis


## 💾 Storage

Chat history is stored in `tmp/agents.db` using SQLite. The database is automatically created when you first run the application.
