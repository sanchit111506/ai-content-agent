from crewai import Agent
from llm import ollama_llm


seo_agent = Agent(
    role="SEO Optimization Specialist",

    goal="""
    Optimize content for SEO, readability,
    engagement and keyword optimization.
    """,

    backstory="""
    Expert SEO strategist and content optimizer.
    """,

    llm=ollama_llm,

    verbose=True
)