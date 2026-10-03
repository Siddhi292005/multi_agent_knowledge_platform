from rag.router import route_question


questions = [
    "How many sick leave days do I get?",
    "How do I reset my password?",
    "Can I work from home?",
    "What are the office hours?",
    "My account is locked. What should I do?",
    "What is the manager approval rule for leave?"
]


for question in questions:
    route = route_question(question)

    print(f"Question: {question}")
    print(f"Route: {route}")
    print()