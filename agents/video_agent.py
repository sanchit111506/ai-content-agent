from crewai import Agent


video_agent = Agent(
    role="AI Video Creator",

    goal="""
    Create engaging video scripts, scene ideas,
    narration flow, and visual storytelling content.
    """,

    backstory="""
    You are an expert AI video production specialist
    who creates:
    - YouTube videos
    - shorts
    - reels
    - educational videos
    - cinematic storytelling
    """,

    llm="ollama/llama3",

    verbose=True
)