"""
LangGraph AI Agent — HCP CRM Log Interaction Screen
====================================================
The CORE behaviour:
  - User types a natural-language message in the chat.
  - The LLM extracts structured fields and returns them as `form_fields`.
  - The frontend receives `form_fields` and auto-populates the left-side form.
  - The user NEVER types directly into the form.

Tools (5):
  1. log_interaction      – extract fields from chat + save to DB
  2. edit_interaction     – correct specific fields from chat + update DB
  3. recommend_next_action – suggest next best sales action (fills follow_up_actions)
  4. suggest_follow_up    – recommend timing/channel (fills follow_up_actions)
  5. draft_outreach_email – generate email draft (fills outcomes field with draft)
"""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from database import SessionLocal, Interaction as DBInteraction, init_db

load_dotenv()


_key = os.getenv("GROQ_API_KEY", "")

if not _key:
    import warnings
    warnings.warn("GROQ_API_KEY is not set. Add it to your .env file.")


_init_key = _key or "placeholder-set-GROQ_API_KEY-in-env"

_llm    = ChatGroq(model="llama-3.3-70b-versatile",  api_key=_init_key, temperature=0.1)
_llm_fb = ChatGroq(model="llama3-70b-8192",          api_key=_init_key, temperature=0.1)


def _invoke(prompt: str) -> str:
    try:
        return _llm.invoke(prompt).content
    except Exception:
        try:
            return _llm_fb.invoke(prompt).content
        except Exception as e:
            return f"LLM error: {e}"



_TODAY = datetime.utcnow().strftime("%Y-%m-%d")
_NOW   = datetime.utcnow().strftime("%H:%M")

_EXTRACTION_PROMPT = """You are a CRM data-extraction assistant for pharmaceutical field reps.

Extract structured data from the rep's message and return ONLY a valid JSON object.
Use today's date ({today}) if no date is mentioned.
Interaction type options: Meeting, Call, Email, Webinar, Conference, Advisory Board.
Sentiment options: Positive, Neutral, Negative.

Message: "{message}"

Current form values (keep these for any field NOT mentioned in the message):
{current_fields}

Return JSON with EXACTLY these keys (use empty string "" for unknown fields):
{{
  "hcpName": "",
  "interactionType": "Meeting",
  "date": "",
  "time": "",
  "attendees": "",
  "topicsDiscussed": "",
  "materialsShared": "",
  "samplesDistributed": "",
  "hcpSentiment": "Neutral",
  "outcomes": "",
  "followUpActions": ""
}}

Rules:
- Only update fields that are explicitly mentioned in the message.
- Keep current_fields values for fields NOT mentioned.
- Return ONLY the JSON object, no explanation, no markdown fences."""


def _extract_form_fields(message: str, current: Dict[str, Any]) -> Dict[str, Any]:
    """Call LLM to extract form fields from a natural-language message."""
    current_str = "\n".join(f'  "{k}": "{v}"' for k, v in current.items() if v)
    prompt = _EXTRACTION_PROMPT.format(
        today=_TODAY,
        message=message,
        current_fields=current_str or "  (all empty)",
    )
    raw = _invoke(prompt)

    
    raw = re.sub(r"```(?:json)?", "", raw).strip()

    
    m = re.search(r"\{[\s\S]*\}", raw)
    if m:
        try:
            extracted = json.loads(m.group())
            
            merged = dict(current)
            for k, v in extracted.items():
                if v and v != "":
                    merged[k] = v
            return merged
        except json.JSONDecodeError:
            pass

    return dict(current)  



class AgentState(TypedDict):
    messages:       Annotated[List[BaseMessage], add_messages]
    current_fields: Dict[str, Any]
    tool_name:      str
    form_fields:    Dict[str, Any]   
    suggestions:    List[str]
    reply:          str
    interaction_id: Optional[str]



