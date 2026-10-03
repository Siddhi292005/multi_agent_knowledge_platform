from rag.loader import load_documents
from rag.chunker import split_documents
from rag.vector_store import (
    create_domain_vector_stores,
    retrieve_with_scores,
    calculate_retrieval_confidence
)


documents = load_documents("data/documents")
chunks = split_documents(documents)

domain_vector_stores = create_domain_vector_stores(chunks)

it_store = domain_vector_stores["it"]

query = "How do I reset my password?"

results = retrieve_with_scores(
    it_store,
    query,
    k=2
)

for document, score in results:

    confidence = calculate_retrieval_confidence(score)

    print("\n--- Document ---")
    print(document.page_content)

    print("\nSource:", document.metadata["source"])
    print("Distance:", score)
    print("Confidence:", confidence)