from crewai import Agent

from llm import moderate_llm


# NOTE: We removed the @tool function because:
# 1. The "tool" was just returning a hardcoded string — it didn't do
#    actual file conversion.
# 2. phi3:mini doesn't support CrewAI tool-calling, which caused
#    "phi3:mini does not support tools" errors.
# 3. qwen2.5:7b can answer conversion questions perfectly without a tool.
#
# If you later add a REAL file-conversion implementation
# (python-docx + LibreOffice CLI etc.), put it back and keep this on
# qwen2.5:7b — never on phi3:mini.

file_conversion_agent = Agent(
    role="File Conversion Specialist",

    goal="""
    Guide users through document conversion workflows.

    Responsibilities:
    - Explain conversion options (PDF, DOCX, XLSX)
    - Recommend best tools for the job
    - Describe formatting preservation steps
    - Clear, step-by-step guidance

    Rules:
    - Always respond in English only
    - Keep responses concise
    - Use markdown lists when helpful
    """,

    backstory="""
    Document processing specialist focused on structured file conversion,
    office document workflows and enterprise document automation.
    """,

    tools=[],  # ← no tools — keeps it compatible with any model

    llm=moderate_llm,  # qwen2.5:7b — supports any agent behaviour

    verbose=False,
    allow_delegation=False,
    max_iter=1,
)