@tool
def log_interaction(
    hcp_name: str,
    interaction_type: str = "Meeting",
    date: str = "",
    time: str = "",
    attendees: str = "",
    topics_discussed: str = "",
    materials_shared: str = "",
    samples_distributed: str = "",
    hcp_sentiment: str = "Neutral",
    outcomes: str = "",
    follow_up_actions: str = "",
) -> str:
    """
    Log a new HCP interaction. Extracts structured data from the rep's
    natural-language chat message and saves it to the database.
    Returns the interaction ID and an AI-generated summary.
    """
   
    summary_prompt = f"""Write a 2-sentence professional CRM summary for this HCP interaction:
HCP: {hcp_name} | Type: {interaction_type} | Date: {date}
Topics: {topics_discussed} | Sentiment: {hcp_sentiment}
Outcomes: {outcomes} | Follow-ups: {follow_up_actions}
Keep it under 50 words."""

    summary = _invoke(summary_prompt).strip()

    
    interaction_id = str(uuid.uuid4())
    db = SessionLocal()
    try:
        db.add(DBInteraction(
            id=interaction_id,
            hcp_name=hcp_name,
            interaction_type=interaction_type,
            date=date or _TODAY,
            time=time or _NOW,
            attendees=attendees,
            topics_discussed=topics_discussed,
            materials_shared=materials_shared,
            samples_distributed=samples_distributed,
            hcp_sentiment=hcp_sentiment,
            outcomes=outcomes,
            follow_up_actions=follow_up_actions,
            ai_summary=summary,
            ai_entities="{}",
            created_at=datetime.utcnow().isoformat(),
        ))
        db.commit()
    except Exception as e:
        db.rollback()
        return json.dumps({"error": str(e)})
    finally:
        db.close()

    return json.dumps({
        "interaction_id": interaction_id,
        "summary": summary,
        "message": f"✅ Interaction with {hcp_name} logged successfully (ID: {interaction_id[:8]}…).",
    })



@tool
def edit_interaction(
    interaction_id: str = "",
    hcp_name: str = "",
    interaction_type: str = "",
    date: str = "",
    time: str = "",
    attendees: str = "",
    topics_discussed: str = "",
    materials_shared: str = "",
    samples_distributed: str = "",
    hcp_sentiment: str = "",
    outcomes: str = "",
    follow_up_actions: str = "",
) -> str:
    """
    Correct specific fields of the most recent (or specified) logged interaction.
    Only the fields explicitly provided are updated; all others remain unchanged.
    The AI summary is regenerated to reflect the corrections.
    """
    db = SessionLocal()
    try:
        record = (
            db.query(DBInteraction).filter(DBInteraction.id == interaction_id).first()
            if interaction_id else
            db.query(DBInteraction).order_by(DBInteraction.created_at.desc()).first()
        )

        if not record:
            return json.dumps({"error": "No interaction found. Log one first."})

        if hcp_name:           record.hcp_name = hcp_name
        if interaction_type:   record.interaction_type = interaction_type
        if date:               record.date = date
        if time:               record.time = time
        if attendees:          record.attendees = attendees
        if topics_discussed:   record.topics_discussed = topics_discussed
        if materials_shared:   record.materials_shared = materials_shared
        if samples_distributed: record.samples_distributed = samples_distributed
        if hcp_sentiment:      record.hcp_sentiment = hcp_sentiment
        if outcomes:           record.outcomes = outcomes
        if follow_up_actions:  record.follow_up_actions = follow_up_actions

        
        record.ai_summary = _invoke(
            f"2-sentence CRM summary: HCP {record.hcp_name}, "
            f"Topics: {record.topics_discussed}, Sentiment: {record.hcp_sentiment}, "
            f"Outcomes: {record.outcomes}"
        ).strip()
        record.updated_at = datetime.utcnow().isoformat()
        db.commit()
        db.refresh(record)

        return json.dumps({
            "interaction_id": record.id,
            "updated_summary": record.ai_summary,
            "message": f"✅ Interaction updated. Summary: {record.ai_summary}",
        })
    except Exception as e:
        db.rollback()
        return json.dumps({"error": str(e)})
    finally:
        db.close()



