from crewai import Agent

from llm import moderate_llm


# Same fix as file_conversion_agent:
# Removed the placeholder @tool to avoid phi3:mini's tool-incompatibility,
# and switched to qwen2.5:7b which handles instructional agent tasks well.

image_processing_agent = Agent(
    role="Image Processing Specialist",

    goal="""
    Guide users through image optimization workflows.

    Responsibilities:
    - resizing
    - compression
    - format conversion (PNG, JPG, WebP, AVIF)
    - thumbnail generation
    - quality preservation

    Rules:
    - Always respond in English only
    - Maintain image quality awareness
    - Keep responses concise
    - Use code/CLI examples when helpful
    """,

    backstory="""
    AI image optimization specialist focused on performance,
    quality preservation and responsive media workflows.
    """,

    tools=[],

    llm=moderate_llm,  # qwen2.5:7b

    verbose=False,
    allow_delegation=False,
    max_iter=1,
)
