# Demo Video Guide – AI-First HCP CRM

## Recording Instructions (10-15 minutes)

### Part 1: Setup & Overview (1-2 min)
- Show the terminal with both servers running
- Show the GitHub repository
- Explain: "This is an AI-First CRM for logging HCP interactions with intelligent recommendations"

### Part 2: Frontend Overview (1-2 min)
- Open http://localhost:5174 in browser
- Show the header and title
- Pan across the form (left) and AI Assistant (right) panels
- Explain the two main interaction modes

### Part 3: Test Form Submission with Positive Sentiment (2-3 min)
**Fill the form:**
- HCP Name: `Dr. Sarah Johnson`
- Date: Pick today's date
- Time: `14:30`
- Interaction Type: `Meeting`
- Attendees: `Dr. Johnson, Sales Rep Maria`
- Topics Discussed: `Discussed latest clinical trial results for oncology treatment`
- Materials Shared: `Clinical data packets`
- Samples: `Sample medications`
- **HCP Sentiment: SELECT "Positive"** ← KEY FOR SHOWING SENTIMENT LOGIC
- Outcomes: `HCP expressed strong interest in pilot program`
- Follow-up Actions: `Schedule follow-up meeting, Send proposal`

**Click "Submit to AI Agent"**
- Show the AI reply appearing
- Show the 3-5 suggested follow-ups appearing in the green box
- Narrate: "The AI agent generates context-aware suggestions based on the sentiment and outcomes"

### Part 4: Test with Negative Sentiment (2-3 min)
- Clear the form (click Reset)
- **Fill similar form but with:**
  - Outcomes: `HCP expressed concerns about efficacy and side effects`
  - **HCP Sentiment: SELECT "Negative"**
  
**Click "Submit to AI Agent"**
- Show different suggestions appearing
- Narrate: "Notice how the suggestions changed because sentiment is Negative. The AI recommends addressing concerns with evidence"

### Part 5: Demonstrate Each AI Tool (4-5 min)

**In the right panel, AI Assistant:**

1. **Tool 1: Summarize from Voice Note**
   - Type: "Can you summarize this oncology interaction?"
   - Show the response
   - Show suggested follow-ups

2. **Tool 2: Recommend next best action**
   - Change tool dropdown
   - Type: "What should we do next?"
   - Show response with action-oriented suggestions

3. **Tool 3: Suggest follow-up timing**
   - Change tool dropdown
   - Type: "When should we follow up?"
   - Show timing recommendations

4. **Tool 4: Prepare account plan**
   - Change tool dropdown
   - Type: "Help me prepare an account plan"
   - Show strategic guidance

5. **Tool 5: Draft outreach email**
   - Change tool dropdown
   - Type: "Draft an email to Dr. Johnson"
   - Show email template suggestions

### Part 6: Show Backend API (1-2 min)
- Open terminal
- Run the API test command
- Show JSON request and response
- Explain: "The backend processes each interaction through our LangGraph-style tool router"

### Part 7: Wrap-up (1 min)
- Summarize key features:
  - ✅ Comprehensive HCP interaction logging
  - ✅ 5 specialized AI tools
  - ✅ Sentiment-aware recommendations
  - ✅ Real-time suggested follow-ups
  - ✅ Full React + Redux + Python stack
- Show GitHub repo link
- Thank you

---

## Recording Tips

✅ **Use screen recording software:**
- Windows: Use built-in Xbox Game Bar (Win + G)
- Or use OBS Studio (free)
- Or use Loom (easy, web-based)

✅ **Audio:**
- Speak clearly and slowly
- Explain what you're doing as you do it
- Highlight AI-specific features

✅ **Pacing:**
- Pause after actions to show results
- Use cursor highlighting to point out features
- Let AI responses display fully before moving on

✅ **Demo Flow:**
- Start with positive sentiment → good suggestions
- Show negative sentiment → different suggestions
- All 5 tools in action
- API verification
- Clean, professional appearance

---

## Video Submission

After recording:
1. Save as MP4 or WebM
2. Upload to Google Drive or YouTube
3. Share link in assignment submission
4. Include video link in GitHub README

---

## Key Points to Emphasize

🎯 **Functionality:**
- "The app successfully logs comprehensive HCP interactions"
- "AI generates context-aware insights based on the data"
- "Sentiment directly influences AI recommendations"

🎯 **Technology:**
- "React + Redux frontend with modern UI"
- "Python backend with LangGraph-style tool routing"
- "Real-time API communication"
- "All 5 AI tools working independently"

🎯 **Assignment Compliance:**
- "All assignment requirements met"
- "GitHub repository with clean code"
- "Comprehensive README documentation"
- "Working demo of all features"
