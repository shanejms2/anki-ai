// API Client Service for Anki-AI Backend
//
// This file provides a clean interface for communicating with our FastAPI backend.
// It handles authentication, request/response formatting, and error handling.

import { Card, Review, ReviewRating } from './types';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_VERSION = 'v1';

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user?: {
    id: string;
    email: string;
    username?: string;
    created_at: string;
    updated_at: string;
  };
}

export interface OAuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    username?: string;
    created_at: string;
    updated_at: string;
  };
  is_new_user: boolean;
}

export interface User {
  id: string;
  email: string;
  username?: string;
  created_at: string;
  updated_at: string;
}

export interface ApiCard {
  id: string;
  user_id: string;
  front: string;
  back: string;
  tags: string[];
  interval: number;
  ease_factor: number;
  review_count: number;
  next_review: string;
  created_at: string;
  updated_at: string;
}

export interface ApiReview {
  id: string;
  user_id: string;
  card_id: string;
  rating: number;
  interval_before: number;
  interval_after: number;
  ease_factor_before: number;
  ease_factor_after: number;
  created_at: string;
}

export interface ReviewStats {
  total_reviews: number;
  reviews_today: number;
  reviews_this_week: number;
  average_rating: number;
  cards_studied: number;
  due_cards: number;
  learning_cards: number;
  mature_cards: number;
  retention_rate?: number;
  study_streak?: number;
}

export interface CacheStats {
  hits: number;
  misses: number;
  sets: number;
  deletes: number;
  total_requests: number;
  hit_rate: number;
  size: number;
}

// Error Types
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Authentication Service
class AuthService {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      // Always store as access_token for Supabase compatibility
      localStorage.setItem('access_token', token);
      localStorage.setItem('anki_ai_token', token);
    }
  }

  getToken(): string | null {
    if (typeof window !== 'undefined') {
      // Always check Supabase access_token first
      const supabaseToken = localStorage.getItem('access_token');
      if (supabaseToken) {
        this.token = supabaseToken;
        return supabaseToken;
      }
      // Fallback to our app's token
      const appToken = localStorage.getItem('anki_ai_token');
      if (appToken) {
        this.token = appToken;
        return appToken;
      }
    }
    return this.token;
  }

  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('anki_ai_token');
    }
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }
}

