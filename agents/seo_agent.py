from crewai import Agent
from crewai.tools import tool

from tools.search_tool import search_web
from llm import moderate_llm


@tool("SEO Web Research Tool")
def seo_web_search(query: str):
    """
    Search SEO trends, keyword opportunities and optimization strategies.
    """
    return search_web(query)


seo_agent = Agent(
    role="SEO & Content Optimization Specialist",

    goal="""
    Optimize content for SEO and readability.

    Responsibilities:
    - keyword optimization
    - SEO structure
    - readability improvement
    - engagement optimization
    - search visibility

    Rules:
    - Always respond in English only
    - Use proper heading structure
    - Keep SEO natural
    - Avoid keyword stuffing
    - Prioritize readability
    """,

    backstory="""
    Advanced SEO strategist specialized in:
    - Google ranking optimization
    - search intent
    - content structure
    - modern SEO practices
    - technical blogging
    """,

    tools=[seo_web_search],

    llm=moderate_llm,  # qwen2.5:7b

    verbose=False,
    allow_delegation=False,
    max_iter=1,
)
