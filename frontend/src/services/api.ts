import axios from 'axios';
import type { IntakeChatResponse, IntakeState, NextQuestion } from '../types';

let rawBase = (import.meta.env.VITE_API_BASE_URL || '/api/v1').trim();

// Strip any trailing slashes
while (rawBase.endsWith('/')) {
  rawBase = rawBase.slice(0, -1);
}

// Automatically ensure /api/v1 suffix is present regardless of how VITE_API_BASE_URL was configured in Vercel
if (!rawBase.endsWith('/api/v1')) {
  rawBase = `${rawBase}/api/v1`;
}

const baseURL = rawBase;

const api = axios.create({
  baseURL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const intakeApi = {
  chat: (message: string, sessionToken: string) =>
    api.post<IntakeChatResponse>('/intake/chat/', { message, session_token: sessionToken }),
  getState: (sessionToken: string) =>
    api.get<{ session_token: string; state: IntakeState; next_question: NextQuestion | null }>(
      `/intake/state/?session_token=${sessionToken}`
    ),
  correct: (sessionToken: string, field: string, value: any) =>
    api.post<{ session_token: string; state: IntakeState; next_question: NextQuestion | null }>(
      '/intake/correct/',
      { session_token: sessionToken, field, value }
    ),
  restart: (sessionToken: string) =>
    api.post<{ session_token: string; state: IntakeState; next_question: NextQuestion | null }>(
      '/intake/restart/',
      { session_token: sessionToken }
    ),
  voiceIntake: (formData: FormData) =>
    api.post('/intake/voice/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 30000,
    }),
  confirmVoice: (sessionToken: string, confirmedFields: Record<string, any>) =>
    api.post('/intake/confirm_voice/', {
      session_token: sessionToken,
      confirmed_fields: confirmedFields,
    }),
};

export default api;
