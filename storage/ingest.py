from storage.document_loader import load_pdf
from storage.vector_store import store_documents


def ingest_pdf(file_path):

    print(f"Loading PDF: {file_path}")

    chunks = load_pdf(file_path)

    print(f"Chunks created: {len(chunks)}")

    store_documents(chunks)

    print("Embeddings stored successfully!")

    return {
        "status": "success",
        "chunks": len(chunks)
    }