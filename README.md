# 🛡️ VaultMind — Air-Gapped Privacy-First Executive Assistant

A 100% local, air-gapped RAG (Retrieval-Augmented Generation) executive assistant designed for processing confidential documents with **zero cloud calls**, **zero network latency**, and **zero data leakage**.

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-LCEL-green.svg)
![Ollama](https://img.shields.io/badge/LLM-LLaMA%203%20(Local)-orange.svg)
![VectorDB](https://img.shields.io/badge/VectorDB-ChromaDB-purple.svg)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)

---

## 🌟 Key Features

- **🔒 100% On-Device & Air-Gapped:** Zero external API dependencies (No OpenAI, No Anthropic, No Cloud). All computation happens locally.
- **📄 Multi-Format Document Ingestion:** Supports indexing PDFs, Microsoft Word (.docx), and Plain Text (.txt) files into a local vector store.
- **⚡ Local Embedding & Vector Search:** Uses `all-MiniLM-L6-v2` via SentenceTransformers for fast, high-accuracy semantic document search with ChromaDB.
- **🤖 On-Device LLM Inference:** Powered by **LLaMA 3** running via Ollama locally, optimized for consumer GPU hardware (NVIDIA RTX 3050).
- **🛡️ Real-Time Privacy Monitor:** Live sidebar counter guaranteeing `0 Network Calls` and tracking local document metrics.
- **📌 Source Attribution:** Every response cites exact source document names and page numbers used to generate the answer.

---

## 🏗️ System Architecture

```
[ User Upload (PDF/DOCX/TXT) ] 
             │
             ▼
[ Document Loader & Text Splitter ] ── (RecursiveCharacterTextSplitter)
             │
             ▼
[ Local Embedding Model ] ─────────── (SentenceTransformers all-MiniLM-L6-v2)
             │
             ▼
[ Local Vector Store ] ────────────── (ChromaDB - On Disk)
             │
             ▼
[ LCEL Retrieval Chain ] ──────────── (LangChain Expression Language)
             │
             ▼
[ Local LLM Engine ] ──────────────── (Ollama / LLaMA 3 on GPU)
             │
             ▼
[ Streamlit Dashboard ] ───────────── (Privacy Monitor + Source Citing UI)
```

---

## 🚀 Getting Started

### Prerequisites

1. **Python 3.10+**
2. **Ollama**: Download and install from [ollama.com](https://ollama.com/)

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gaurish1811/VaultMind-AirGapped-Assistant.git
   cd VaultMind-AirGapped-Assistant/app
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Pull the LLaMA 3 model locally:**
   ```bash
   ollama pull llama3
   ```

4. **Launch the Streamlit UI:**
   ```bash
   python -m streamlit run main.py
   ```

5. Open your browser at `http://localhost:8501`.

---

## 🛠️ Tech Stack

- **Framework:** LangChain (LCEL)
- **Vector Database:** ChromaDB
- **Embedding Model:** SentenceTransformers (`all-MiniLM-L6-v2`)
- **Local LLM Runner:** Ollama (LLaMA 3)
- **Frontend / UI:** Streamlit
- **Language:** Python 3.12

---

## 📜 Resume Highlights

- Built a production-ready, air-gapped RAG AI assistant processing enterprise documents with 0 network calls and 0 cloud data leakage.
- Implemented LangChain LCEL pipelines connected to a local ChromaDB vector store and LLaMA 3 running on-device.
- Optimized local GPU inference using Ollama on an NVIDIA RTX 3050 laptop GPU for real-time document Q&A.
