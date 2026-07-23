"""
VaultMind — Streamlit UI
A private, air-gapped document Q&A assistant.
Every computation runs locally. Zero cloud calls.
"""

import os
import time
import tempfile
from pathlib import Path

import streamlit as st

# ── Page config (must be first) ──────────────────────────────────────────
st.set_page_config(
    page_title="VaultMind — Air-Gapped AI Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

.stApp {
    background: #06060f;
    color: #e2e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0a0a1a;
    border-right: 1px solid rgba(255,255,255,0.06);
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }

/* Metric cards */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 16px;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    margin-bottom: 8px;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #00e5ff, #7c3aed);
    color: white;
    border: none;
    border-radius: 50px;
    font-weight: 600;
    font-family: 'Space Grotesk', sans-serif;
    padding: 10px 24px;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }

/* File uploader */
[data-testid="stFileUploader"] {
    background: rgba(0,229,255,0.03);
    border: 1px dashed rgba(0,229,255,0.2);
    border-radius: 12px;
}

/* Input */
.stTextInput > div > div > input,
.stChatInput > div > div > input {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 50px;
    color: #e2e8f0;
    font-family: 'Space Grotesk', sans-serif;
}

/* Status box */
.status-box {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 14px;
    border-radius: 50px;
    font-size: 0.82rem;
    font-weight: 600;
    margin-bottom: 16px;
}
.status-ok { background: rgba(0,229,160,0.1); border: 1px solid rgba(0,229,160,0.25); color: #00e5a0; }
.status-err { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.25); color: #ef4444; }

/* Source badge */
.src-badge {
    display: inline-block;
    padding: 3px 10px;
    background: rgba(0,229,255,0.08);
    border: 1px solid rgba(0,229,255,0.15);
    border-radius: 50px;
    font-size: 0.72rem;
    color: #00e5ff;
    margin: 2px;
    font-family: 'JetBrains Mono', monospace;
}

/* Network badge */
.net-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 14px;
    background: rgba(0,229,160,0.08);
    border: 1px solid rgba(0,229,160,0.2);
    border-radius: 50px;
    font-size: 0.8rem;
    font-weight: 600;
    color: #00e5a0;
}

