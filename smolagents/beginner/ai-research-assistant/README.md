# 🤖 AI Research Assistant

A simple research assistant built with [Hugging Face Smol Agents](https://huggingface.co/docs/smolagents/en/index). This agent performs web research on any topic using DuckDuckGo and provides concise answers with sources. Input of your Hugging Face access token is securely masked with asterisks.

## ✨ Features

- **Web Research**: Uses DuckDuckGoSearchTool to find up-to-date information
- **LLM Summarization**: Summarizes results using a public LLM via Hugging Face Inference API
- **Source Attribution**: Returns answers with links to sources
- **Secure Token Input**: Access token input is hidden with asterisks for privacy
- **Customizable**: Easily adjust agent parameters like `max_steps`

## 🛠️ Prerequisites

- Python 3.7+
- [Hugging Face account](https://huggingface.co/join)
- Hugging Face Access Token with the following permissions:
  - ✅ **Make calls to Inference Providers**
  - ✅ **Make calls to your Inference Endpoints**
  - ✅ **Manage your Inference Endpoints**
- (Optional) [Hugging Face CLI](https://huggingface.co/docs/huggingface_hub/en/guides/cli) for managing tokens

### 🔑 How to Create and Configure Your Access Token
1. Go to your [Hugging Face Access Tokens page](https://huggingface.co/settings/tokens)
2. Click **New token**
3. Name your token and select the required permissions above
4. Copy the token (starts with `hf_...`)
5. When running the script, paste your token when prompted (it will be masked with asterisks)

## 📥 Installation

1. Clone the repository and navigate to this directory:
   ```bash
   git clone https://github.com/jenilsoni-ai/master-ai-agents.git
   cd master-ai-agents/smolagents/beginner/ai-research-assistant
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

1. Run the agent:
   ```bash
   python research_assistant.py
   ```
2. When prompted, paste your Hugging Face access token (input will be masked)
3. Enter your research question
4. Review the answer and sources in your terminal

## ⚙️ Customizing Agent Parameters

You can change the number of reasoning steps (how many times the agent will try to get or refine an answer) by editing the `max_steps` parameter in `research_assistant.py`:

```python
agent = ToolCallingAgent(
    tools=[search_tool],
    model=model,
    max_steps=3,  # Change this value as needed
)
```

## 🧩 Frameworks & Tools Used
- [Smol Agents](https://huggingface.co/docs/smolagents/en/index)
- [DuckDuckGoSearchTool](https://huggingface.co/docs/smolagents/en/tutorials/tools)
- [pwinput](https://pypi.org/project/pwinput/) (for secure token input)

## 🛠️ Troubleshooting
- **403 Forbidden or Permission Errors**: Ensure your Hugging Face token has the correct permissions (see above).
- **Rate Limit Errors**: The DuckDuckGo search tool may hit rate limits. Wait a few minutes and try again, or use a different query.
- **Model Errors**: If the default model is unavailable, try another public model supported by the Hugging Face Inference API.

## 📚 Learn More
- [Smol Agents Documentation](https://huggingface.co/docs/smolagents/en/index)
- [Hugging Face Hub Python Library](https://huggingface.co/docs/huggingface_hub/en/package_reference/hf_api)

---

Feel free to explore and modify the code to suit your research needs! 