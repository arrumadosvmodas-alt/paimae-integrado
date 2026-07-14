import axios, { AxiosInstance, AxiosError } from 'axios';
import * as SecureStore from 'expo-secure-store';
import Constants from 'expo-constants';

const API_URL = Constants.expoConfig?.extra?.apiUrl || 'http://localhost:8000';

interface ApiResponse<T> {
  data: T;
  status: number;
}

interface LoginRequest {
  email: string;
  password: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    name: string;
    role: string;
  };
}

class ApiService {
  private api: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.api = axios.create({
      baseURL: API_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor de requisição
    this.api.interceptors.request.use(async (config) => {
      const token = await this.getToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Interceptor de resposta
    this.api.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expirado - fazer logout
          await this.logout();
        }
        return Promise.reject(error);
      }
    );

    this.initToken();
  }

  private async initToken() {
    this.token = await this.getToken();
  }

  private async getToken(): Promise<string | null> {
    try {
      return await SecureStore.getItemAsync('auth_token');
    } catch (error) {
      console.error('Erro ao recuperar token:', error);
      return null;
    }
  }

  private async setToken(token: string): Promise<void> {
    try {
      await SecureStore.setItemAsync('auth_token', token);
      this.token = token;
    } catch (error) {
      console.error('Erro ao salvar token:', error);
    }
  }

  // Auth
  async login(email: string, password: string): Promise<AuthResponse> {
    try {
      const response = await this.api.post<AuthResponse>('/api/v1/auth/login', {
        email,
        password,
      });
      await this.setToken(response.data.access_token);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async logout(): Promise<void> {
    try {
      await SecureStore.deleteItemAsync('auth_token');
      this.token = null;
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
    }
  }

  // Children
  async getChildren() {
    try {
      const response = await this.api.get('/api/v1/children');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getChildById(childId: string) {
    try {
      const response = await this.api.get(`/api/v1/children/${childId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Learning Analytics
  async getLearningMetrics(childId: string) {
    try {
      const response = await this.api.get(`/api/v1/learning/metrics?child_id=${childId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getLearningHistory(childId: string, limit: number = 10) {
    try {
      const response = await this.api.get(
        `/api/v1/learning/history?child_id=${childId}&limit=${limit}`
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Interactions
  async getInteractions(childId: string, limit: number = 10) {
    try {
      const response = await this.api.get(
        `/api/v1/interactions?child_id=${childId}&limit=${limit}`
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getPendingInteractions(limit: number = 5) {
    try {
      const response = await this.api.get(`/api/v1/interactions/pending?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async respondToInteraction(
    interactionId: string,
    responseText: string,
    responseScore?: number
  ) {
    try {
      const response = await this.api.post(
        `/api/v1/interactions/${interactionId}/responses`,
        {
          responder_type: 'child',
          response_text: responseText,
          response_score: responseScore || 3,
          responded_at: new Date().toISOString().split('T')[0],
        }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Study Plans
  async getStudyPlans(childId: string) {
    try {
      const response = await this.api.get(`/api/v1/study-plans?child_id=${childId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getStudyPlanDetail(planId: string) {
    try {
      const response = await this.api.get(`/api/v1/study-plans/${planId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Recommendations
  async getRecommendation(childId: string, availableThemes: string[] = []) {
    try {
      const response = await this.api.post('/api/v1/learning/recommendations', {
        child_id: childId,
        available_themes: availableThemes,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.api.get('/health');
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }

  private handleError(error: any): Error {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.detail || error.message;
      return new Error(message);
    }
    return error;
  }
}

export default new ApiService();