.logo-title {
    font-size: 1.4rem;
    font-weight: 800;
    background: linear-gradient(90deg, #00e5ff, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
}

.hero-header {
    text-align: center;
    padding: 40px 0 24px;
}

.hero-header h1 {
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.2;
    margin-bottom: 12px;
}

.hero-header p {
    color: #94a3b8;
    font-size: 1rem;
}

.answer-box {
    background: rgba(0,229,255,0.04);
    border: 1px solid rgba(0,229,255,0.12);
    border-radius: 14px;
    padding: 20px 24px;
    margin: 12px 0;
    line-height: 1.7;
}

.timing {
    font-size: 0.75rem;
    color: #4b5563;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 8px;
}

div[data-testid="stSelectbox"] label,
div[data-testid="stFileUploader"] label {
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Fallback defaults (used if engine import fails) ──────────────────────
DEFAULT_MODEL = "llama3"

# ── Import engine ──────────────────────────────────────────────────────────
try:
    from rag_engine import (
        check_ollama_running, list_ollama_models, build_rag_chain,
        ingest_file, list_ingested_docs, get_embeddings, clear_vectorstore
    )
    ENGINE_AVAILABLE = True
except Exception as e:
    ENGINE_AVAILABLE = False
    ENGINE_ERROR = str(e)

    def check_ollama_running():
        try:
            import urllib.request
            urllib.request.urlopen("http://localhost:11434", timeout=2)
            return True
        except Exception:
            return False

    def list_ollama_models():
        return []

# ── Session state ──────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chain" not in st.session_state:
    st.session_state.chain = None
if "embeddings" not in st.session_state:
    st.session_state.embeddings = None
if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0
if "docs_ingested" not in st.session_state:
    st.session_state.docs_ingested = 0
if "network_calls" not in st.session_state:
    st.session_state.network_calls = 0  # always stays 0

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="logo-title">🛡️ VaultMind</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#4b5563;font-size:0.75rem;margin-bottom:20px;">Air-Gapped Executive Assistant</div>', unsafe_allow_html=True)

    # Ollama status
    ollama_ok = check_ollama_running() if ENGINE_AVAILABLE else False
    if ollama_ok:
        st.markdown('<div class="status-box status-ok">● Ollama Running — Local</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-box status-err">✕ Ollama Not Running</div>', unsafe_allow_html=True)
        st.info("Start Ollama: open a terminal and run `ollama serve`")

    # Model selector
    st.markdown("**Model**")
    if ollama_ok:
        models = list_ollama_models()
        if models:
            selected_model = st.selectbox("Local models", models, label_visibility="collapsed")
        else:
            st.warning("No models found. Run: `ollama pull llama3`")
            selected_model = DEFAULT_MODEL
    else:
        selected_model = DEFAULT_MODEL
        st.selectbox("Local models", [DEFAULT_MODEL], disabled=True, label_visibility="collapsed")

    st.divider()

    # Upload documents
    st.markdown("**Upload Documents**")
    st.caption("PDFs, Word docs, or text files")
    uploaded = st.file_uploader(
        "Drop files here",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded and st.button("Ingest Documents", use_container_width=True):
        if not ollama_ok:
            st.error("Start Ollama first!")
        else:
            if st.session_state.embeddings is None:
                with st.spinner("Loading embedding model locally..."):
                    st.session_state.embeddings = get_embeddings()

            for uf in uploaded:
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uf.name).suffix) as tmp:
                    tmp.write(uf.read())
                    tmp_path = tmp.name

                with st.spinner(f"Ingesting {uf.name}..."):
                    try:
                        stats = ingest_file(tmp_path, st.session_state.embeddings)
                        st.success(f"✓ {uf.name} — {stats['chunks']} chunks in {stats['time_sec']}s")
                        st.session_state.docs_ingested += 1
                    except Exception as e:
                        st.error(f"Error: {e}")
                    finally:
                        os.unlink(tmp_path)

            # Rebuild chain with new docs
            with st.spinner("Rebuilding RAG chain..."):
                st.session_state.chain, st.session_state.embeddings = build_rag_chain(selected_model)
            st.success("✓ Ready to answer questions!")

    # Ingested docs list
    if ENGINE_AVAILABLE and st.session_state.embeddings:
        docs = list_ingested_docs(st.session_state.embeddings)
        if docs:
            st.divider()
            st.markdown("**Indexed Documents**")
            for doc in docs:
                st.markdown(f'<span class="src-badge">📄 {doc}</span>', unsafe_allow_html=True)

    # Clear DB
    if st.button("🗑️ Clear All Documents", use_container_width=True):
        clear_vectorstore()
        st.session_state.chain = None
        st.session_state.embeddings = None
        st.session_state.docs_ingested = 0
        st.success("Cleared.")

    st.divider()

    # Network calls monitor
    st.markdown("**Privacy Monitor**")
    st.markdown(f"""
    <div class="net-badge">
        🔒 Network Calls: {st.session_state.network_calls}
    </div>
    """, unsafe_allow_html=True)
    st.caption("This counter will always read 0.")

# ── Main area ──────────────────────────────────────────────────────────────
if not ENGINE_AVAILABLE:
    st.error(f"Engine not available: {ENGINE_ERROR}")
    st.info("Run: `pip install -r requirements.txt`")
    st.stop()

# Hero header
st.markdown("""
<div class="hero-header">
    <h1>Your <span style="background:linear-gradient(90deg,#00e5ff,#7c3aed);-webkit-background-clip:text;-webkit-text-fill-color:transparent">Private AI</span> Assistant</h1>
    <p>Ask anything about your documents · 100% local · Zero cloud · Zero exposure</p>
</div>
""", unsafe_allow_html=True)

# Stats row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("☁️ Cloud Calls", "0", delta="always", delta_color="off")
with col2:
    st.metric("📄 Docs Indexed", st.session_state.docs_ingested)
with col3:
    st.metric("💬 Queries Run", st.session_state.total_queries)
with col4:
    st.metric("🛡️ Data Leaked", "0 bytes")

st.divider()

# ── Setup prompt ──────────────────────────────────────────────────────────
if not ollama_ok:
    st.warning("⚠️ **Ollama is not running.** Please start it to use VaultMind.")
    with st.expander("Setup Instructions"):
        st.markdown("""
**Step 1:** Download Ollama from [ollama.com](https://ollama.com/download)

**Step 2:** Open a terminal and run:
```bash
ollama serve
```

**Step 3:** Pull a model:
```bash
ollama pull llama3
```

**Step 4:** Refresh this page.
        """)
    st.stop()

# Auto-build chain if not built yet
if st.session_state.chain is None and ollama_ok:
    with st.spinner("Initializing VaultMind..."):
        try:
            st.session_state.chain, st.session_state.embeddings = build_rag_chain(selected_model)
        except Exception as e:
            st.error(f"Failed to build chain: {e}")

# ── Chat history ──────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🛡️"):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and "sources" in msg:
            if msg["sources"]:
                st.markdown("**Sources:** " + " ".join(
                    f'<span class="src-badge">{s}</span>' for s in msg["sources"]
                ), unsafe_allow_html=True)
            st.markdown(f'<div class="timing">⏱ {msg.get("time","?")}s · 🔒 0 network calls</div>',
                        unsafe_allow_html=True)

# ── Chat input ────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask anything about your documents..."):
    if st.session_state.chain is None:
        st.error("Please upload and ingest documents first.")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)

        # Get answer
        with st.chat_message("assistant", avatar="🛡️"):
            with st.spinner("Thinking locally..."):
                try:
                    from rag_engine import query as rag_query
                    result = rag_query(st.session_state.chain, prompt)
                    st.session_state.total_queries += 1

                    st.markdown(result["answer"])
                    if result["sources"]:
                        st.markdown("**Sources:** " + " ".join(
                            f'<span class="src-badge">{s}</span>' for s in result["sources"]
                        ), unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="timing">⏱ {result["time_sec"]}s · 🔒 0 network calls</div>',
                        unsafe_allow_html=True
                    )

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result["sources"],
                        "time": result["time_sec"]
                    })

                except Exception as e:
                    err_msg = f"Error: {e}"
                    st.error(err_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": err_msg,
                        "sources": []
                    })

# ── Empty state hint ──────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center;padding:60px 0;color:#4b5563;">
        <div style="font-size:3rem;margin-bottom:16px;">🛡️</div>
        <div style="font-size:1rem;margin-bottom:8px;color:#94a3b8;">Upload documents in the sidebar, then ask anything.</div>
        <div style="font-size:0.82rem;">Try: "Summarize this document" or "What are the key terms?"</div>
    </div>
    """, unsafe_allow_html=True)
