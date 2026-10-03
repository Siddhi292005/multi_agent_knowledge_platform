from rag.embeddings import get_embeddings


embeddings = get_embeddings()

text = "Employees are entitled to 10 days of sick leave."

vector = embeddings.embed_query(text)

print("Vector length:", len(vector))
print("First 10 values:", vector[:10])