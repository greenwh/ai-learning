/**
 * Global state management with Zustand
 */
import { create } from 'zustand';
import { User, Module, LessonContent, ProgressOverview } from '../services/api';

interface AppState {
  // User state
  user: User | null;
  setUser: (user: User | null) => void;

  // Current learning session
  currentSession: LessonContent | null;
  setCurrentSession: (session: LessonContent | null) => void;

  // Available modules
  modules: Module[];
  setModules: (modules: Module[]) => void;

  // Progress
  progress: ProgressOverview | null;
  setProgress: (progress: ProgressOverview | null) => void;

  // UI state
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;

  error: string | null;
  setError: (error: string | null) => void;

  // Session tracking
  sessionStartTime: number | null;
  setSessionStartTime: (time: number | null) => void;

  questionsAsked: number;
  incrementQuestionsAsked: () => void;
  resetQuestionsAsked: () => void;
}

export const useStore = create<AppState>((set) => ({
  // User state
  user: null,
  setUser: (user) => set({ user }),

  // Current learning session
  currentSession: null,
  setCurrentSession: (session) => set({ currentSession: session }),

  // Available modules
  modules: [],
  setModules: (modules) => set({ modules }),

  // Progress
  progress: null,
  setProgress: (progress) => set({ progress }),

  // UI state
  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),

  error: null,
  setError: (error) => set({ error }),

  // Session tracking
  sessionStartTime: null,
  setSessionStartTime: (time) => set({ sessionStartTime: time }),

  questionsAsked: 0,
  incrementQuestionsAsked: () => set((state) => ({ questionsAsked: state.questionsAsked + 1 })),
  resetQuestionsAsked: () => set({ questionsAsked: 0 }),
}));
