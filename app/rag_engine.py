"""
VaultMind — Core RAG Engine
Handles document ingestion, embedding, and retrieval entirely locally.
No data ever leaves this machine.
"""

import os
import time
from pathlib import Path
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser

# ── Config ──────────────────────────────────────────────────────────────────
CHROMA_DB_PATH = "./vaultmind_db"
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3"
EMBED_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

SYSTEM_PROMPT = """You are VaultMind, a 100% private, air-gapped executive AI assistant.
Your job is to assist the user by answering their questions using the provided document context whenever relevant.

Instructions:
1. If the question relates to the uploaded documents, use the provided Context to answer accurately.
2. If the user asks general questions, system/privacy questions (e.g. "Is my data private?"), or conversational greetings, answer them helpfully as VaultMind, ensuring them that all computations and data stay strictly on their local machine.
3. Be concise, professional, clear, and helpful.

Context:
{context}

Question: {question}

Answer:"""


# ── Embeddings (local, no API) ────────────────────────────────────────────
def get_embeddings():
    return SentenceTransformerEmbeddings(model_name=EMBED_MODEL)


# ── Document Loaders ─────────────────────────────────────────────────────
def load_document(file_path: str):
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path, encoding="utf-8")
    elif ext in [".docx", ".doc"]:
        loader = Docx2txtLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    return loader.load()


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return splitter.split_documents(documents)


# ── Vector Store ─────────────────────────────────────────────────────────
def get_vectorstore(embeddings):
    return Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=embeddings,
        collection_name="vaultmind_docs"
    )


def ingest_file(file_path: str, embeddings) -> dict:
    start = time.time()
    docs = load_document(file_path)
    chunks = split_documents(docs)
    vectorstore = get_vectorstore(embeddings)
    vectorstore.add_documents(chunks)
    elapsed = round(time.time() - start, 2)
    return {
        "file": Path(file_path).name,
        "pages": len(docs),
        "chunks": len(chunks),
        "time_sec": elapsed,
        "network_calls": 0
    }


def list_ingested_docs(embeddings) -> List[str]:
    try:
        vectorstore = get_vectorstore(embeddings)
        collection = vectorstore._collection
        results = collection.get()
        sources = set()
        for meta in results.get("metadatas", []):
            if meta and "source" in meta:
                sources.add(Path(meta["source"]).name)
        return sorted(list(sources))
    except Exception:
        return []


def clear_vectorstore():
    import shutil
    if os.path.exists(CHROMA_DB_PATH):
        shutil.rmtree(CHROMA_DB_PATH)


# ── RAG Chain (LCEL — modern LangChain) ──────────────────────────────────
def build_rag_chain(model_name: str = DEFAULT_MODEL):
    embeddings = get_embeddings()
    vectorstore = get_vectorstore(embeddings)
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )

    llm = OllamaLLM(
        model=model_name,
        base_url=OLLAMA_BASE_URL,
        temperature=0.1,
    )

    prompt = PromptTemplate(
        template=SYSTEM_PROMPT,
        input_variables=["context", "question"]
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Modern LCEL chain — retrieves docs then passes to LLM
    rag_chain = (
        RunnableParallel(
            context=(retriever | format_docs),
            question=RunnablePassthrough(),
            source_docs=retriever
        )
    )

    return {"chain": rag_chain, "llm": llm, "prompt": prompt}, embeddings


def query(chain_bundle, question: str) -> dict:
    start = time.time()

    rag_chain = chain_bundle["chain"]
    llm = chain_bundle["llm"]
    prompt = chain_bundle["prompt"]

    # Get context + source docs
    retrieved = rag_chain.invoke(question)
    context = retrieved["context"]
    source_docs = retrieved["source_docs"]

    # Format prompt and run LLM
    formatted_prompt = prompt.format(context=context, question=question)
    answer = llm.invoke(formatted_prompt)

    elapsed = round(time.time() - start, 2)

    # Extract source names
    sources = []
    for doc in source_docs:
        src = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "")
        label = Path(src).name
        if page != "":
            label += f" (page {int(page)+1})"
        if label not in sources:
            sources.append(label)

    return {
        "answer": str(answer).strip(),
        "sources": sources,
        "time_sec": elapsed,
        "network_calls": 0
    }


# ── Ollama health check ───────────────────────────────────────────────────
def check_ollama_running() -> bool:
    try:
        import urllib.request
        urllib.request.urlopen(OLLAMA_BASE_URL, timeout=2)
        return True
    except Exception:
        return False


def list_ollama_models() -> List[str]:
    try:
        import json, urllib.request
        with urllib.request.urlopen(f"{OLLAMA_BASE_URL}/api/tags", timeout=3) as r:
            data = json.loads(r.read())
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []
