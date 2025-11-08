/**
 * API Service for communicating with the backend
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface User {
  user_id: string;
  username: string;
  email?: string;
  created_at: string;
  last_active: string;
}

export interface Module {
  module_id: string;
  domain: string;
  subject: string;
  topic: string;
  title: string;
  description: string;
  prerequisites: string[];
  learning_objectives: string[];
  difficulty_level: number;
  estimated_time: number;
  created_at: string;
  version: string;
}

export interface LessonContent {
  session_id: string;
  content: string;
  modality: string;
  selection_reason: string;
  module: {
    id: string;
    title: string;
    objectives: string[];
    estimated_time: number;
  };
}

export interface ChatResponse {
  response: string;
  session_id: string;
  timestamp: string;
}

export interface ProgressOverview {
  user_id: string;
  total_sessions: number;
  modules_in_progress: number;
  modules_completed: number;
  modules_mastered: number;
  total_time_spent: number;
  learning_insights: any;
}

export const authAPI = {
  register: async (username: string, email: string, password: string): Promise<User> => {
    const response = await api.post('/auth/register', { username, email, password });
    return response.data;
  },

  login: async (username: string, password: string): Promise<User> => {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  },

  getUser: async (username: string): Promise<User> => {
    const response = await api.get(`/auth/users/${username}`);
    return response.data;
  },
};

export const contentAPI = {
  listModules: async (domain?: string, subject?: string): Promise<Module[]> => {
    const params: any = {};
    if (domain) params.domain = domain;
    if (subject) params.subject = subject;
    const response = await api.get('/content/modules', { params });
    return response.data;
  },

  getModule: async (moduleId: string): Promise<Module> => {
    const response = await api.get(`/content/modules/${moduleId}`);
    return response.data;
  },
};

export const sessionAPI = {
  startSession: async (
    userId: string,
    moduleId: string,
    forceModality?: string
  ): Promise<LessonContent> => {
    const response = await api.post(
      `/sessions/start?user_id=${userId}`,
      { module_id: moduleId, force_modality: forceModality }
    );
    return response.data;
  },

  recordEngagement: async (
    sessionId: string,
    signalType: string,
    signalValue: number,
    context?: any
  ) => {
    await api.post(`/sessions/${sessionId}/engagement`, {
      signal_type: signalType,
      signal_value: signalValue,
      context,
    });
  },

  completeSession: async (
    sessionId: string,
    comprehensionScore: number,
    engagementScore: number
  ) => {
    await api.post(`/sessions/${sessionId}/complete`, {
      comprehension_score: comprehensionScore,
      engagement_score: engagementScore,
    });
  },
};

export const chatAPI = {
  sendMessage: async (sessionId: string, message: string): Promise<ChatResponse> => {
    const response = await api.post(`/chat/${sessionId}/message`, { message });
    return response.data;
  },

  getComprehensionCheck: async (sessionId: string) => {
    const response = await api.get(`/chat/${sessionId}/comprehension-check`);
    return response.data;
  },

  evaluateComprehension: async (sessionId: string, answer: string) => {
    const response = await api.post(`/chat/${sessionId}/comprehension-check`, { answer });
    return response.data;
  },
};

export const progressAPI = {
  getOverview: async (userId: string): Promise<ProgressOverview> => {
    const response = await api.get(`/progress/${userId}/overview`);
    return response.data;
  },

  getUserModules: async (userId: string) => {
    const response = await api.get(`/progress/${userId}/modules`);
    return response.data;
  },

  getModuleProgress: async (userId: string, moduleId: string) => {
    const response = await api.get(`/progress/${userId}/modules/${moduleId}`);
    return response.data;
  },
};

// Dynamic Learning APIs
export interface AssessmentResponse {
  status: string;
  question?: string;
  questions_asked?: number;
  assessment_complete: boolean;
  knowledge_level?: number;
  summary?: string;
  gaps?: string[];
  starting_point?: string;
  learning_objectives?: string[];
}

export interface ConversationMessage {
  role: string;
  content: string;
}

export const dynamicAPI = {
  startAssessment: async (userId: string, subject: string): Promise<AssessmentResponse> => {
    const response = await api.post(`/dynamic/assess/start?user_id=${userId}`, { subject });
    return response.data;
  },

  continueAssessment: async (
    userId: string,
    subject: string,
    conversationHistory: ConversationMessage[]
  ): Promise<AssessmentResponse> => {
    const response = await api.post(`/dynamic/assess/continue?user_id=${userId}`, {
      subject,
      conversation_history: conversationHistory,
    });
    return response.data;
  },

  createModule: async (userId: string, subject: string, assessment: any): Promise<Module> => {
    const response = await api.post(`/dynamic/create-module?user_id=${userId}`, {
      subject,
      assessment,
    });
    return response.data;
  },
};

// Settings API
export interface UserSettings {
  // AI Provider Settings
  preferred_provider?: string;
  anthropic_api_key?: string;
  anthropic_model: string;
  openai_api_key?: string;
  openai_model: string;
  google_api_key?: string;
  google_model: string;

  // Learning Preferences
  default_modality?: string;
  session_reminders: boolean;
  spaced_repetition_enabled: boolean;

  // UI Preferences
  theme: string;
  language: string;

  updated_at?: string;
}

export const settingsAPI = {
  getSettings: async (userId: string): Promise<UserSettings> => {
    const response = await api.get(`/settings/${userId}`);
    return response.data;
  },

  updateSettings: async (userId: string, settings: Partial<UserSettings>): Promise<UserSettings> => {
    const response = await api.put(`/settings/${userId}`, settings);
    return response.data;
  },
};

export default api;
