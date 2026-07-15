import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  submission: {
    hcpName: '',
    date: '',
    time: '',
    interactionType: 'Meeting',
    attendees: '',
    topicsDiscussed: '',
    materialsShared: '',
    samplesDistributed: '',
    hcpSentiment: 'Neutral',
    outcomes: '',
    followUpActions: '',
  },
  messages: [],
  suggestedFollowUps: [],
  loading: false,
  error: '',
};

const interactionSlice = createSlice({
  name: 'interaction',
  initialState,
  reducers: {
    updateField(state, action) {
      const { field, value } = action.payload;
      state.submission[field] = value;
    },
    appendMessage(state, action) {
      state.messages.push(action.payload);
    },
    setLoading(state, action) {
      state.loading = action.payload;
    },
    setError(state, action) {
      state.error = action.payload;
    },
    setSuggestedFollowUps(state, action) {
      state.suggestedFollowUps = action.payload;
    },
    resetForm(state) {
      state.submission = initialState.submission;
      state.messages = [];
      state.suggestedFollowUps = [];
      state.error = '';
    },
  },
});

export const { updateField, appendMessage, setLoading, setError, setSuggestedFollowUps, resetForm } = interactionSlice.actions;
export default interactionSlice.reducer;
