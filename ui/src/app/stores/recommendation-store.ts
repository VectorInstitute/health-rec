import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import { Service } from '../types/service';

export interface Query {
  query: string;
  latitude: number | null;
  longitude: number | null;
  radius: number | null;
}

export interface Recommendation {
  message: string;
  services: Service[];
  is_emergency: boolean;
  is_out_of_scope: boolean;
  no_services_found: boolean;
  query: Query;
}

export interface RecommendationStore {
  recommendation: Recommendation | null;
  query: Query | null;
  setRecommendation: (recommendation: Recommendation | null) => void;
  setStoreQuery: (query: Query) => void;
}

export const useRecommendationStore = create<RecommendationStore>()(
  persist(
    (set) => ({
      recommendation: null,
      query: null,
      setRecommendation: (recommendation: Recommendation | null) => set({ recommendation }),
      setStoreQuery: (query: Query) => set({ query }),
    }),
    {
      name: 'recommendation-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
);