@tool
def recommend_next_action(
    hcp_name: str,
    hcp_sentiment: str = "Neutral",
    topics_discussed: str = "",
    outcomes: str = "",
) -> str:
    """
    Analyse the interaction and recommend the single highest-impact next sales
    action for the field rep. The recommendation is written into the
    Follow-up Actions field of the form.
    """
    content = _invoke(f"""You are a life-science sales strategist.
Recommend the single best next action for this HCP interaction.
Reply in this exact format (plain text, no markdown):
NEXT ACTION: <one clear action sentence>
REASON: <one sentence why>
PRIORITY: High / Medium / Low

HCP: {hcp_name} | Sentiment: {hcp_sentiment}
Topics: {topics_discussed} | Outcomes: {outcomes}""")

    return json.dumps({"recommendation": content, "hcp": hcp_name})



@tool
def suggest_follow_up(
    hcp_name: str,
    hcp_sentiment: str = "Neutral",
    interaction_type: str = "Meeting",
    topics_discussed: str = "",
) -> str:
    """
    Recommend the optimal follow-up timing, channel, and key message based
    on the HCP's sentiment and discussion topics. The result is written into
    the Follow-up Actions field of the form.
    """
    content = _invoke(f"""You are a pharma sales engagement expert.
Give a concrete follow-up plan (plain text, no markdown):
TIMING: <when to follow up>
CHANNEL: <email / call / visit>
KEY MESSAGE: <one sentence to reinforce>

HCP: {hcp_name} | Sentiment: {hcp_sentiment}
Type: {interaction_type} | Topics: {topics_discussed}""")

    return json.dumps({"follow_up_strategy": content, "hcp": hcp_name})



@tool
def draft_outreach_email(
    hcp_name: str,
    topics_discussed: str = "",
    materials_shared: str = "",
    hcp_sentiment: str = "Neutral",
    outcomes: str = "",
) -> str:
    """
    Generate a short, personalised, compliance-aware follow-up email.
    The drafted email is placed into the Outcomes field so the rep can
    copy and send it directly.
    """
    content = _invoke(f"""Write a professional pharma follow-up email (max 120 words).
Format:
SUBJECT: <subject>
BODY:
<email text>

HCP: {hcp_name} | Topics: {topics_discussed}
Materials: {materials_shared} | Sentiment: {hcp_sentiment}
Outcomes: {outcomes}""")

    return json.dumps({"email_draft": content, "hcp": hcp_name})


TOOLS = [
    log_interaction,
    edit_interaction,
    recommend_next_action,
    suggest_follow_up,
    draft_outreach_email,
]
TOOL_NAMES_DISPLAY = [
    "Log Interaction",
    "Edit Interaction",
    "Recommend Next Action",
    "Suggest Follow-up",
    "Draft Outreach Email",
]
TOOL_NAMES = [t.name for t in TOOLS]

_llm_with_tools = _llm.bind_tools(TOOLS)


def _build_graph():
    def agent_node(state: AgentState) -> Dict[str, Any]:
        return {"messages": [_llm_with_tools.invoke(state["messages"])]}

    def tool_node(state: AgentState) -> Dict[str, Any]:
        last = state["messages"][-1]
        results: List[BaseMessage] = []
        tool_map = {t.name: t for t in TOOLS}

        if hasattr(last, "tool_calls") and last.tool_calls:
            for tc in last.tool_calls:
                fn = tool_map.get(tc["name"])
                try:
                    out = fn.invoke(tc["args"]) if fn else json.dumps({"error": "unknown tool"})
                except Exception as e:
                    out = json.dumps({"error": str(e)})
                results.append(ToolMessage(content=str(out), tool_call_id=tc["id"]))

        return {"messages": results}

    def should_continue(state: AgentState) -> str:
        last = state["messages"][-1]
        return "tools" if (hasattr(last, "tool_calls") and last.tool_calls) else END

    g = StateGraph(AgentState)
    g.add_node("agent", agent_node)
    g.add_node("tools", tool_node)
    g.add_edge(START, "agent")
    g.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    g.add_edge("tools", "agent")
    return g.compile()


