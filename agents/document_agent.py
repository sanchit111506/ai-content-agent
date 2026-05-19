from crewai import Agent
from crewai.tools import tool

from tools.rag_tool import rag_search
from llm import moderate_llm


@tool("Document Analysis Tool")
def document_analysis_tool(query: str):
    """
    Analyze uploaded documents and retrieve relevant information.
    """
    return rag_search(query)


document_agent = Agent(
    role="Document Intelligence Specialist",

    goal="""
    Analyze uploaded documents accurately.

    Responsibilities:
    - PDF analysis
    - report summarization
    - semantic extraction
    - document understanding

    Rules:
    - Always respond in English only
    - Keep summaries concise
    - Extract important information clearly
    - Avoid unnecessary verbosity
    """,

    backstory="""
    Advanced document intelligence system
    specialized in enterprise document analysis,
    PDF understanding
    and semantic extraction.
    """,

    tools=[document_analysis_tool],

    llm=moderate_llm,  # qwen2.5:7b

    verbose=False,
    allow_delegation=False,
    max_iter=1,
)
