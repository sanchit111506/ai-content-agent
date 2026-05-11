from crewai import Agent
from crewai.tools import tool

from tools.search_tool import search_web
from tools.rag_tool import rag_search

from llm import ollama_llm


@tool("Web Search Tool")
def web_search_tool(query: str):
    """
    Searches the web for latest information.
    """
    return search_web(query)


@tool("Knowledge Base Search Tool")
def knowledge_base_tool(query: str):
    """
    Searches uploaded PDFs and local knowledge base.
    """
    return rag_search(query)


research_agent = Agent(
    role="Research Specialist",

    goal="""
    Find accurate and latest information from:
    - internet
    - uploaded documents
    - local knowledge base
    """,

    backstory="""
    Expert AI researcher capable of combining:
    - live internet data
    - semantic document search
    - private knowledge base retrieval
    """,

    tools=[
        web_search_tool,
        knowledge_base_tool
    ],

    llm=ollama_llm,

    verbose=True
)