_graph = _build_graph()



def _parse_tool_result(messages: List[BaseMessage]) -> Dict[str, Any]:
    """Extract the tool JSON result from the last ToolMessage."""
    for msg in reversed(messages):
        if isinstance(msg, ToolMessage):
            try:
                return json.loads(msg.content)
            except Exception:
                pass
    return {}


def _final_ai_text(messages: List[BaseMessage]) -> str:
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content:
            return msg.content
    return "Done."


def _suggestions_for(tool_name: str) -> List[str]:
    return {
        "log_interaction":      ["Schedule a follow-up meeting within 2 weeks",
                                 "Send a thank-you email within 24 hours",
                                 "Add Dr. Sharma to advisory board invite list"],
        "edit_interaction":     ["Confirm corrected details with your manager",
                                 "Re-run Next Action analysis with updated data",
                                 "Sync updated notes with your account plan"],
        "recommend_next_action":["Block time in your calendar for this action",
                                 "Prepare clinical materials to support the visit",
                                 "Coordinate with Medical Science Liaison"],
        "suggest_follow_up":    ["Set a calendar reminder now",
                                 "Draft your follow-up message in advance",
                                 "Align timing with your territory plan"],
        "draft_outreach_email": ["Review for compliance before sending",
                                 "Attach one relevant clinical reference",
                                 "CC your field manager if required"],
    }.get(tool_name, [])



_TOOL_MAP = {
    "Log Interaction":       "log_interaction",
    "Edit Interaction":      "edit_interaction",
    "Recommend Next Action": "recommend_next_action",
    "Suggest Follow-up":     "suggest_follow_up",
    "Draft Outreach Email":  "draft_outreach_email",
}


def run_agent(
    tool_name: str,
    current_fields: Dict[str, Any],
    message: str,
) -> Dict[str, Any]:
    """
    Main entry point.

    Returns a dict with:
      reply          – AI text to show in chat
      form_fields    – complete updated form state (frontend merges this in)
      suggestions    – clickable follow-up suggestions
      interaction_id – DB id if a record was saved/updated
    """
    internal = _TOOL_MAP.get(tool_name, "log_interaction")

    
    updated_fields = _extract_form_fields(message, current_fields)

   
    system = f"""You are an AI assistant in a life-science CRM.
The field rep just said: "{message}"

Extracted form data:
{json.dumps(updated_fields, indent=2)}

Your task: call the '{internal}' tool using the extracted data above.
After the tool call, write a brief 2-3 sentence confirmation for the rep."""

   
    try:
        final_state = _graph.invoke(
            {
                "messages":       [HumanMessage(content=system)],
                "current_fields": updated_fields,
                "tool_name":      internal,
                "form_fields":    updated_fields,
                "suggestions":    [],
                "reply":          "",
                "interaction_id": current_fields.get("interaction_id"),
            },
            {"recursion_limit": 12},
        )
    except Exception as exc:
        return {
            "reply":          f"Agent error: {exc}. Check your GROQ_API_KEY.",
            "form_fields":    current_fields,
            "suggestions":    [],
            "interaction_id": None,
        }

   
    tool_result = _parse_tool_result(final_state["messages"])
    ai_reply    = _final_ai_text(final_state["messages"])
    interaction_id = tool_result.get("interaction_id") or current_fields.get("interaction_id")

   
    if internal == "edit_interaction":
        updated_fields = _extract_form_fields(message, current_fields)

   
    if internal == "recommend_next_action":
        rec = tool_result.get("recommendation", "")
        if rec:
            updated_fields["followUpActions"] = rec

    if internal == "suggest_follow_up":
        strat = tool_result.get("follow_up_strategy", "")
        if strat:
            updated_fields["followUpActions"] = strat

    
    if internal == "draft_outreach_email":
        draft = tool_result.get("email_draft", "")
        if draft:
            updated_fields["outcomes"] = draft

    return {
        "reply":          ai_reply,
        "form_fields":    updated_fields,
        "suggestions":    _suggestions_for(internal),
        "interaction_id": interaction_id,
    }
