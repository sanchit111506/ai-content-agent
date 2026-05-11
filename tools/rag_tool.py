from storage.retriever import search_documents


def rag_search(query):

    results = search_documents(query)

    extracted_text = []

    for r in results:
        extracted_text.append(r.page_content)

    return "\n\n".join(extracted_text)