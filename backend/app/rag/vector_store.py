from langchain_community.vectorstores import FAISS
from app.rag.embeddings import get_embeddings


def create_vector_store(chunks):
    embeddings = get_embeddings()

    vector_store = FAISS.from_documents(
        chunks,
        embeddings
    )

    return vector_store


def retrieve_with_scores(vector_store, query, k=2):
    return vector_store.similarity_search_with_score(
        query,
        k=k
    )


def calculate_retrieval_confidence(distance):
    confidence = 1 / (1 + distance)
    return round(confidence, 2)


def create_domain_vector_stores(chunks):
    embeddings = get_embeddings()

    domain_chunks = {
        "hr": [],
        "it": [],
        "policy": []
    }

    for chunk in chunks:
        source = chunk.metadata.get("source")

        if source == "hr_policy.txt":
            domain_chunks["hr"].append(chunk)

        elif source == "it_support.txt":
            domain_chunks["it"].append(chunk)

        elif source == "company_policies.txt":
            domain_chunks["policy"].append(chunk)

    vector_stores = {}

    for domain, domain_documents in domain_chunks.items():

        if domain_documents:
            vector_stores[domain] = FAISS.from_documents(
                domain_documents,
                embeddings
            )

    return vector_stores