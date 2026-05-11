import os

from storage.document_loader import load_pdf
from storage.vector_store import store_documents
from storage.retriever import search_documents


DOCUMENTS_PATH = "storage/documents"


all_chunks = []

# Load all PDFs automatically
for file in os.listdir(DOCUMENTS_PATH):

    if file.endswith(".pdf"):

        file_path = os.path.join(DOCUMENTS_PATH, file)

        print(f"Loading PDF: {file}")

        chunks = load_pdf(file_path)

        all_chunks.extend(chunks)


# Store all chunks
store_documents(all_chunks)

print("Documents stored successfully!")

# Test semantic search
results = search_documents(
    "What does the document talk about?"
)

print("\nSearch Results:\n")

for r in results:
    print(r.page_content)
    print("\n-----------------\n")