import { create } from 'zustand';

interface Recommendation {
  message: string;
  services: any[];
  is_emergency: boolean;
}

interface RecommendationStore {
  recommendation: Recommendation | null;
  setRecommendation: (recommendation: Recommendation) => void;
}

export const useRecommendationStore = create<RecommendationStore>((set) => ({
  recommendation: null,
  setRecommendation: (recommendation) => set({ recommendation }),
}));
