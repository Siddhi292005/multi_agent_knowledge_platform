from rag.loader import load_documents
from rag.chunker import split_documents


documents = load_documents("data/documents")

print("Documents loaded:", len(documents))

chunks = split_documents(documents)

print("Chunks created:", len(chunks))

for i, chunk in enumerate(chunks):
    print(f"\n--- Chunk {i + 1} ---")
    print(chunk.page_content)
    print("Source:", chunk.metadata["source"])