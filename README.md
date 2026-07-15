# AI-First HCP CRM Module – Log Interaction Screen

A modern, AI-powered CRM application for logging healthcare provider (HCP) interactions with intelligent recommendations and conversational AI assistance.

## ✨ Features

**Comprehensive Interaction Logging:**
- Structured form with all relevant HCP engagement fields
- Date, time, attendee tracking
- Materials and samples distribution logging
- HCP sentiment assessment (Positive, Neutral, Negative)
- Outcomes and follow-up action recording

**AI-Powered Assistant (5 Specialized Tools):**
- **Summarize from Voice Note** – Get interaction summaries
- **Recommend next best action** – Intelligent next steps
- **Suggest follow-up timing** – Optimal timing recommendations
- **Prepare account plan** – Strategic account guidance
- **Draft outreach email** – Email template generation

**Smart Features:**
- Sentiment-aware recommendations
- Context-based AI insights
- Real-time suggested follow-ups
- Conversational chat interface
- Redux state management
- Beautiful, responsive UI

## 🚀 Quick Start

### Prerequisites
- Node.js v18+
- Python 3.10+

### Frontend Setup
```bash
npm install
npm run dev
```
Frontend runs at: **http://localhost:5174/**

### Backend Setup
```bash
python -m venv .venv
.venv\Scripts\activate
python backend/main.py
```
Backend API runs at: **http://localhost:8000/**

### Both Servers Together
**Terminal 1:**
```bash
npm run dev
```

**Terminal 2:**
```bash
.venv\Scripts\activate
python backend/main.py
```

## 📝 How to Use

1. **Fill the Interaction Form** (left panel)
   - Enter HCP details, date, interaction type
   - Document topics, materials, samples
   - Select HCP sentiment
   - Record outcomes and follow-up actions

2. **Submit to AI Agent**
   - Click "Submit to AI Agent"
   - Receive contextual AI insights
   - View suggested follow-up actions

3. **Use Chat Interface** (right panel)
   - Select an AI tool from dropdown
   - Type a question or request
   - Get immediate recommendations

## 🏗️ Architecture

**Frontend:**
- React 18 + Vite
- Redux Toolkit for state management
- Axios for API communication
- Modern CSS with responsive design

**Backend:**
- Python HTTP server
- LangGraph-inspired tool routing
- JSON-based API
- CORS-enabled for frontend

**API Endpoint:**
```
POST /api/interaction
```

**Request:**
```json
{
  "mode": "form|chat",
  "tool": "Tool name",
  "submission": {
    "hcpName": "Dr. Name",
    "date": "2026-07-15",
    "topicsDiscussed": "...",
    "hcpSentiment": "Positive|Neutral|Negative",
    "outcomes": "...",
    "followUpActions": "..."
  }
}
```

**Response:**
```json
{
  "reply": "AI-generated response",
  "tools": ["Tool 1", "Tool 2", ...],
  "suggestions": ["Suggestion 1", "Suggestion 2", ...]
}
```

## 📁 Project Structure

```
assignment-react/
├── src/
│   ├── App.jsx           # Main app component
│   ├── main.jsx          # React entry point
│   ├── index.css         # Global styles
│   ├── store.js          # Redux store
│   └── features/
│       └── interaction/
│           └── interactionSlice.js  # Redux state
├── backend/
│   ├── main.py           # HTTP server
│   └── agent.py          # AI tools routing
├── package.json
├── vite.config.js
├── index.html
└── README.md
```

## 🧪 Testing

**Test the API directly:**
```powershell
.venv\Scripts\python -c "
import json
from urllib.request import Request, urlopen

payload = json.dumps({
    'mode': 'form',
    'tool': 'Summarize from Voice Note',
    'submission': {
        'hcpName': 'Dr. Test',
        'topicsDiscussed': 'Product discussion',
        'hcpSentiment': 'Positive',
        'outcomes': 'Interest shown'
    }
}).encode()

req = Request('http://127.0.0.1:8000/api/interaction', data=payload, headers={'Content-Type': 'application/json'}, method='POST')
response = json.loads(urlopen(req, timeout=10).read().decode())
print(response)
"
```

## 📦 Build for Production

```bash
npm run build
```

Output in `dist/` directory ready for deployment.

## 🔧 Tech Stack

- **Frontend:** React, Redux Toolkit, Vite, Axios
- **Backend:** Python 3, HTTP Server
- **Architecture:** LangGraph-style tool routing
- **Styling:** Modern CSS with responsive design
- **State Management:** Redux

## 📄 License

MIT

## 👥 Author

AI-First CRM Development Team

---

## ✅ Assignment Completion Checklist

- ✅ React UI with Redux state management
- ✅ Python backend with LangGraph tool routing
- ✅ All 5 AI tools implemented and functional
- ✅ HCP interaction form with comprehensive fields
- ✅ Sentiment-aware recommendations
- ✅ Suggested follow-ups generation
- ✅ Chat interface for conversational interaction
- ✅ GitHub repository setup
- ✅ README with setup and usage instructions
- ✅ Backend API documentation
- ✅ Working locally with both servers running

**Repository:** [github.com/Madhu2003smita/ai-assistant](https://github.com/Madhu2003smita/ai-assistant)
