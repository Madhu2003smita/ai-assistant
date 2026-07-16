import { createSlice } from '@reduxjs/toolkit';

const today = new Date().toISOString().split('T')[0];
const now   = new Date().toTimeString().slice(0, 5);

const emptyForm = {
  hcpName: '',
  date: today,
  time: now,
  interactionType: 'Meeting',
  attendees: '',
  topicsDiscussed: '',
  materialsShared: '',
  samplesDistributed: '',
  hcpSentiment: 'Neutral',
  outcomes: '',
  followUpActions: '',
  interaction_id: null,
};

const interactionSlice = createSlice({
  name: 'interaction',
  initialState: {
    form: { ...emptyForm },         
    messages: [],
    suggestions: [],
    recentInteractions: [],
    loading: false,
    error: '',
    lastSavedId: null,
  },
  reducers: {
    
    setFormFields(state, { payload }) {
      state.form = { ...state.form, ...payload };
    },
    appendMessage(state, { payload }) {
      state.messages.push(payload);
    },
    setSuggestions(state, { payload }) {
      state.suggestions = payload;
    },
    setLoading(state, { payload }) {
      state.loading = payload;
    },
    setError(state, { payload }) {
      state.error = payload;
    },
    setLastSavedId(state, { payload }) {
      state.lastSavedId = payload;
      state.form.interaction_id = payload;
    },
    setRecentInteractions(state, { payload }) {
      state.recentInteractions = payload;
    },
    resetAll(state) {
      state.form = { ...emptyForm };
      state.messages = [];
      state.suggestions = [];
      state.error = '';
      state.lastSavedId = null;
    },
  },
});

export const {
  setFormFields,
  appendMessage,
  setSuggestions,
  setLoading,
  setError,
  setLastSavedId,
  setRecentInteractions,
  resetAll,
} = interactionSlice.actions;

export default interactionSlice.reducer;
