from crewai import Agent
from crewai.tools import tool

from tools.rag_tool import rag_search
from llm import moderate_llm


@tool("RAG Knowledge Base Tool")
def rag_knowledge_tool(query: str):
    """
    Retrieve semantic knowledge from uploaded documents.
    """
    return rag_search(query)


rag_agent = Agent(
    role="RAG Knowledge Specialist",

    goal="""
    Retrieve accurate information from uploaded documents.

    Responsibilities:
    - semantic search
    - document retrieval
    - contextual understanding
    - knowledge extraction

    Rules:
    - Always respond in English only
    - Use retrieved context carefully
    - Avoid hallucinations
    - Prefer concise factual answers
    """,

    backstory="""
    Advanced Retrieval-Augmented Generation specialist
    focused on vector search,
    semantic retrieval
    and document intelligence.
    """,

    tools=[rag_knowledge_tool],

    llm=moderate_llm,  # qwen2.5:7b

    verbose=False,
    allow_delegation=False,
    max_iter=1,
)
