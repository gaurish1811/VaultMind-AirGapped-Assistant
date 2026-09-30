# 🛡️ VaultMind — Air-Gapped Privacy-First Executive Assistant

[![CI](https://github.com/gaurish1811/VaultMind-AirGapped-Assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/gaurish1811/VaultMind-AirGapped-Assistant/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-LCEL-green.svg)
![LLM](https://img.shields.io/badge/LLM-LLaMA%203%20%28Local%29-orange.svg)
![VectorDB](https://img.shields.io/badge/VectorDB-ChromaDB-purple.svg)
![Privacy](https://img.shields.io/badge/Network%20Calls-0-brightgreen.svg)
![Air-Gapped](https://img.shields.io/badge/Air--Gapped-100%25%20Offline-red.svg)

> **Your data. Your hardware. Zero cloud. Complete sovereignty.**

A 100% local, air-gapped RAG (Retrieval-Augmented Generation) executive assistant that lets you ask natural language questions about your confidential documents — with **zero cloud calls, zero data leakage, and zero external API dependencies**.

---

## 🌟 Why VaultMind?

Most AI assistants (ChatGPT, Claude, Gemini) send your documents to external servers. For **legal firms, healthcare providers, C-suite executives, and defense contractors**, that's a compliance violation. VaultMind processes everything on-device — your data never leaves your machine.

| Feature | VaultMind | Cloud AI (ChatGPT etc.) |
|---|---|---|
| Data leaves your machine | ❌ Never | ✅ Always |
| Works offline / air-gapped | ✅ Yes | ❌ No |
| HIPAA / privilege safe | ✅ Yes | ❌ No |
| API cost per query | ✅ $0 | ❌ Paid |
| Source attribution | ✅ Page-level | ⚠️ Varies |

---

## 🌟 Key Features

- **🔒 100% On-Device & Air-Gapped** — Zero external API dependencies. All computation happens locally.
- **📄 Multi-Format Document Ingestion** — PDF, Microsoft Word (.docx), and Plain Text (.txt)
- **⚡ Local Embedding & Vector Search** — `all-MiniLM-L6-v2` via SentenceTransformers + ChromaDB
- **🤖 On-Device LLM Inference** — LLaMA 3 via Ollama, optimized for consumer GPU (RTX 3050)
- **🛡️ Real-Time Privacy Monitor** — Live sidebar counter guaranteeing `0 Network Calls`
- **📌 Source Attribution** — Every answer cites exact document name and page number

---

## 🏗️ System Architecture

```
[ User Upload (PDF / DOCX / TXT) ]
              │
              ▼
[ RecursiveCharacterTextSplitter ]  chunk_size=800, overlap=100
              │
              ▼
[ SentenceTransformers all-MiniLM-L6-v2 ]  (local, no API)
              │
              ▼
[ ChromaDB Vector Store ]  ─────────  On-disk at ./vaultmind_db
              │
              ▼
[ LCEL Retrieval Chain ]  ──────────  RunnableParallel (context + source_docs)
              │
              ▼
[ OllamaLLM — LLaMA 3 ]  ──────────  localhost:11434, temperature=0.1
              │
              ▼
[ Streamlit UI ]  ──────────────────  Chat + Privacy Monitor + Source Badges
```

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| **Orchestration** | LangChain (LCEL) | RAG pipeline composition |
| **Vector DB** | ChromaDB | Local on-disk embedding storage |
| **Embedding Model** | `all-MiniLM-L6-v2` | 384-dim local text embeddings |
| **LLM Runner** | Ollama | Local LLM inference |
| **LLM Model** | LLaMA 3 (7B Q4) | Question answering |
| **UI** | Streamlit | Chat interface + privacy dashboard |
| **Document Loaders** | PyPDFLoader, Docx2txtLoader, TextLoader | Multi-format ingestion |

---

## 🚀 Getting Started

### Prerequisites
1. **Python 3.10+**
2. **Ollama** — Download from [ollama.com](https://ollama.com/)

### Installation

```bash
git clone https://github.com/gaurish1811/VaultMind-AirGapped-Assistant.git
cd VaultMind-AirGapped-Assistant/app
pip install -r requirements.txt
```

### Pull the local LLM
```bash
ollama pull llama3
```

### Launch
```bash
python -m streamlit run main.py
```
Open **`http://localhost:8501`**

---

## 📊 Performance

| Metric | Value |
|---|---|
| Embedding Model | `all-MiniLM-L6-v2` (~90 MB) |
| LLM Size on Disk | ~4 GB (LLaMA 3 7B @ 4-bit quantization) |
| GPU Required | NVIDIA RTX 3050 (4 GB VRAM) — consumer-grade |
| Chunk Size | 800 characters, 100 overlap |
| Retrieval | Top-5 chunks by cosine similarity |
| Network Calls (inference) | **0** |

---

## 🏭 Built For

| Industry | Use Case |
|---|---|
| ⚖️ **Legal** | Contract analysis, case law search — attorney-client privilege preserved |
| 🏥 **Healthcare** | Patient record Q&A — HIPAA-compliant by architecture |
| 🏛️ **C-Suite** | Sensitive email triage, board prep — zero exposure surface |
| 🛡️ **Defense** | Classified document QA — SCIF-compatible, fully air-gapped |
| 💰 **Finance** | P&L analysis, contracts — data never leaves your device |

---

## 📜 Resume Highlights

- Built a production-ready, air-gapped RAG AI assistant with 0 network calls and 0 cloud data leakage
- Implemented LangChain LCEL pipelines with `RunnableParallel` for simultaneous retrieval and source attribution
- Optimized local GPU inference using Ollama + LLaMA 3 on NVIDIA RTX 3050 for real-time document Q&A
- Persistent ChromaDB vector store with multi-format document ingestion (PDF, DOCX, TXT)
