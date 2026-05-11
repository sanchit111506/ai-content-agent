from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings


embedding = OllamaEmbeddings(
    model="nomic-embed-text"
)


def store_documents(chunks):

    db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory="storage/chroma_db"
    )

    db.persist()

    return db