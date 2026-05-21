import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface InteractionState {
  hcp_name: string;
  interaction_type: string;
  date: string;
  time: string;
  attendees: string;
  topics_discussed: string;
  summary: string;
  materials_shared: string;
  samples_distributed: string;
  sentiment: string;
  outcomes: string;
  loading: boolean;
}

const initialState: InteractionState = {
  hcp_name: '',
  interaction_type: 'Meeting',
  date: new Date().toISOString().split('T')[0],
  time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
  attendees: '',
  topics_discussed: '',
  summary: '',
  materials_shared: '',
  samples_distributed: '',
  sentiment: 'Neutral',
  outcomes: '',
  loading: false,
};

export const interactionSlice = createSlice({
  name: 'interaction',
  initialState,
  reducers: {
    updateField: (state, action: PayloadAction<{ field: keyof InteractionState; value: string }>) => {
      state[action.payload.field] = action.payload.value;
    },
    setFormData: (state, action: PayloadAction<Partial<InteractionState>>) => {
      return { ...state, ...action.payload };
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    resetForm: () => initialState,
  },
});

export const { updateField, setFormData, setLoading, resetForm } = interactionSlice.actions;
export default interactionSlice.reducer;