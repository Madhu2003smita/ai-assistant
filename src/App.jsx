import { useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import axios from 'axios';
import { appendMessage, resetForm, setError, setLoading, setSuggestedFollowUps, updateField } from './features/interaction/interactionSlice';

const toolOptions = [
  'Summarize from Voice Note',
  'Recommend next best action',
  'Suggest follow-up timing',
  'Prepare account plan',
  'Draft outreach email',
];

function App() {
  const dispatch = useDispatch();
  const { submission, messages, suggestedFollowUps, loading, error } = useSelector((state) => state.interaction);
  const [chatInput, setChatInput] = useState('');
  const [selectedTool, setSelectedTool] = useState(toolOptions[0]);

  const summary = useMemo(() => {
    const parts = [submission.hcpName, submission.date, submission.interactionType, submission.topicsDiscussed, submission.followUpActions].filter(Boolean);
    return parts.join(' • ');
  }, [submission]);

  const handleChange = (field) => (event) => {
    dispatch(updateField({ field, value: event.target.value }));
  };

  const runAgent = async (mode = 'form') => {
    dispatch(setLoading(true));
    dispatch(setError(''));

    try {
      const payload = {
        mode,
        tool: selectedTool,
        submission,
        message: chatInput,
      };
      const response = await axios.post('http://localhost:8000/api/interaction', payload);
      const reply = response.data.reply || response.data.message || 'Agent completed the action.';
      const suggestions = response.data.suggestions || [];
      dispatch(appendMessage({ role: 'assistant', content: reply }));
      if (suggestions.length > 0) {
        dispatch(setSuggestedFollowUps(suggestions));
      }
      if (mode === 'chat') {
        dispatch(appendMessage({ role: 'user', content: chatInput }));
        setChatInput('');
      }
    } catch (err) {
      dispatch(setError(err.response?.data?.detail || 'Unable to contact the AI agent.'));
    } finally {
      dispatch(setLoading(false));
    }
  };

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">AI-First CRM • HCP Module</p>
          <h1>Log HCP Interaction</h1>
          <p className="subtext">Capture comprehensive HCP engagement details with AI-powered insights and suggestions.</p>
        </div>
      </header>

      <main className="interaction-grid">
        <section className="card form-panel">
          <h2>Interaction Details</h2>
          
          <div className="form-row">
            <label style={{ flex: 1 }}>
              HCP Name
              <input value={submission.hcpName} onChange={handleChange('hcpName')} placeholder="Search or select HCP..." />
            </label>
            <label style={{ flex: 0.6 }}>
              Interaction Type
              <select value={submission.interactionType} onChange={handleChange('interactionType')}>
                <option>Meeting</option>
                <option>Call</option>
                <option>Email</option>
                <option>Webinar</option>
                <option>Conference</option>
              </select>
            </label>
          </div>

          <div className="form-row">
            <label style={{ flex: 0.5 }}>
              Date
              <input type="date" value={submission.date} onChange={handleChange('date')} />
            </label>
            <label style={{ flex: 0.5 }}>
              Time
              <input type="time" value={submission.time} onChange={handleChange('time')} />
            </label>
          </div>

          <label>
            Attendees
            <input value={submission.attendees} onChange={handleChange('attendees')} placeholder="Enter names or search..." />
          </label>

          <label>
            Topics Discussed
            <textarea value={submission.topicsDiscussed} onChange={handleChange('topicsDiscussed')} placeholder="Enter key discussion points..." rows={3} />
          </label>

          <h3 style={{ marginTop: '16px', marginBottom: '8px' }}>Materials Shared / Samples Distributed</h3>
          <label>
            Materials Shared
            <input value={submission.materialsShared} onChange={handleChange('materialsShared')} placeholder="Any materials validated" />
          </label>
          <label>
            Samples Distributed
            <input value={submission.samplesDistributed} onChange={handleChange('samplesDistributed')} placeholder="Any samples validated" />
          </label>

          <h3 style={{ marginTop: '16px', marginBottom: '8px' }}>Observed/Inferred HCP Sentiment</h3>
          <div className="radio-group">
            {['Positive', 'Neutral', 'Negative'].map((sentiment) => (
              <label key={sentiment} style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                <input
                  type="radio"
                  name="sentiment"
                  value={sentiment}
                  checked={submission.hcpSentiment === sentiment}
                  onChange={handleChange('hcpSentiment')}
                />
                {sentiment}
              </label>
            ))}
          </div>

          <label style={{ marginTop: '16px' }}>
            Outcomes
            <textarea value={submission.outcomes} onChange={handleChange('outcomes')} placeholder="Key outcomes or agreements..." rows={3} />
          </label>

          <label>
            Follow-up Actions
            <textarea value={submission.followUpActions} onChange={handleChange('followUpActions')} placeholder="Enter next steps or tasks..." rows={3} />
          </label>

          <div className="actions" style={{ marginTop: '16px' }}>
            <button onClick={() => runAgent('form')} disabled={loading} style={{ flex: 1 }}>
              {loading ? 'Processing...' : 'Submit to AI Agent'}
            </button>
            <button className="secondary" onClick={() => dispatch(resetForm())}>Reset</button>
          </div>
        </section>

        <section className="card assistant-panel">
          <h2>AI Assistant</h2>
          <p style={{ fontSize: '0.9rem', color: '#567', marginBottom: '12px' }}>Log interaction via chat</p>
          
          <label>
            Tool
            <select value={selectedTool} onChange={(e) => setSelectedTool(e.target.value)}>
              {toolOptions.map((tool) => (
                <option key={tool} value={tool}>{tool}</option>
              ))}
            </select>
          </label>

          <textarea 
            value={chatInput} 
            onChange={(e) => setChatInput(e.target.value)} 
            placeholder="Describe the interaction or ask for suggestions..." 
            rows={4} 
          />
          
          <div className="actions">
            <button onClick={() => runAgent('chat')} disabled={loading || !chatInput.trim()}>
              {loading ? 'Thinking...' : 'Send'}
            </button>
          </div>

          <div className="chat-window">
            {messages.length === 0 && suggestedFollowUps.length === 0 && (
              <p style={{ color: '#999', fontSize: '0.9rem', marginTop: '12px' }}>No messages yet. Start by submitting the form or asking a question.</p>
            )}
            
            {suggestedFollowUps.length > 0 && (
              <div style={{ marginBottom: '12px' }}>
                <p style={{ fontWeight: '600', fontSize: '0.85rem', color: '#3f6ed8', marginBottom: '6px' }}>Suggested Follow-ups:</p>
                <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '0.9rem' }}>
                  {suggestedFollowUps.map((item, idx) => (
                    <li key={idx} style={{ marginBottom: '4px', color: '#567' }}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {messages.map((message, index) => (
              <div key={`${message.role}-${index}`} className={`bubble ${message.role}`} style={{ marginBottom: '8px' }}>
                <strong>{message.role === 'assistant' ? 'Agent' : 'You'}:</strong> {message.content}
              </div>
            ))}
            {error ? <div className="bubble error" style={{ marginTop: '8px' }}>{error}</div> : null}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
