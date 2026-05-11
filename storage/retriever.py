from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings


embedding = OllamaEmbeddings(
    model="nomic-embed-text"
)


def search_documents(query):

    db = Chroma(
        persist_directory="storage/chroma_db",
        embedding_function=embedding
    )

    results = db.similarity_search(query, k=3)

    return results