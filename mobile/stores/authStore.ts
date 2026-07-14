import { create } from 'zustand';
import * as SecureStore from 'expo-secure-store';
import apiService from '@services/api';

interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'school_admin' | 'teacher' | 'guardian' | 'child';
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isLoading: false,
  isAuthenticated: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiService.login(email, password);
      set({
        user: response.user,
        token: response.access_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Erro ao fazer login',
        isLoading: false,
      });
      throw error;
    }
  },

  logout: async () => {
    set({ isLoading: true });
    try {
      await apiService.logout();
      set({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      });
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
      set({ isLoading: false });
    }
  },

  checkAuth: async () => {
    set({ isLoading: true });
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      if (token) {
        // TODO: Verificar validade do token
        set({
          token,
          isAuthenticated: true,
          isLoading: false,
        });
      } else {
        set({ isLoading: false });
      }
    } catch (error) {
      set({ isLoading: false });
    }
  },

  clearError: () => set({ error: null }),
}));
