from pathlib import Path
from langchain_core.documents import Document


def load_documents(directory: str):
    documents = []

    for file_path in Path(directory).glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": file_path.name
                }
            )
        )

    return documents