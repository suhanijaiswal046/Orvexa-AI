"""Document retrieval and grounded RAG answering."""
from pathlib import Path
from langchain_community.vectorstores import FAISS
from src.config import VECTORSTORE_DIR, embeddings, llm
from src.prompts import RAG_PROMPT

def index_exists() -> bool:
    return (VECTORSTORE_DIR / "index.faiss").exists()

def get_vectorstore():
    if not index_exists():
        raise FileNotFoundError("No document index found. Upload documents and click 'Index documents'.")
    return FAISS.load_local(
        str(VECTORSTORE_DIR), embeddings, allow_dangerous_deserialization=True
    )

def answer_from_documents(question: str, k: int = 4) -> dict:
    store = get_vectorstore()
    docs = store.similarity_search(question, k=k)
    if not docs:
        return {"answer": "I could not find relevant information in the indexed company documents.", "sources": []}
    context_parts, sources = [], []
    for doc in docs:
        source = doc.metadata.get("source", doc.metadata.get("file_path", "Unknown source"))
        page = doc.metadata.get("page")
        label = f"{source}" + (f", page {int(page) + 1}" if page is not None else "")
        context_parts.append(f"[Source: {label}]\n{doc.page_content}")
        if label not in sources:
            sources.append(label)
    chain = RAG_PROMPT | llm
    result = chain.invoke({"context": "\n\n---\n\n".join(context_parts), "question": question})
    content = result.content if isinstance(result.content, str) else str(result.content)
    return {"answer": content, "sources": sources}
