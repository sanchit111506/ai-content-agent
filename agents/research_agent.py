from crewai import Agent

research_agent = Agent(
    role="Research Analyst",

    goal="""
    Research accurate technical information
    and generate useful research summaries
    """,

    backstory="""
    Technical research specialist focused on:
    - AI
    - DevOps
    - Kubernetes
    - cloud computing
    - cybersecurity
    """,

    llm="ollama/llama3",

    verbose=True
)