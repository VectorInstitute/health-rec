import { create } from 'zustand';

interface Service {
  id: string;
  PublicName: string;
  Description?: string;
  [key: string]: unknown;
}

interface Recommendation {
  message: string;
  services: Service[];
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
