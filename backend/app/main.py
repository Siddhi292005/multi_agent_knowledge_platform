
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from database import get_connection

from rag.loader import load_documents
from rag.chunker import split_documents
from rag.vector_store import (
    create_domain_vector_stores,
    retrieve_with_scores,
    calculate_retrieval_confidence
)
from rag.generator import get_llm
from rag.router import route_question


app = FastAPI(title="Enterprise Knowledge Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Load documents and create domain-specific vector stores
documents = load_documents("data/documents")
chunks = split_documents(documents)

domain_vector_stores = create_domain_vector_stores(chunks)

llm = get_llm()


class ChatRequest(BaseModel):
    question: str


def save_conversation(
    question,
    answer,
    agent,
    confidence,
    escalated,
    sources
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO conversations
        (question, answer, agent, confidence, escalated, sources)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            question,
            answer,
            agent,
            confidence,
            escalated,
            sources
        )
    )

    connection.commit()
    cursor.close()
    connection.close()


@app.get("/")
def root():
    return {
        "message": "Enterprise Knowledge Platform API is running"
    }

@app.get("/conversations")
def get_conversations():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            question,
            answer,
            agent,
            confidence,
            escalated,
            sources,
            created_at
        FROM conversations
        ORDER BY created_at DESC
        LIMIT 20
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    conversations = []

    for row in rows:
        conversations.append({
            "id": row[0],
            "question": row[1],
            "answer": row[2],
            "agent": row[3],
            "confidence": row[4],
            "escalated": row[5],
            "sources": row[6],
            "created_at": row[7]
        })

    return {
        "conversations": conversations
    }

@app.post("/chat")
def chat(request: ChatRequest):

    # Step 1: Route the question
    agent = route_question(request.question)

    if agent == "unknown":

        answer = "I am not sure which department can answer this question."

        save_conversation(
            request.question,
            answer,
            "unknown",
            0.0,
            True,
            []
        )

        return {
            "question": request.question,
            "agent": "unknown",
            "answer": answer,
            "confidence": 0.0,
            "escalated": True,
            "sources": []
        }

    # Step 2: Select the vector store for the routed agent
    vector_store = domain_vector_stores[agent]

    # Step 3: Retrieve documents only from the selected domain
    results = retrieve_with_scores(
        vector_store,
        request.question,
        k=2
    )

    agent_documents = results

    # No document found for the selected agent
    if not agent_documents:

        answer = "I do not have enough information to answer this."

        save_conversation(
            request.question,
            answer,
            agent,
            0.0,
            True,
            []
        )

        return {
            "question": request.question,
            "agent": agent,
            "answer": answer,
            "confidence": 0.0,
            "escalated": True,
            "sources": []
        }

    # Step 4: Use the best matching document
    best_document, best_distance = min(
        agent_documents,
        key=lambda item: float(item[1])
    )

    best_distance = float(best_distance)

    confidence = calculate_retrieval_confidence(best_distance)

    # Step 5: Escalate low-confidence questions
    
    # Step 6: Build context from retrieved documents
    context = "\n\n".join(
        document.page_content
        for document, distance in agent_documents
    )
    print("\n===== RETRIEVED CONTEXT =====")
    print(context)
    print("=============================\n")
    # Step 7: Generate answer using RAG
    prompt = f"""
You are the {agent.upper()} department knowledge assistant.

Your task is to answer the user's question using the information in the
CONTEXT below.

IMPORTANT RULES:
1. Use the CONTEXT as the source of truth.
2. If the CONTEXT directly answers the question, answer it directly.
3. Do not say that you lack information when the answer is present in the CONTEXT.
4. Do not add information that is not present in the CONTEXT.
5. If the answer truly cannot be found in the CONTEXT, respond exactly:
"I do not have enough information to answer this."

USER QUESTION:
{request.question}

CONTEXT:
{context}

ANSWER:
"""

    response = llm.invoke(prompt)

    if isinstance(response.content, list):
        answer = "".join(
            block["text"]
            for block in response.content
            if block.get("type") == "text"
        )
    else:
        answer = response.content

    # Step 8: Collect sources
    sources = list({
        document.metadata["source"]
        for document, distance in agent_documents
    })

    # Step 9: Save successful conversation to PostgreSQL
    save_conversation(
        request.question,
        answer,
        agent,
        confidence,
        False,
        sources
    )

    # Step 10: Return response
    return {
        "question": request.question,
        "agent": agent,
        "answer": answer,
        "confidence": confidence,
        "escalated": False,
        "sources": sources
    }

