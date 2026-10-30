# Orvexa AI – Intelligent Enterprise Workspace

**One platform. Multiple agents. Smarter operations.**

Orvexa AI is an AI-powered enterprise assistant designed to simplify everyday business operations through intelligent agents, Retrieval-Augmented Generation (RAG), document understanding, data analytics, and automated support ticket management.

Built using **Python, LangChain, LangGraph, Groq, FAISS, and Streamlit**, Orvexa AI combines multiple specialized workflows into one unified workspace.

## ✨ Key Features

### 🤖 Multi-Agent AI Assistant
- Supervisor-based workflow using LangGraph.
- Routes user queries to specialized agents.
- Supports knowledge retrieval, customer support, and data analysis.
- Maintains conversation history within a session.

### 📚 Intelligent Knowledge Hub (RAG)
- Upload PDF, TXT, and Markdown documents.
- Split documents into searchable chunks.
- Generate embeddings using HuggingFace sentence transformers.
- Store and retrieve relevant information using FAISS.
- Generate context-aware answers with source references.

### 📊 AI-Powered Data Analytics
- Upload CSV datasets.
- Perform predefined data analysis operations using Pandas.
- Generate summary statistics and insights.
- Ask natural-language questions about uploaded data.

### 🎫 Smart Ticket Management
- Create support tickets through natural-language requests.
- Store tickets persistently using SQLite.
- Track and manage support requests.

### 📈 Enterprise Dashboard
- Centralized workspace for application modules.
- Dashboard overview of available operations.
- Professional Streamlit interface.

## 🏗️ System Architecture

```text
                    USER
                      |
                      v
               STREAMLIT FRONTEND
                      |
                      v
             LANGGRAPH SUPERVISOR
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
      KNOWLEDGE    SUPPORT     ANALYTICS
       AGENT        AGENT        AGENT
          |           |           |
          v           v           v
        FAISS       SQLITE      PANDAS
       VECTOR DB    DATABASE    DATAFRAME
          |           |           |
          +-----------+-----------+
                      |
                      v
                  GROQ LLM
                      |
                      v
                AI RESPONSE
```

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| LLM Provider | Groq |
| LLM Framework | LangChain |
| Agent Workflow | LangGraph |
| Frontend | Streamlit |
| Embeddings | HuggingFace Sentence Transformers |
| Vector Database | FAISS |
| Database | SQLite |
| Data Analysis | Pandas |
| Document Processing | PyPDF |

## 📁 Project Structure

```text
Orvexa-AI/
│
├── frontend/
│   └── app.py
│
├── src/
│   ├── config.py
│   ├── schemas.py
│   ├── prompts.py
│   ├── ingest.py
│   ├── rag_chain.py
│   ├── database.py
│   ├── tools.py
│   ├── analytics.py
│   ├── graph.py
│   └── main.py
│
├── data/
│   ├── hr_policy.md
│   ├── product_faq.md
│   └── sample_sales.csv
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Orvexa-AI.git
cd Orvexa-AI
```

### 2. Create a virtual environment

```bash
python -m venv myenv
```

### 3. Activate the environment

**Windows CMD:**

```bash
myenv\Scripts\activate
```

**PowerShell:**

```powershell
.\myenv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the root directory and add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get your API key from [Groq Console](https://console.groq.com/).

**Important:** Never upload your `.env` file or expose your API key on GitHub.

## ▶️ Run the Application

From the project root directory:

```bash
python -m streamlit run frontend/app.py
```

Open the local URL displayed in your terminal, usually:

```text
http://localhost:8501
```

## 💡 Example Use Cases

**Knowledge Assistant**
- How many paid leave days are available?
- What is the company's remote work policy?

**Support Assistant**
- Create a ticket for an email authentication issue.
- My CloudSync application keeps crashing.

**Data Analytics Assistant**
- Which column has the highest total?
- Show summary statistics for my uploaded CSV.

## 🔐 Security Considerations

- API keys are managed through environment variables.
- CSV analysis uses predefined operations rather than executing generated Python code.
- FAISS indexes use local persistence. Only load trusted indexes.
- SQLite provides local ticket persistence.

For production deployment, additional authentication, authorization, access controls, audit logging, and secure database integrations are recommended.

## 🚀 Future Enhancements

- Role-based access control.
- More specialized AI agents.
- Advanced analytics and visualization.
- Integration with enterprise APIs.
- Cloud deployment and scalable storage.
- Persistent conversation memory.

---

**Orvexa AI**  
*Intelligent Enterprise Workspace*  
Built with Python and Generative AI.
