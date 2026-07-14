import { create } from 'zustand';
import apiService from '@services/api';

interface LearningMetrics {
  overall_success_rate: number;
  average_engagement: number;
  dropout_risk: 'low' | 'medium' | 'high';
  predicted_next_success_rate: number;
  themes_mastered: string[];
  themes_struggling: string[];
  total_activities: number;
  successful_activities: number;
}

interface LearningState {
  childId: string | null;
  metrics: LearningMetrics | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  setChildId: (childId: string) => void;
  fetchMetrics: (childId: string) => Promise<void>;
  clearError: () => void;
}

export const useLearningStore = create<LearningState>((set) => ({
  childId: null,
  metrics: null,
  isLoading: false,
  error: null,

  setChildId: (childId: string) => set({ childId }),

  fetchMetrics: async (childId: string) => {
    set({ isLoading: true, error: null });
    try {
      const metrics = await apiService.getLearningMetrics(childId);
      set({
        metrics,
        childId,
        isLoading: false,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Erro ao carregar métricas',
        isLoading: false,
      });
    }
  },

  clearError: () => set({ error: null }),
}));
