from rag.loader import load_documents
from rag.chunker import split_documents
from rag.vector_store import create_vector_store

documents = load_documents("data/documents")
chunks=split_documents(documents)
vector_store=create_vector_store(chunks)

query = "How much medical time off is an employee allowed?"
results=vector_store.similarity_search(query, k=1)

for result in results:
    print("\n--- Retrieved Chunk ---")
    print(result.page_content)
    print("\nSource:", result.metadata["source"])
