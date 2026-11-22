import axios from 'axios';
import type { IntakeChatResponse, IntakeState, NextQuestion } from '../types';

const api = axios.create({
  baseURL: '/api/v1',
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
};

export default api;
