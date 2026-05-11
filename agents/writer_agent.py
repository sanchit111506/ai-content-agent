from crewai import Agent
from llm import ollama_llm


writer_agent = Agent(
    role="AI Content Writer",

    goal="""
    Generate high quality engaging SEO optimized content
    """,

    backstory="""
    Expert content writer specialized in:
    - blogs
    - technical articles
    - YouTube scripts
    - AI content
    """,

    llm=ollama_llm,

    verbose=True
)