from rag.loader import load_documents
from rag.chunker import split_documents
from rag.vector_store import create_vector_store
from rag.generator import get_llm


# 1. Load documents
documents = load_documents("data/documents")

# 2. Split documents into chunks
chunks = split_documents(documents)

# 3. Create FAISS vector store
vector_store = create_vector_store(chunks)

# 4. Create Gemini LLM
llm = get_llm()


# 5. User question
query = "How many days of sick leave do employees get?"


# 6. Retrieve relevant chunks
results = vector_store.similarity_search(
    query,
    k=2
)


# 7. Build context from retrieved chunks
context = "\n\n".join(
    document.page_content
    for document in results
)


# 8. Ask Gemini to answer using only retrieved context
prompt = f"""
You are an enterprise knowledge assistant.

Answer the user's question using ONLY the provided context.

If the answer cannot be found in the context, say:
"I do not have enough information to answer this."

User question:
{query}

Context:
{context}

Give a concise answer.
"""


# 9. Generate answer
response = llm.invoke(prompt)


# 10. Display answer
print("\n--- Answer ---")
if isinstance(response.content, list):
    answer = "".join(
        block["text"]
        for block in response.content
        if block.get("type") == "text"
    )
else:
    answer = response.content

print(answer)

# 11. Display sources
print("\n--- Sources ---")

sources = set()

for document in results:
    sources.add(document.metadata["source"])

for source in sources:
    print(source)