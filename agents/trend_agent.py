from crewai import Agent
from crewai.tools import tool

from tools.search_tool import search_web
from llm import moderate_llm


@tool("Trend Analysis Tool")
def trend_search_tool(query: str):
    """
    Analyze trending technologies and emerging topics.
    """
    return search_web(query)


trend_agent = Agent(
    role="Trend Intelligence Specialist",

    goal="""
    Discover emerging trends and opportunities.

    Responsibilities:
    - trending technologies
    - viral topics
    - SEO opportunities
    - future technology trends

    Rules:
    - Always respond in English only
    - Focus on recent trends
    - Keep analysis concise
    - Avoid speculative claims
    """,

    backstory="""
    Advanced trend analyst specialized in:
    - AI trends
    - market shifts
    - content opportunities
    - emerging technologies
    """,

    tools=[trend_search_tool],

    llm=moderate_llm,  # qwen2.5:7b

    verbose=False,
    allow_delegation=False,
    max_iter=1,
)
