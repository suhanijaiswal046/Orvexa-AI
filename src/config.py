"""Shared LLM, embeddings, and project paths."""
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError("GROQ_API_KEY missing. Add it to the project-root .env file.")

MODEL_NAME = os.getenv("GROQ_MODEL", "qwen/qwen3-32b")
llm = ChatGroq(
    model=MODEL_NAME,
    temperature=0.2,
    api_key=GROQ_API_KEY,
)

# Local embeddings: no separate embedding API key is required.
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

DATA_DIR = ROOT_DIR / "data"
UPLOAD_DIR = ROOT_DIR / "uploads"
VECTORSTORE_DIR = ROOT_DIR / "vectorstore"
DB_PATH = ROOT_DIR / "nexora.db"
