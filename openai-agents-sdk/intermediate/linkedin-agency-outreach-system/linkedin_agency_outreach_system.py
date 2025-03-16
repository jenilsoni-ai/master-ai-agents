import os
import streamlit as st
import asyncio
import requests
import json
import traceback
from dotenv import load_dotenv
from openai import OpenAI
from agents import (
    Agent, 
    Runner,
    handoff,
    RunContextWrapper,
    function_tool
)
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Load environment variables
load_dotenv()

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
PROXYCURL_API_KEY = st.secrets["PROXYCURL_API_KEY"]

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Define OutreachContext
@dataclass
class OutreachContext:
    name: Optional[str]
    linkedinUrl: Optional[str]
    profileData: Optional[Dict[str, Any]]
    email: Optional[str]

# Instructions for each agent
AGENCY_TEAM_LEAD_INSTRUCTIONS = """
You are the LinkedIn Agency Team Lead responsible for managing the outreach workflow.
Follow these steps in sequence:
1. If the lead's LinkedIn profile data is not present (i.e. only name and LinkedIn URL are provided), instruct the Lead Research Specialist to scrape and parse the LinkedIn profile using the provided URL. Do not output a final result at this stage.
2. Once you receive the profile data from the Lead Research Specialist, instruct the Cold Email Outreach Specialist to generate a personalized outreach email based on the profile data that highlights our premium LinkedIn agency services.
3. After receiving the email draft from the Cold Email Outreach Specialist, review it and output the final outreach email.
Ensure that you do not output any intermediate results (like raw profile data) as your final response.
"""

LEAD_RESEARCH_SPECIALIST_INSTRUCTIONS = """
You are a Lead Research Specialist responsible for researching leads.
Your job is to extract and parse LinkedIn profile information.
Use the scrape_linkedin_profile tool to obtain the profile data.
Once done, hand off your result to your supervisor.
"""

COLD_EMAIL_SPECIALIST_INSTRUCTIONS = """
You are a Cold Email Specialist responsible for drafting highly personalized outreach emails.
Use the generate_outreach_email tool to write a personalized email that offers our premium LinkedIn agency services.
Once done, hand off your email draft to the Agency Team Lead.
"""

# LinkedIn Profile Schema
LINKEDIN_PROFILE_SCHEMA = {
    "type": "object",
    "properties": {
        "current_role": {"type": "string", "description": "The current job title of the person on LinkedIn."},
        "company": {"type": "string", "description": "The name of the company where the person is currently employed."},
        "industry": {"type": "string", "description": "The industry the person works in."},
        "experience": {
            "type": "array",
            "description": "A list of previous job positions held by the person.",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The job title of the position held."},
                    "company": {"type": "string", "description": "The name of the company where the job was held."},
                    "duration": {"type": "string", "description": "The duration of time spent in the position."},
                },
                "required": ["title", "company", "duration"],
                "additionalProperties": False,
            },
        },
        "education": {
            "type": "array",
            "description": "A list of educational qualifications.",
            "items": {"type": "string", "description": "Educational qualification in format: Degree, Institution, Year"},
        },
        "interests": {
            "type": "array",
            "description": "A list of professional interests mentioned on the profile.",
            "items": {"type": "string", "description": "A professional interest or topic"},
        },
        "recent_activity": {"type": "string", "description": "Brief description of recent activity on LinkedIn, if visible."},
    },
    "required": ["current_role", "company", "industry", "experience", "education", "interests", "recent_activity"],
    "additionalProperties": False,
}

# Handoff Callback for UI Updates
def on_handoff_callback(ctx: RunContextWrapper[OutreachContext]):
    st.write("🔁 Handoff just happened")

# Parse LinkedIn Profile 
def parse_linkedin_profile(page_markdown: str):
    try:
        response = client.responses.create(
            model="gpt-4o-mini",  # corrected model name
            input=[
                {"role": "system", "content": [{"type": "text", "text": "You're an expert at parsing a LinkedIn page and extracting relevant information. Only output the parsed information. Do not include any extra text."}]},
                {"role": "user", "content": [{"type": "text", "text": page_markdown}]},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "linkedin_profile",
                    "strict": True,
                    "schema": LINKEDIN_PROFILE_SCHEMA,
                }
            },
            temperature=0.5,
            top_p=1,
        )
        return json.loads(response.content[0]["text"])
    except Exception as ex:
        raise Exception(f"Error parsing LinkedIn profile: {ex}\nTraceback: {traceback.format_exc()}")

