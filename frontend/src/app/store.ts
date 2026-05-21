import { configureStore, ThunkAction, Action } from '@reduxjs/toolkit';
import interactionReducer from '../features/interaction/interactionSlice';

export const store = configureStore({
  reducer: {
    interaction: interactionReducer,
  },
});

export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>;