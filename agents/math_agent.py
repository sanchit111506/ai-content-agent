from crewai import Agent
from crewai.tools import tool

from tools.search_tool import search_web
from llm import moderate_llm


@tool("Math and Science Research Tool")
def math_research_tool(query: str):
    """
    Research mathematics and science concepts.
    """
    return search_web(query)


math_agent = Agent(
    role="Mathematics and Science Specialist",

    goal="""
    Solve mathematical and scientific problems accurately.

    Responsibilities:
    - mathematics
    - calculus
    - algebra
    - statistics
    - physics
    - engineering concepts

    Rules:
    - Always respond in English only
    - Use step-by-step explanations
    - Use formulas where appropriate
    - Keep explanations educational
    - Avoid overly verbose output
    """,

    backstory="""
    Advanced AI mathematician and scientist
    specialized in technical education,
    scientific reasoning and engineering analysis.
    """,

    tools=[math_research_tool],

    llm=moderate_llm,  # qwen2.5:7b

    verbose=False,
    allow_delegation=False,
    max_iter=1,
)
