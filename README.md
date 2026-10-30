# ORVEXA AI — Enhanced Smart Company Assistant

An enhanced version of the Smart Company Assistant with a LangGraph supervisor, specialist workflows, RAG document Q&A, CSV analysis, SQLite support tickets, and a Streamlit UI.

## Features
- Professional dark Streamlit SaaS dashboard with Dashboard, AI Assistant, Knowledge Hub, Data Analytics, and Ticket Management pages.
- Supervisor routing: knowledge/RAG, support, data analyst.
- Groq chat model + HuggingFace sentence-transformer embeddings.
- Upload PDF, TXT and Markdown documents and index them into FAISS.
- Answers include retrieved source filenames and page metadata where available.
- CSV upload with safe, predefined Pandas analysis operations (no generated Python execution).
- Create and persist support tickets in SQLite.
- Per-session conversation history in Streamlit.

## Windows setup (PowerShell or CMD)
```bash
cd Nexora-AI-Enhanced
python -m venv myenv
myenv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```
Edit `.env` and add your Groq API key.

## Run the application (Windows)
Double-click `RUN_NEXORA_WINDOWS.bat`. On first run it creates a virtual environment,
copies `.env.example` to `.env`, and opens it so you can add your Groq API key.
Run the batch file again to install dependencies and launch the Streamlit dashboard.

Alternatively, activate the environment and run:
```bash
streamlit run frontend/app.py
```
Open the local URL shown in the terminal.

## Build the document index
You can upload files from the Streamlit sidebar. To index the sample `data/` documents:
```bash
python -m src.ingest
```

## CLI mode
```bash
python -m src.main
```

## Example questions
- "How many days of paid time off do I get?"
- "What is the status of order ORD-1002?"
- "Create a ticket: my CloudSync app keeps crashing."
- Upload a CSV, then ask "Which column has the highest total?" or "Show summary statistics."

## Important notes
- The sample order records are demo data in `src/tools.py`, not a live order-management integration.
- Tickets are stored locally in `nexora.db`.
- FAISS uses local pickle-based persistence. Only load indexes you created yourself; do not load untrusted vectorstore files.
- For a real company deployment, add authentication, authorization, audit logging, PII controls, rate limits, and connect tools to approved company APIs/databases.
