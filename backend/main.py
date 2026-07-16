"""
FastAPI backend — AI-First CRM HCP Module
"""
from __future__ import annotations

import json
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import SessionLocal, Interaction as DBInteraction, init_db
from agent import TOOL_NAMES_DISPLAY, run_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI-First CRM – HCP Module", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)




class FormFields(BaseModel):
    hcpName: str = ""
    interactionType: str = "Meeting"
    date: str = ""
    time: str = ""
    attendees: str = ""
    topicsDiscussed: str = ""
    materialsShared: str = ""
    samplesDistributed: str = ""
    hcpSentiment: str = "Neutral"
    outcomes: str = ""
    followUpActions: str = ""
    interaction_id: Optional[str] = None


class AgentRequest(BaseModel):
    tool: str = "Log Interaction"
    current_fields: FormFields = FormFields()
    message: str = ""


class AgentResponse(BaseModel):
    reply: str
    form_fields: Dict[str, Any]     
    tools: List[str]
    suggestions: List[str]
    interaction_id: Optional[str] = None




@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/tools")
async def list_tools():
    return {"tools": TOOL_NAMES_DISPLAY}


@app.post("/api/interaction", response_model=AgentResponse)
async def handle_interaction(req: AgentRequest) -> AgentResponse:
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    result = run_agent(
        tool_name=req.tool,
        current_fields=req.current_fields.model_dump(),
        message=req.message,
    )

    return AgentResponse(
        reply=result["reply"],
        form_fields=result["form_fields"],
        tools=TOOL_NAMES_DISPLAY,
        suggestions=result["suggestions"],
        interaction_id=result.get("interaction_id"),
    )


@app.get("/api/interactions")
async def list_interactions():
    db = SessionLocal()
    try:
        rows = db.query(DBInteraction).order_by(DBInteraction.created_at.desc()).limit(50).all()
        return [
            {
                "id": r.id,
                "hcp_name": r.hcp_name,
                "interaction_type": r.interaction_type,
                "date": r.date,
                "hcp_sentiment": r.hcp_sentiment,
                "ai_summary": r.ai_summary,
                "created_at": r.created_at,
            }
            for r in rows
        ]
    finally:
        db.close()


@app.get("/api/interactions/{interaction_id}")
async def get_interaction(interaction_id: str):
    db = SessionLocal()
    try:
        r = db.query(DBInteraction).filter(DBInteraction.id == interaction_id).first()
        if not r:
            raise HTTPException(status_code=404, detail="Not found.")
        return {
            "id": r.id,
            "hcp_name": r.hcp_name,
            "interaction_type": r.interaction_type,
            "date": r.date, "time": r.time,
            "attendees": r.attendees,
            "topics_discussed": r.topics_discussed,
            "materials_shared": r.materials_shared,
            "samples_distributed": r.samples_distributed,
            "hcp_sentiment": r.hcp_sentiment,
            "outcomes": r.outcomes,
            "follow_up_actions": r.follow_up_actions,
            "ai_summary": r.ai_summary,
            "ai_entities": json.loads(r.ai_entities or "{}"),
            "created_at": r.created_at,
            "updated_at": r.updated_at,
        }
    finally:
        db.close()
