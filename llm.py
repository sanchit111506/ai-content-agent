from crewai import LLM

ollama_llm = LLM(
    model="ollama/qwen2.5",
    base_url="http://localhost:11434"
)