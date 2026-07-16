/**
 * AI-First CRM — HCP Log Interaction Screen
 *
 * GOLDEN RULE: The left form is READ-ONLY.
 * It is populated entirely by the AI chat on the right.
 * The user types in the chat → LangGraph agent extracts fields → form auto-fills.
 */
import { useEffect, useRef, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import axios from 'axios';
import {
  appendMessage,
  resetAll,
  setError,
  setFormFields,
  setLastSavedId,
  setLoading,
  setRecentInteractions,
  setSuggestions,
} from './features/interaction/interactionSlice';

const API = 'http://localhost:8000';

const TOOLS = [
  { value: 'Log Interaction',        desc: 'Extract fields from chat & save' },
  { value: 'Edit Interaction',       desc: 'Correct specific fields via chat' },
  { value: 'Recommend Next Action',  desc: 'AI suggests best next sales step' },
  { value: 'Suggest Follow-up',      desc: 'Optimal timing & channel advice' },
  { value: 'Draft Outreach Email',   desc: 'Generate personalised email draft' },
];

const SENTIMENTS = ['Positive', 'Neutral', 'Negative'];
const TYPES      = ['Meeting', 'Call', 'Email', 'Webinar', 'Conference', 'Advisory Board'];

// ── Sentiment icon helper ────────────────────────────────────────────────────
function SentimentIcon({ value, active }) {
  const map = { Positive: '🙂', Neutral: '😐', Negative: '😞' };
  return (
    <span style={{ fontSize: 18, opacity: active ? 1 : 0.35,
                   filter: active ? 'drop-shadow(0 0 4px #6366f160)' : 'none',
                   transition: 'all .2s' }}>
      {map[value]}
    </span>
  );
}

// ── Read-only field ──────────────────────────────────────────────────────────
function ROField({ label, value, multiline }) {
  return (
    <div className="ro-field">
      <span className="ro-label">{label}</span>
      {multiline
        ? <div className="ro-value ro-multiline">{value || <span className="ro-empty">—</span>}</div>
        : <div className="ro-value">{value || <span className="ro-empty">—</span>}</div>
      }
    </div>
  );
}

// ── Main component ───────────────────────────────────────────────────────────
export default function App() {
  const dispatch = useDispatch();
  const { form, messages, suggestions, loading, error, lastSavedId } =
    useSelector((s) => s.interaction);

  const [chatInput, setChatInput]   = useState('');
  const [activeTool, setActiveTool] = useState('Log Interaction');
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory]       = useState([]);
  const chatEndRef = useRef(null);

  // auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchHistory = async () => {
    try {
      const r = await axios.get(`${API}/api/interactions`);
      setHistory(r.data);
      dispatch(setRecentInteractions(r.data));
    } catch (_) {}
  };

  // ── Send chat message to agent ─────────────────────────────────────────────
  const send = async () => {
    const msg = chatInput.trim();
    if (!msg || loading) return;

    dispatch(appendMessage({ role: 'user', content: msg }));
    setChatInput('');
    dispatch(setLoading(true));
    dispatch(setError(''));

    try {
      const { data } = await axios.post(`${API}/api/interaction`, {
        tool:           activeTool,
        current_fields: form,
        message:        msg,
      });

      // ← THE KEY STEP: AI returned form_fields → auto-populate the form
      if (data.form_fields) {
        dispatch(setFormFields(data.form_fields));
      }
      if (data.interaction_id) {
        dispatch(setLastSavedId(data.interaction_id));
        fetchHistory();
      }
      if (data.suggestions?.length) {
        dispatch(setSuggestions(data.suggestions));
      }

      dispatch(appendMessage({ role: 'assistant', content: data.reply }));

    } catch (err) {
      const msg = err.response?.data?.detail || 'Could not reach the AI agent.';
      dispatch(setError(msg));
      dispatch(appendMessage({ role: 'error', content: msg }));
    } finally {
      dispatch(setLoading(false));
    }
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  };

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="page-bg">
      <div className="split-layout">

        {/* ════════════════════════════════════════════════
            LEFT — Read-only form panel
        ════════════════════════════════════════════════ */}
        <div className="form-card">

          {/* Header */}
          <div className="form-card-header">
            <h1 className="page-heading">Log HCP Interaction</h1>
            <div className="header-actions">
              <button className="hdr-btn" onClick={() => { setShowHistory(!showHistory); fetchHistory(); }}>
                📋 History {history.length > 0 && <span className="cnt">{history.length}</span>}
              </button>
              <button className="hdr-btn hdr-btn--danger" onClick={() => dispatch(resetAll())}>
                Reset
              </button>
            </div>
          </div>

          {/* Saved banner */}
          {lastSavedId && (
            <div className="saved-banner">
              ✅ Interaction saved &nbsp;<code>{lastSavedId.slice(0,8)}…</code>
              <button className="dismiss" onClick={() => dispatch(setLastSavedId(null))}>✕</button>
            </div>
          )}

          {/* AI control notice */}
          <div className="ai-notice">
            <span className="ai-notice-dot" />
            This form is controlled by the AI assistant. Type in the chat panel →
          </div>

          {/* History panel */}
          {showHistory && (
            <div className="history-panel">
              <p className="history-title">Recent Interactions</p>
              {history.length === 0
                ? <p className="history-empty">No interactions yet.</p>
                : history.map(r => (
                    <div key={r.id} className="history-row">
                      <span className="history-hcp">{r.hcp_name}</span>
                      <span className="history-type">{r.interaction_type} · {r.date}</span>
                      <span className={`history-sent history-sent--${(r.hcp_sentiment||'neutral').toLowerCase()}`}>
                        {r.hcp_sentiment}
                      </span>
                    </div>
                  ))
              }
            </div>
          )}

          {/* ── Interaction Details section ── */}
          <div className="form-section">
            <p className="form-section-title">Interaction Details</p>

            <div className="ro-grid-2">
              <ROField label="HCP Name"         value={form.hcpName} />
              <ROField label="Interaction Type" value={form.interactionType} />
            </div>
            <div className="ro-grid-2">
              <ROField label="Date" value={form.date} />
              <ROField label="Time" value={form.time} />
            </div>
            <ROField label="Attendees" value={form.attendees} />
            <ROField label="Topics Discussed" value={form.topicsDiscussed} multiline />

            {/* Voice note stub */}
            <div className="voice-stub">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8"/>
              </svg>
              Summarize from Voice Note <span className="muted">(Requires Consent)</span>
            </div>
          </div>

          {/* ── Materials ── */}
          <div className="form-section">
            <p className="form-section-title">Materials Shared / Samples Distributed</p>

            <div className="mat-box">
              <div className="mat-box-header">
                <span>Materials Shared</span>
                <span className="mat-box-btn">🔍 Search/Add</span>
              </div>
              {form.materialsShared
                ? <p className="mat-val">{form.materialsShared}</p>
                : <p className="mat-empty">No materials added.</p>}
            </div>

            <div className="mat-box">
              <div className="mat-box-header">
                <span>Samples Distributed</span>
                <span className="mat-box-btn">＋ Add Sample</span>
              </div>
              {form.samplesDistributed
                ? <p className="mat-val">{form.samplesDistributed}</p>
                : <p className="mat-empty">No samples added.</p>}
            </div>
          </div>

          {/* ── Sentiment ── */}
          <div className="form-section">
            <p className="form-section-title">Observed/Inferred HCP Sentiment</p>
            <div className="sentiment-row">
              {SENTIMENTS.map(s => (
                <label key={s} className="sentiment-opt">
                  <SentimentIcon value={s} active={form.hcpSentiment === s} />
                  <span className={`sentiment-lbl ${form.hcpSentiment === s ? 'sentiment-lbl--active' : ''}`}>
                    {s}
                  </span>
                  {/* radio is hidden but accessible */}
                  <input type="radio" name="sent" value={s}
                    checked={form.hcpSentiment === s} readOnly className="sr-only" />
                </label>
              ))}
            </div>
          </div>

          {/* ── Outcomes ── */}
          <div className="form-section">
            <ROField label="Outcomes" value={form.outcomes} multiline />
          </div>

          {/* ── Follow-up Actions ── */}
          <div className="form-section">
            <ROField label="Follow-up Actions" value={form.followUpActions} multiline />

            {suggestions.length > 0 && (
              <div className="suggestions-block">
                <p className="suggestions-title">AI Suggested Follow-ups:</p>
                {suggestions.map((s, i) => (
                  <p key={i} className="suggestion-item"
                    onClick={() => dispatch(setFormFields({
                      followUpActions: form.followUpActions
                        ? `${form.followUpActions}\n• ${s}` : `• ${s}`
                    }))}>
                    + {s}
                  </p>
                ))}
              </div>
            )}
          </div>

        </div>

        {/* ════════════════════════════════════════════════
            RIGHT — AI Chat Panel
        ════════════════════════════════════════════════ */}
        <div className="chat-card">

          {/* Header */}
          <div className="chat-hdr">
            <div className="chat-avatar">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="8" r="4"/>
                <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
              </svg>
            </div>
            <div>
              <p className="chat-title">AI Assistant</p>
              <p className="chat-sub">Log interaction via chat</p>
            </div>
          </div>

          {/* Tool selector */}
          <div className="tool-row">
            <select
              className="tool-select"
              value={activeTool}
              onChange={e => setActiveTool(e.target.value)}
            >
              {TOOLS.map(t => (
                <option key={t.value} value={t.value}>{t.value}</option>
              ))}
            </select>
            <span className="tool-desc">
              {TOOLS.find(t => t.value === activeTool)?.desc}
            </span>
          </div>

          {/* Messages */}
          <div className="chat-msgs">
            {messages.length === 0 && (
              <div className="chat-hint">
                Log interaction details here (e.g., "Met Dr. Smith, discussed
                Product X efficacy, positive sentiment, shared brochure") or ask for help.
              </div>
            )}

            {messages.map((m, i) => (
              <div key={i} className={`bubble bubble--${m.role}`}>
                <p className="bubble-text">{m.content}</p>
              </div>
            ))}

            {loading && (
              <div className="bubble bubble--assistant">
                <p className="bubble-text typing">
                  <span /><span /><span />
                </p>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Input */}
          <div className="chat-input-bar">
            <input
              className="chat-input"
              value={chatInput}
              onChange={e => setChatInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Describe interaction..."
              disabled={loading}
            />
            <button
              className="log-btn"
              onClick={send}
              disabled={loading || !chatInput.trim()}
            >
              {loading
                ? <span className="spin" />
                : <>
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M22 2L11 13M22 2L15 22l-4-9-9-4 20-7z"/>
                    </svg>
                    Log
                  </>
              }
            </button>
          </div>

          {error && <p className="chat-error">{error}</p>}
        </div>

      </div>
    </div>
  );
}