// HTTP Client
class HttpClient {
  private authService = new AuthService();

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}/api/${API_VERSION}${endpoint}`;
    const token = this.authService.getToken();

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    // Debug logging for token and headers
    if (typeof window !== 'undefined') {
      console.log('API Request:', { url, token, headers: config.headers });
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new ApiError(
          errorData.detail || `HTTP ${response.status}`,
          response.status,
          errorData.code
        );
      }

      // Handle empty responses
      if (response.status === 204) {
        return {} as T;
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        error instanceof Error ? error.message : 'Network error',
        0
      );
    }
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

// API Client
class ApiClient {
  private http = new HttpClient();
  private authService = new AuthService();

  // Authentication Methods
  async register(email: string, password: string, username?: string): Promise<AuthResponse> {
    const response = await this.http.post<AuthResponse>('/auth/register', {
      email,
      password,
      username,
    });
    this.authService.setToken(response.access_token);
    return response;
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await this.http.post<AuthResponse>('/auth/login', {
      email,
      password,
    });
    this.authService.setToken(response.access_token);
    return response;
  }

  async logout(): Promise<{ message: string }> {
    const response = await this.http.post<{ message: string }>('/auth/logout');
    this.authService.clearToken();
    return response;
  }

  async refreshToken(): Promise<AuthResponse> {
    const response = await this.http.post<AuthResponse>('/auth/refresh');
    this.authService.setToken(response.access_token);
    return response;
  }

  async getProfile(): Promise<User> {
    return this.http.get<User>('/auth/me');
  }

  async getUserById(userId: string): Promise<User> {
    return this.http.get<User>(`/auth/me-by-id/${userId}`);
  }

  async createUserProfile(userId: string, email: string, username?: string): Promise<User> {
    return this.http.post<User>('/auth/create-profile', {
      user_id: userId,
      email: email,
      username: username
    });
  }

  async updateProfile(data: { email?: string; username?: string }): Promise<User> {
    return this.http.put<User>('/auth/profile', data);
  }

  async requestPasswordReset(email: string): Promise<{ message: string }> {
    return this.http.post<{ message: string }>('/auth/password-reset', { email });
  }

  // OAuth Methods
  async getOAuthUrl(provider: 'google'): Promise<{ url: string; state: string }> {
    return this.http.get<{ url: string; state: string }>(`/auth/oauth/${provider}/url`);
  }

  async oauthLogin(provider: 'google', code: string, redirectUri: string): Promise<OAuthResponse> {
    const response = await this.http.post<OAuthResponse>('/auth/oauth', {
      provider,
      code,
      redirect_uri: redirectUri,
    });
    this.authService.setToken(response.access_token);
    return response;
  }

  // Card Methods
  async createCard(data: { front: string; back: string; tags?: string[] }): Promise<ApiCard> {
    return this.http.post<ApiCard>('/cards/', data);
  }

  async getCards(params?: {
    page?: number;
    page_size?: number;
    search?: string;
    tags?: string;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
  }): Promise<PaginatedResponse<ApiCard>> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const query = searchParams.toString();
    const endpoint = query ? `/cards/?${query}` : '/cards/';
    return this.http.get<PaginatedResponse<ApiCard>>(endpoint);
  }

  async getCard(id: string): Promise<ApiCard> {
    return this.http.get<ApiCard>(`/cards/${id}`);
  }

  async updateCard(id: string, data: { front?: string; back?: string; tags?: string[] }): Promise<ApiCard> {
    return this.http.put<ApiCard>(`/cards/${id}`, data);
  }

  async deleteCard(id: string): Promise<{ message: string }> {
    return this.http.delete<{ message: string }>(`/cards/${id}`);
  }

  async getDueCards(params?: { page?: number; page_size?: number }): Promise<ApiCard[]> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const query = searchParams.toString();
    const endpoint = query ? `/cards/due/list?${query}` : '/cards/due/list';
    return this.http.get<ApiCard[]>(endpoint);
  }

  async getDueCount(): Promise<{ count: number }> {
    return this.http.get<{ count: number }>('/cards/due/count');
  }

  // Review Methods
  async submitReview(cardId: string, rating: number): Promise<{
    review: ApiReview;
    card_updated: Partial<ApiCard>;
    next_review: string;
    message: string;
  }> {
    return this.http.post(`/reviews/cards/${cardId}/review`, { rating });
  }

  async getReviews(params?: {
    page?: number;
    page_size?: number;
    card_id?: string;
    rating?: number;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
  }): Promise<PaginatedResponse<ApiReview>> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const query = searchParams.toString();
    const endpoint = query ? `/reviews/?${query}` : '/reviews/';
    return this.http.get<PaginatedResponse<ApiReview>>(endpoint);
  }

  async getCardReviews(cardId: string, params?: { page?: number; page_size?: number }): Promise<PaginatedResponse<ApiReview>> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const query = searchParams.toString();
    const endpoint = query ? `/reviews/cards/${cardId}?${query}` : `/reviews/cards/${cardId}`;
    return this.http.get<PaginatedResponse<ApiReview>>(endpoint);
  }

  async getReviewStats(period?: 'today' | 'week' | 'month' | 'year' | 'all'): Promise<ReviewStats> {
    const endpoint = period ? `/reviews/stats?period=${period}` : '/reviews/stats';
    return this.http.get<ReviewStats>(endpoint);
  }

  // System Methods
  async getCacheStats(): Promise<{ cache_stats: CacheStats; description: string }> {
    return this.http.get<{ cache_stats: CacheStats; description: string }>('/system/cache/stats');
  }

  async clearCache(): Promise<{ message: string }> {
    return this.http.post<{ message: string }>('/system/cache/clear');
  }

  async cleanupCache(): Promise<{ message: string; removed_items: number }> {
    return this.http.post<{ message: string; removed_items: number }>('/system/cache/cleanup');
  }

  // Utility Methods
  isAuthenticated(): boolean {
    return this.authService.isAuthenticated();
  }

  getAuthToken(): string | null {
    return this.authService.getToken();
  }
}

// Create and export a single API client instance
export const apiClient = new ApiClient();

// Helper functions for data transformation
export const apiHelpers = {
  // Convert API card to local card format
  apiCardToCard(apiCard: ApiCard): Card {
    return {
      id: apiCard.id,
      front: apiCard.front,
      back: apiCard.back,
      createdAt: new Date(apiCard.created_at),
      updatedAt: new Date(apiCard.updated_at),
      reviewHistory: [], // Reviews are fetched separately
      nextReview: new Date(apiCard.next_review),
      interval: apiCard.interval,
      ease: apiCard.ease_factor,
    };
  },

  // Convert local card to API card format
  cardToApiCard(card: Card): Omit<ApiCard, 'id' | 'user_id' | 'created_at' | 'updated_at'> {
    return {
      front: card.front,
      back: card.back,
      tags: [], // Add tags support later
      interval: card.interval,
      ease_factor: card.ease,
      review_count: card.reviewHistory.length,
      next_review: card.nextReview.toISOString(),
    };
  },

  // Convert rating to API format
  ratingToApi(rating: ReviewRating): number {
    switch (rating) {
      case 'easy': return 5;
      case 'hard': return 3;
      case 'forgot': return 1;
      default: return 3;
    }
  },

  // Convert API rating to local format
  apiRatingToRating(rating: number): ReviewRating {
    if (rating >= 4) return 'easy';
    if (rating >= 2) return 'hard';
    return 'forgot';
  },
};

 