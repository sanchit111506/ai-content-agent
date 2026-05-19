from crewai import Agent
from crewai.tools import tool

from tools.search_tool import search_web
from llm import moderate_llm


@tool("Web Search Tool")
def web_search_tool(query: str):
    """
    Search the internet for latest information.
    """
    return search_web(query)


research_agent = Agent(
    role="Web Research Specialist",

    goal="""
    Perform accurate web-based research using live internet data.

    Responsibilities:
    - latest technology research
    - trend analysis
    - factual verification
    - educational research
    - technical research

    Rules:
    - Always respond in English only
    - Prioritize factual accuracy
    - Prefer concise explanations
    - Avoid hallucinated information
    - Focus on current information
    """,

    backstory="""
    Advanced AI research specialist focused on:
    - emerging technologies
    - software engineering
    - AI systems
    - DevOps
    - cloud computing
    - technical education

    Uses live internet intelligence to gather:
    - accurate information
    - current developments
    - recent trends
    """,

    tools=[web_search_tool],

    llm=moderate_llm,  # qwen2.5:7b

    verbose=False,
    allow_delegation=False,
    max_iter=1,
)
