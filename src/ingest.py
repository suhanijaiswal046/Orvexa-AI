"""Load and index local company documents into FAISS."""
from pathlib import Path
from typing import Iterable
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from src.config import DATA_DIR, VECTORSTORE_DIR, embeddings

SUPPORTED = {".pdf", ".txt", ".md"}

def load_documents(paths: Iterable[str | Path] | None = None):
    docs = []
    candidates = [Path(p) for p in paths] if paths else list(DATA_DIR.glob("*"))
    for path in candidates:
        if not path.is_file() or path.suffix.lower() not in SUPPORTED:
            continue
        if path.suffix.lower() == ".pdf":
            loaded = PyPDFLoader(str(path)).load()
        else:
            loaded = TextLoader(str(path), encoding="utf-8", autodetect_encoding=True).load()
        for doc in loaded:
            doc.metadata["source"] = path.name
        docs.extend(loaded)
    return docs

def build_index(paths: Iterable[str | Path] | None = None, append: bool = False):
    docs = load_documents(paths)
    if not docs:
        raise ValueError("No supported documents found. Upload PDF, TXT, or MD files.")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=120,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(docs)
    VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
    if append and (VECTORSTORE_DIR / "index.faiss").exists():
        store = FAISS.load_local(
            str(VECTORSTORE_DIR), embeddings, allow_dangerous_deserialization=True
        )
        store.add_documents(chunks)
    else:
        store = FAISS.from_documents(chunks, embeddings)
    store.save_local(str(VECTORSTORE_DIR))
    return len(chunks)

if __name__ == "__main__":
    count = build_index()
    print(f"Indexed {count} chunks into {VECTORSTORE_DIR}")
