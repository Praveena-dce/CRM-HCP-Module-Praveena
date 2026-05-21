import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/interactions';

export const sendChatMessage = createAsyncThunk(
  'interactions/sendChatMessage',
  async (message, { getState, rejectWithValue }) => {
    try {
      const { currentInteraction } = getState().interactions;
      const response = await axios.post(`${API_URL}/chat`, {
        message,
        interaction_id: currentInteraction?.id || null
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.response?.data);
    }
  }
);

export const createInteraction = createAsyncThunk(
  'interactions/createInteraction',
  async (data, { rejectWithValue }) => {
    try {
      const response = await axios.post(API_URL, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const updateInteraction = createAsyncThunk(
  'interactions/updateInteraction',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      const response = await axios.put(`${API_URL}/${id}`, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const fetchInteractions = createAsyncThunk(
  'interactions/fetchInteractions',
  async (_, { rejectWithValue }) => {
    try {
      const response = await axios.get(API_URL);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

const interactionSlice = createSlice({
  name: 'interactions',
  initialState: {
    currentInteraction: null,
    interactions: [],
    chatHistory: [],
    loading: false,
    error: null,
  },
  reducers: {
    setCurrentInteraction: (state, action) => {
      state.currentInteraction = action.payload;
    },
    addChatMessage: (state, action) => {
      state.chatHistory.push(action.payload);
    },
    clearChatHistory: (state) => {
      state.chatHistory = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.loading = false;
        const userMessage = typeof action.meta.arg === 'string' ? action.meta.arg : action.meta.arg?.message || '';
        
        if (action.payload.interaction) {
          state.currentInteraction = action.payload.interaction;
        }
        
        state.chatHistory.push({ type: 'user', text: userMessage });
        state.chatHistory.push({ type: 'ai', text: action.payload.response });
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(createInteraction.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createInteraction.fulfilled, (state, action) => {
        state.loading = false;
        state.interactions.unshift(action.payload);
        state.currentInteraction = action.payload;
      })
      .addCase(createInteraction.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(updateInteraction.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateInteraction.fulfilled, (state, action) => {
        state.loading = false;
        state.currentInteraction = action.payload;
        const index = state.interactions.findIndex(i => i.id === action.payload.id);
        if (index !== -1) {
          state.interactions[index] = action.payload;
        }
      })
      .addCase(updateInteraction.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchInteractions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.loading = false;
        state.interactions = action.payload;
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { setCurrentInteraction, addChatMessage, clearChatHistory } = interactionSlice.actions;
export default interactionSlice.reducer;
