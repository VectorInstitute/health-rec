import { create } from 'zustand';
import { Service } from '../types/service';

export interface Recommendation {
  message: string;
  services: Service[];
  is_emergency: boolean;
}

interface RecommendationStore {
  recommendation: Recommendation | null;
  query: string | null;
  setRecommendation: (recommendation: Recommendation | null) => void;
  setStoreQuery: (query: string) => void;
}

export const useRecommendationStore = create<RecommendationStore>((set) => ({
  recommendation: null,
  query: null,
  setRecommendation: (recommendation) => set({ recommendation }),
  setStoreQuery: (query) => set({ query }),
}));
