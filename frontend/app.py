"""Professional Streamlit UI for Nexora AI."""
import sys
import uuid
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import UPLOAD_DIR
from src.ingest import build_index
from src.rag_chain import index_exists
from src.graph import ask
from src.database import init_db, list_tickets

st.set_page_config(
    page_title="ORVEXA AI | Company Intelligence",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------- Session state ---------------------------
defaults = {
    "thread_id": str(uuid.uuid4()),
    "chat": [],
    "csv_path": None,
    "page": "Dashboard",
    "total_queries": 0,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --------------------------- Styling ---------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { --nx-bg:#0b1020; --nx-panel:#111a2e; --nx-panel2:#17223a; --nx-border:rgba(148,163,184,.16); --nx-text:#edf2ff; --nx-muted:#94a3b8; --nx-accent:#8b7cff; --nx-cyan:#4fd1c5; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background: radial-gradient(circle at 12% 0%, rgba(91,75,190,.17), transparent 27%), radial-gradient(circle at 95% 10%, rgba(35,169,177,.10), transparent 24%), var(--nx-bg); color:var(--nx-text); }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#10182b 0%,#0d1425 100%); border-right:1px solid var(--nx-border); }
[data-testid="stSidebar"] * { color:var(--nx-text); }
h1,h2,h3 { font-family:'Space Grotesk',sans-serif !important; letter-spacing:-.035em; }
h1 { font-size:2.35rem !important; }
p, label, .stMarkdown { color:var(--nx-text); }
.nx-eyebrow { color:#a99fff; font-size:.72rem; letter-spacing:.16em; font-weight:700; text-transform:uppercase; }
.nx-title { font-family:'Space Grotesk',sans-serif; font-size:2.35rem; font-weight:700; line-height:1.08; color:#f5f7ff; }
.nx-subtitle { color:#9ba9c2; font-size:1rem; margin-top:.55rem; }
.nx-card { background:linear-gradient(145deg,rgba(24,35,59,.96),rgba(16,25,44,.96)); border:1px solid var(--nx-border); border-radius:18px; padding:20px 21px; min-height:126px; box-shadow:0 12px 35px rgba(0,0,0,.12); }
.nx-card-label { color:#9ba9c2; font-size:.82rem; font-weight:600; }
.nx-card-value { color:#f5f7ff; font-family:'Space Grotesk',sans-serif; font-size:2rem; font-weight:700; margin-top:8px; }
.nx-card-note { color:#75d8ca; font-size:.76rem; margin-top:4px; }
.nx-panel { background:rgba(17,26,46,.88); border:1px solid var(--nx-border); border-radius:18px; padding:20px; }
.nx-agent { background:#141f35; border:1px solid var(--nx-border); border-radius:14px; padding:15px; min-height:112px; }
.nx-agent-icon { font-size:1.35rem; }
.nx-agent-name { color:#f5f7ff; font-weight:700; margin-top:7px; }
.nx-agent-desc { color:#9ba9c2; font-size:.78rem; margin-top:3px; }
.nx-pill { display:inline-block; padding:5px 10px; border-radius:30px; background:rgba(139,124,255,.14); border:1px solid rgba(139,124,255,.28); color:#c6beff; font-size:.72rem; font-weight:700; }
div.stButton > button { border-radius:10px; border:1px solid rgba(139,124,255,.35); background:linear-gradient(100deg,#7565e8,#8b7cff); color:white; font-weight:700; min-height:2.65rem; }
div.stButton > button:hover { border-color:#b4aaff; color:white; filter:brightness(1.08); }
.stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div { background:#111a2e !important; color:#edf2ff !important; border-color:var(--nx-border) !important; }
[data-testid="stFileUploader"] { background:rgba(17,26,46,.72); border:1px dashed rgba(139,124,255,.4); border-radius:14px; padding:10px; }
[data-testid="stMetric"] { background:#111a2e; border:1px solid var(--nx-border); border-radius:14px; padding:14px; }
[data-testid="stMetricLabel"] { color:#9ba9c2 !important; }
[data-testid="stMetricValue"] { color:#f5f7ff !important; }
hr { border-color:var(--nx-border) !important; }
.stChatMessage { background:rgba(17,26,46,.72); border:1px solid var(--nx-border); border-radius:14px; }
[data-testid="stDataFrame"] { border:1px solid var(--nx-border); border-radius:12px; overflow:hidden; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# --------------------------- Helpers ---------------------------
def heading(eyebrow, title, subtitle=None):
    st.markdown(f'<div class="nx-eyebrow">{eyebrow}</div><div class="nx-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="nx-subtitle">{subtitle}</div>', unsafe_allow_html=True)
    st.write("")

def metric_card(label, value, note):
    st.markdown(
        f'<div class="nx-card"><div class="nx-card-label">{label}</div>'
        f'<div class="nx-card-value">{value}</div><div class="nx-card-note">{note}</div></div>',
        unsafe_allow_html=True
    )

def save_upload(uploaded_file):
    # Prefix with a UUID to avoid overwriting a different user's same-named upload.
    safe_name = Path(uploaded_file.name).name
    destination = UPLOAD_DIR / f"{uuid.uuid4().hex[:8]}_{safe_name}"
    destination.write_bytes(uploaded_file.getvalue())
    return destination

def run_question(question):
    try:
        result = ask(question, st.session_state.thread_id, st.session_state.csv_path)
        st.session_state.total_queries += 1
        return result
    except Exception as exc:
        return {"answer": f"Request failed: {exc}", "analytics_table": None}

# --------------------------- Sidebar ---------------------------
with st.sidebar:
    st.markdown("""
    <div style="padding:8px 2px 22px 2px">
      <div style="font-size:1.65rem;font-weight:700;font-family:'Space Grotesk',sans-serif;color:#f5f7ff">✦ NEXORA<span style="color:#9b8cff"> AI</span></div>
      <div style="font-size:.68rem;letter-spacing:.15em;color:#8291ad;margin-top:3px">COMPANY INTELLIGENCE</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="nx-eyebrow">WORKSPACE</div>', unsafe_allow_html=True)
    pages = ["Dashboard", "AI Assistant", "Knowledge Hub", "Data Analytics", "Ticket Management"]
    selected = st.radio(
        "Navigation", pages,
        index=pages.index(st.session_state.page),
        label_visibility="collapsed",
        key="navigation_radio",
    )
    st.session_state.page = selected
    st.divider()
    st.markdown('<div class="nx-eyebrow">SYSTEM STATUS</div>', unsafe_allow_html=True)
    st.markdown(
        f'<span class="nx-pill">● {"KNOWLEDGE INDEX READY" if index_exists() else "INDEX NOT BUILT"}</span>',
        unsafe_allow_html=True
    )
    st.caption("Groq-powered • Local FAISS • SQLite")
    st.divider()
    if st.button("＋ New conversation", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.chat = []
        st.rerun()
    st.caption("Nexora AI · Learning/demo workspace")

tickets = list_tickets()
ticket_count = len(tickets)
doc_count = len(list(UPLOAD_DIR.glob("*"))) if UPLOAD_DIR.exists() else 0

# --------------------------- Dashboard ---------------------------
if st.session_state.page == "Dashboard":
    heading("YOUR AI WORKSPACE", "Company intelligence, <span style='color:#a99fff'>simplified.</span>",
            "One workspace to search company knowledge, analyse data, and manage support workflows.")
    st.markdown('<span class="nx-pill">✦ AI WORKSPACE ACTIVE</span>', unsafe_allow_html=True)
    st.write("")
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("TOTAL QUESTIONS", f"{st.session_state.total_queries:,}", "This browser session")
    with c2: metric_card("UPLOADED FILES", f"{doc_count:,}", "Documents and datasets")
    with c3: metric_card("SUPPORT TICKETS", f"{ticket_count:,}", "Saved in local SQLite")
    with c4: metric_card("AI WORKFLOWS", "04", "Supervisor + 3 specialists")
    st.write("")
    left, right = st.columns([1.35, 1])
    with left:
        st.markdown('<div class="nx-panel">', unsafe_allow_html=True)
        st.subheader("Explore your workspace")
        quick = [
            ("🤖", "AI Assistant", "Ask questions and let the supervisor route your request."),
            ("📚", "Knowledge Hub", "Upload internal documents and build searchable company knowledge."),
            ("📊", "Data Analytics", "Explore CSV data and generate business insights."),
            ("🎫", "Ticket Management", "Review support requests created by the assistant."),
        ]
        for icon, name, desc in quick:
            st.markdown(f'<div style="padding:10px 0;border-bottom:1px solid rgba(148,163,184,.12)"><b>{icon} &nbsp;{name}</b><div style="color:#9ba9c2;font-size:.82rem;margin:4px 0 0 31px">{desc}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="nx-panel">', unsafe_allow_html=True)
        st.subheader("Specialist agents")
        agents = [("🧭", "Supervisor", "Routes each request"), ("📖", "Knowledge", "Grounded document Q&A"), ("🎧", "Support", "Orders and ticket creation"), ("📈", "Data Analyst", "CSV calculations and insights")]
        for icon, name, desc in agents:
            st.markdown(f'<div class="nx-agent" style="margin-bottom:9px"><span class="nx-agent-icon">{icon}</span><div class="nx-agent-name">{name}</div><div class="nx-agent-desc">{desc}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.write("")
    st.info("Getting started: upload company PDFs/TXT/MD files in Knowledge Hub, or upload a CSV in Data Analytics.")

# --------------------------- AI Assistant ---------------------------
elif st.session_state.page == "AI Assistant":
    heading("NEXORA COPILOT", "How can I help today?", "Ask about company policies, orders, support tickets, or an uploaded dataset.")
    st.markdown('<span class="nx-pill">SUPERVISOR ROUTING ENABLED</span>', unsafe_allow_html=True)
    for item in st.session_state.chat:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])
            if item.get("table"):
                st.dataframe(pd.DataFrame(item["table"]), use_container_width=True)
    question = st.chat_input("Message Nexora AI...")
    if question:
        st.session_state.chat.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Supervisor is choosing the right specialist..."):
                result = run_question(question)
                answer = result.get("answer", "No response returned.")
                st.markdown(answer)
                table_text = result.get("analytics_table")
                if table_text:
                    st.code(table_text, language="text")
                st.session_state.chat.append({"role": "assistant", "content": answer})
        st.rerun()
    if not st.session_state.chat:
        st.markdown("**Try asking:**")
        examples = ["How many paid leave days are available?", "Check order ORD-1002", "Create a support ticket: the app keeps crashing."]
        cols = st.columns(3)
        for col, example in zip(cols, examples):
            with col:
                if st.button(example, use_container_width=True):
                    st.session_state.pending_question = example
                    st.rerun()
    if st.session_state.get("pending_question"):
        pending = st.session_state.pop("pending_question")
        with st.chat_message("user"):
            st.markdown(pending)
        with st.chat_message("assistant"):
            with st.spinner("Working..."):
                result = run_question(pending)
                answer = result.get("answer", "No response returned.")
                st.markdown(answer)
                st.session_state.chat.extend([
                    {"role": "user", "content": pending},
                    {"role": "assistant", "content": answer},
                ])
        st.rerun()

# --------------------------- Knowledge Hub ---------------------------
elif st.session_state.page == "Knowledge Hub":
    heading("DOCUMENT INTELLIGENCE", "Knowledge Hub", "Build a searchable knowledge base from your company documents.")
    col1, col2 = st.columns([1.25, .75])
    with col1:
        st.markdown('<div class="nx-panel">', unsafe_allow_html=True)
        st.subheader("Upload documents")
        uploads = st.file_uploader("Choose PDF, TXT or Markdown files", type=["pdf", "txt", "md"], accept_multiple_files=True, key="knowledge_uploads")
        if st.button("Build / update knowledge index", disabled=not uploads, use_container_width=True):
            saved_paths = [save_upload(file) for file in uploads]
            with st.spinner("Extracting, chunking, embedding and indexing documents..."):
                try:
                    chunk_count = build_index(saved_paths, append=index_exists())
                    st.success(f"Success! Indexed {chunk_count} text chunks.")
                except Exception as exc:
                    st.error(f"Indexing failed: {exc}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="nx-panel">', unsafe_allow_html=True)
        st.subheader("Index status")
        st.metric("Vector index", "Ready" if index_exists() else "Not built")
        st.metric("Files in uploads", doc_count)
        st.caption("Embeddings: all-MiniLM-L6-v2 · Vector store: FAISS")
        st.markdown('</div>', unsafe_allow_html=True)
    st.write("")
    st.subheader("Ask your documents")
    doc_question = st.text_input("Question", placeholder="What is the company's remote work policy?")
    if st.button("Search knowledge base", disabled=not doc_question):
        with st.spinner("Searching indexed documents..."):
            result = run_question(doc_question)
        st.markdown('<div class="nx-panel">', unsafe_allow_html=True)
        st.markdown(result.get("answer", "No answer."))
        st.markdown('</div>', unsafe_allow_html=True)

# --------------------------- Data Analytics ---------------------------
elif st.session_state.page == "Data Analytics":
    heading("BUSINESS INTELLIGENCE", "Data Analytics", "Upload a CSV and ask business questions in natural language.")
    uploaded_csv = st.file_uploader("Upload CSV dataset", type=["csv"], key="analytics_csv")
    if uploaded_csv:
        csv_path = save_upload(uploaded_csv)
        st.session_state.csv_path = str(csv_path)
        st.success(f"Loaded {uploaded_csv.name}")
    if st.session_state.csv_path and Path(st.session_state.csv_path).exists():
        df = pd.read_csv(st.session_state.csv_path)
        a, b, c = st.columns(3)
        with a: metric_card("ROWS", f"{len(df):,}", "Records loaded")
        with b: metric_card("COLUMNS", f"{len(df.columns):,}", "Available fields")
        with c: metric_card("MISSING CELLS", f"{int(df.isna().sum().sum()):,}", "Across the dataset")
        st.write("")
        st.subheader("Dataset preview")
        st.dataframe(df.head(100), use_container_width=True, hide_index=True)
        st.subheader("Quick visualisation")
        numeric_cols = list(df.select_dtypes(include="number").columns)
        if numeric_cols:
            chosen = st.selectbox("Choose a numeric column", numeric_cols)
            fig = px.histogram(df, x=chosen, title=f"Distribution of {chosen}", template="plotly_dark")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        st.subheader("Ask the Data Analyst")
        analytics_question = st.text_input("Your question", placeholder="Which product has the highest revenue?")
        if st.button("Analyse dataset", disabled=not analytics_question):
            with st.spinner("Analysing your dataset..."):
                result = run_question(analytics_question)
            st.markdown('<div class="nx-panel">', unsafe_allow_html=True)
            st.markdown(result.get("answer", "No result."))
            if result.get("analytics_table"):
                st.code(result["analytics_table"], language="text")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Upload a CSV file above to unlock dataset preview, charts, and natural-language analysis.")
        st.markdown("**Sample questions**")
        st.markdown("- Which month has the highest revenue?\\n- What is the average order value?\\n- Show the top five products by revenue.")

# --------------------------- Ticket Management ---------------------------
elif st.session_state.page == "Ticket Management":
    heading("CUSTOMER OPERATIONS", "Ticket Management", "Review support tickets created by Nexora's Support Agent.")
    tickets = list_tickets()
    open_count = sum(1 for t in tickets if t["status"].lower() != "resolved")
    high_count = sum(1 for t in tickets if t["priority"].lower() in {"high", "critical"})
    a, b, c = st.columns(3)
    with a: metric_card("TOTAL TICKETS", f"{len(tickets):,}", "All saved tickets")
    with b: metric_card("OPEN / ACTIVE", f"{open_count:,}", "Not marked resolved")
    with c: metric_card("HIGH PRIORITY", f"{high_count:,}", "High or critical")
    st.write("")
    if tickets:
        frame = pd.DataFrame(tickets)
        st.dataframe(frame, use_container_width=True, hide_index=True)
        st.download_button("Download tickets as CSV", frame.to_csv(index=False), "nexora_tickets.csv", "text/csv")
    else:
        st.info("No tickets yet. Open AI Assistant and say: 'Create a ticket: describe your issue.'")

