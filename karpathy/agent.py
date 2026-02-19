import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from .tools import delegate_task
from .utils import load_instructions

load_dotenv()

# Configuration
NEXUS_URL = os.getenv("NEXUS_URL", "https://nexus-master.lmndstaging.com")
NEXUS_API_KEY = os.getenv("LITELLM_PROXY_API_KEY", "sk-12345")
MODEL = os.getenv("AGENT_MODEL", "openai/gpt-4.1")

# Main agent - use litellm_proxy prefix for proper Nexus routing
main_agent = LlmAgent(
    name="MainAgent",
    model=LiteLlm(
        model=f"litellm_proxy/{MODEL}",
        api_base=NEXUS_URL,
        api_key=NEXUS_API_KEY
    ),
    description="The main agent that makes sure the user's machine learning requests are successfully fulfilled",
    instruction=load_instructions("main_agent"),
    tools=[delegate_task],
    output_key="final_output",
)