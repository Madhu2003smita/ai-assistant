# AI-First CRM – HCP Module: Log Interaction Screen

A full-stack AI-powered CRM application for life science field representatives to log, analyse, and manage HCP (Healthcare Professional) interactions.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18 + Redux Toolkit + Vite |
| **Backend** | Python 3.11 + FastAPI + Uvicorn |
| **AI Framework** | LangGraph (agent graph with tool-calling) |
| **LLMs** | Groq – `gemma2-9b-it` (primary) · `llama-3.3-70b-versatile` (fallback) |
| **Database** | SQLite (default) · PostgreSQL / MySQL (configurable via `DATABASE_URL`) |
| **Font** | Google Inter |

---

## Features

- **Dual-mode interaction logging** – structured form *and* conversational chat interface
- **LangGraph AI agent** with 5 specialised tools for sales activities
- **AI enrichment** – automatic summarisation and entity extraction (products, action items, sentiment)
- **Persistent storage** – all interactions saved to a relational database
- **Interaction history** – browse, load, and edit previously logged records
- **One-click AI suggestions** – suggested follow-ups populate the form with a single click
- **Responsive UI** – works on desktop and tablet

---

## LangGraph Agent & Tools

The agent is a **ReAct-style graph** built with LangGraph. Each user request triggers the agent node which decides which tool to invoke based on the selected tool and conversation context.

```
START → agent_node ─(tool_calls?)─► tool_node → agent_node → END
```

### Tool 1 – `log_interaction`
Captures all interaction fields, sends them to the Groq LLM for **summarisation and entity extraction** (products mentioned, action items, sentiment signals), then persists the enriched record to the database. Returns the generated interaction ID, AI summary, and extracted entities.

### Tool 2 – `edit_interaction`
Accepts an `interaction_id` (or defaults to the most recent record) and updates only the supplied non-empty fields. **Regenerates the AI summary** after applying changes. Used when a rep needs to correct or supplement a previously logged interaction.

### Tool 3 – `recommend_next_action`
Analyses HCP sentiment, discussed topics, and outcomes to suggest the **single highest-impact next sales action**, along with its rationale and priority level.

### Tool 4 – `suggest_follow_up`
Recommends the **optimal follow-up timing and communication channel** based on sentiment and interaction type, and proposes the core message to reinforce.

### Tool 5 – `draft_outreach_email`
Generates a **personalised, compliance-aware follow-up email** (subject + body ≤ 150 words) tailored to the specific topics discussed and HCP context.

---

## Project Structure

```
├── backend/
│   ├── main.py          # FastAPI app – routes + CORS
│   ├── agent.py         # LangGraph agent graph + 5 tools
│   └── database.py      # SQLAlchemy models + session setup
├── src/
│   ├── App.jsx          # Main React component (form + chat UI)
│   ├── main.jsx         # React entry point + Redux Provider
│   ├── store.js         # Redux store
│   ├── index.css        # Global styles (Google Inter)
│   └── features/
│       └── interaction/
│           └── interactionSlice.js  # Redux slice
├── index.html
├── vite.config.js
├── package.json
├── requirements.txt
└── .env.example
```

---

## Getting Started

### Prerequisites
- **Node.js** ≥ 18
- **Python** ≥ 3.10
- A free [Groq API key](https://console.groq.com/)

---

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <repo-folder>
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Open .env and add your GROQ_API_KEY
```

### 3. Install Python dependencies

```bash
# Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 4. Start the FastAPI backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

### 5. Install frontend dependencies & start Vite

Open a new terminal:

```bash
npm install
npm run dev
```

The UI will be available at `http://localhost:5173`.

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness probe |
| `GET` | `/api/tools` | List all agent tool names |
| `POST` | `/api/interaction` | Run LangGraph agent (main endpoint) |
| `GET` | `/api/interactions` | List recent interactions (last 50) |
| `GET` | `/api/interactions/{id}` | Fetch a single interaction by ID |

### POST `/api/interaction` payload

```json
{
  "tool": "Log Interaction",
  "mode": "form",
  "message": "Optional chat message",
  "submission": {
    "hcpName": "Dr. Priya Sharma",
    "interactionType": "Meeting",
    "date": "2025-04-19",
    "time": "14:30",
    "attendees": "John Doe",
    "topicsDiscussed": "Phase III efficacy data for OncoBoost",
    "materialsShared": "OncoBoost Phase III brochure",
    "samplesDistributed": "Starter pack x2",
    "hcpSentiment": "Positive",
    "outcomes": "HCP open to prescribing after formulary review",
    "followUpActions": "Send clinical evidence summary"
  }
}
```

---

## Using a Production Database

Set `DATABASE_URL` in your `.env` file:

**PostgreSQL:**
```
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/hcp_crm
```

**MySQL:**
```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/hcp_crm
```

The tables are created automatically on server start.

---

## What I Understood from the Task

This task required building an **AI-first CRM screen** specifically for pharmaceutical/life-science field representatives interacting with Healthcare Professionals. The key insight is that traditional CRM data entry is slow and error-prone – the AI layer (LangGraph + Groq) makes the experience faster by:

1. **Extracting structured data** from freeform conversation (chat mode)
2. **Enriching records automatically** with summaries and entity extraction
3. **Guiding reps** with next-best-action and follow-up recommendations
4. **Reducing cognitive load** by drafting emails and suggesting follow-ups

The dual-mode UI (form + chat) ensures flexibility for reps who prefer structured input as well as those who prefer conversational logging in the field.
