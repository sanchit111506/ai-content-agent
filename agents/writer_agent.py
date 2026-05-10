from crewai import Agent

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

    llm="ollama/llama3",

    verbose=True
)