# Scrape LinkedIn Profile Tool using Proxycurl API
@function_tool
def scrape_linkedin_profile(wrapper: RunContextWrapper[OutreachContext], linkedin_url: str) -> Dict[str, Any]:
    try:
        headers = {'Authorization': 'Bearer ' + PROXYCURL_API_KEY}
        api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
        params = {
            'linkedin_profile_url': linkedin_url,
            'extra': 'include',
            'use_cache': 'if-present',
            'fallback_to_cache': 'on-error'
        }
        response = requests.get(api_endpoint, params=params, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to scrape LinkedIn profile: HTTP {response.status_code} - {response.text}")
        # Use the JSON response directly as profile data
        profile_data = response.json()
        wrapper.context.profileData = profile_data  # Update context directly
        return profile_data
    except Exception as ex:
        raise Exception(f"Error scraping LinkedIn profile: {ex}\nTraceback: {traceback.format_exc()}")

# Define the Generate Outreach Email Tool
@function_tool
def generate_outreach_email(wrapper: RunContextWrapper[OutreachContext]) -> str:
    if not wrapper.context.profileData:
        raise Exception("No LinkedIn profile data available.")
    try:
        system_prompt = ("You are an expert at writing personalized outreach emails to LinkedIn users. "
                         "Write an email that offers premium LinkedIn agency services, including profile optimization, "
                         "targeted networking strategies, and lead generation solutions, tailored to the recipient's professional background.")
        prompt_details = f"""
        USER INFORMATION:
        {wrapper.context.name}
        {json.dumps(wrapper.context.profileData, indent=2)}
        
        Guideline:
        1. Write a personalized outreach email offering our premium LinkedIn agency services.
        2. Highlight how our services can optimize the recipient's profile, boost their networking efforts, and generate quality leads.
        3. The email should be professional, engaging, and less than 200 words.
        4. Write in a formal tone.
        
        Sender Name - AI
        Sender Company - AI Outreach Team
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_details},
            ],
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
        )
        outreach_email = response.choices[0].message.content
        wrapper.context.email = outreach_email  # Update context directly
        return outreach_email
    except Exception as ex:
        raise Exception(f"Error generating outreach email: {ex}\nTraceback: {traceback.format_exc()}")

# Define Agents
agency_team_lead_agent = Agent[OutreachContext](
    name="Agency Team Lead",
    instructions=prompt_with_handoff_instructions(AGENCY_TEAM_LEAD_INSTRUCTIONS),
    model="gpt-4o"
)

lead_research_specialist_agent = Agent[OutreachContext](
    name="Lead Research Specialist",
    instructions=prompt_with_handoff_instructions(LEAD_RESEARCH_SPECIALIST_INSTRUCTIONS),
    model="gpt-4o",
    tools=[scrape_linkedin_profile]
)

cold_outreach_specialist_agent = Agent[OutreachContext](
    name="Cold Email Outreach Specialist",
    instructions=prompt_with_handoff_instructions(COLD_EMAIL_SPECIALIST_INSTRUCTIONS),
    model="gpt-4o",
    tools=[generate_outreach_email]
)

# Set Handoffs
agency_team_lead_agent.handoffs = [
    handoff(lead_research_specialist_agent, on_handoff=on_handoff_callback),
    handoff(cold_outreach_specialist_agent, on_handoff=on_handoff_callback)
]
lead_research_specialist_agent.handoffs = [
    handoff(agency_team_lead_agent, on_handoff=on_handoff_callback)
]
cold_outreach_specialist_agent.handoffs = [
    handoff(agency_team_lead_agent, on_handoff=on_handoff_callback)
]

# Streamlit UI
st.sidebar.title("Input Lead Details")
name = st.sidebar.text_input("Lead's Name", placeholder="e.g., John Doe")
linkedin_url = st.sidebar.text_input("LinkedIn URL", placeholder="e.g., https://linkedin.com/in/johndoe")

if st.sidebar.button("Generate Outreach Email", key="generate_button"):
    if not name or not linkedin_url:
        st.error("Please provide both the lead's name and LinkedIn URL.")
    else:
        st.markdown("### Processing Your Request")
        with st.spinner("Running outreach process..."):
            context = OutreachContext(name=name, linkedinUrl=linkedin_url, profileData=None, email=None)
            try:
                run_outreach_system = asyncio.run(Runner.run(
                    starting_agent=agency_team_lead_agent,
                    input=f"Name: {name}, LinkedinUrl: {linkedin_url}. Start the outreach process.",
                    context=context,
                    max_turns=10
                ))
                if run_outreach_system.final_output:
                    st.success("Outreach process completed successfully!")
                    # Display Extracted Profile Data
                    with st.expander("View Extracted LinkedIn Profile Data", expanded=False):
                        st.json(context.profileData if context.profileData else {"message": "No profile data extracted."})
                    # Display Generated Email
                    st.subheader("Generated Outreach Email")
                    st.text_area("", run_outreach_system.final_output, height=300, key="email_output")
                    st.download_button(
                        label="Download Email",
                        data=run_outreach_system.final_output,
                        file_name=f"outreach_email_{name}.txt",
                        mime="text/plain",
                        key="download_button"
                    )
                    st.balloons()  # Celebratory effect
                else:
                    st.error("Failed to generate outreach email. Please check the LinkedIn URL or try again.")
            except Exception as e:
                st.error("An error occurred during the outreach process. See details below:")
                st.error(str(e))
                st.text(traceback.format_exc())
else:
    st.markdown("### 👥 LinkedIn Agency Outreach System")
    st.write("""
    Welcome to the LinkedIn Agency Outreach System! This tool leverages AI agents to:
    - Research a lead's LinkedIn profile.
    - Generate a personalized outreach email offering premium LinkedIn agency services.
    
    Enter the lead's name and LinkedIn URL in the sidebar, then click 'Generate Outreach Email' to start.
    """)

st.markdown("---")
