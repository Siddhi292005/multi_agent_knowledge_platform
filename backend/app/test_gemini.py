from rag.generator import get_llm

llm = get_llm()

prompt = """Answer the question using only the context below.

Question:
Why do remote employees need to connect to the company VPN?

Context:
VPN Access:
Employees working remotely must connect to the company VPN to access internal systems.

IT Support:
Employees can contact the IT help desk for technical issues.

Give the answer directly.
"""

response = llm.invoke(prompt)

print(response.content)
