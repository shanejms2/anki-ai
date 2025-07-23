// Authentication Context for Anki-AI
//
// This file provides a React context for managing authentication state across the app.
// It handles login, logout, token management, and user profile data.

'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { apiClient, User, AuthResponse, ApiError } from './api';

// Authentication context state
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, username?: string) => Promise<void>;
  oauthLogin: (provider: 'google') => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  clearError: () => void;
}

// Create the context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider component
interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check if user is authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        if (apiClient.isAuthenticated()) {
          const userData = await apiClient.getProfile();
          setUser(userData);
        }
      } catch (err) {
        // Token might be invalid, clear it
        if (err instanceof ApiError && err.status === 401) {
          apiClient.logout();
        }
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  // Login function
  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiClient.login(email, password);
      
      if (response.user) {
        setUser(response.user);
      } else {
        // Fetch user profile if not included in response
        const userData = await apiClient.getProfile();
        setUser(userData);
      }
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Login failed';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Register function
  const register = async (email: string, password: string, username?: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiClient.register(email, password, username);
      
      if (response.user) {
        setUser(response.user);
      } else {
        // Fetch user profile if not included in response
        const userData = await apiClient.getProfile();
        setUser(userData);
      }
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Registration failed';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = async () => {
    try {
      await apiClient.logout();
    } catch (err) {
      // Even if logout fails, clear local state
      console.warn('Logout error:', err);
    } finally {
      // Clear localStorage to prevent data leakage
      try {
        localStorage.removeItem('anki-cards');
        console.log('Cleared localStorage on logout');
      } catch (error) {
        console.error('Error clearing localStorage:', error);
      }
      
      setUser(null);
      setError(null);
    }
  };

  // Refresh user data
  const refreshUser = async () => {
    try {
      // Check if we have a stored access token
      const accessToken = localStorage.getItem('access_token');
      
      if (accessToken) {
        // Use Supabase client to get user data directly
        const { supabase } = await import('./supabase');
        const { data: { user }, error } = await supabase.auth.getUser(accessToken);
        
        if (error) {
          throw error;
        }
        
                  if (user) {
            // Try to create user profile in backend first
            try {
              console.log('Creating user profile in backend...');
              const userData = await apiClient.createUserProfile(
                user.id,
                user.email || '',
                user.user_metadata?.username || user.email?.split('@')[0] || ''
              );
              setUser(userData);
              console.log('User profile created in backend');
            } catch (createError) {
              console.warn('Failed to create user profile, using Supabase data:', createError);
              // Fallback to Supabase user data
              const userData: User = {
                id: user.id,
                email: user.email || '',
                username: user.user_metadata?.username || user.email?.split('@')[0] || '',
                created_at: user.created_at,
                updated_at: user.last_sign_in_at || user.created_at
              };
              setUser(userData);
              console.log('User authenticated with Supabase token');
            }
          }
      } else if (apiClient.isAuthenticated()) {
        // Fallback to regular API call
        const userData = await apiClient.getProfile();
        setUser(userData);
      }
    } catch (err) {
      console.error('Failed to refresh user:', err);
      // Clear stored tokens on any error
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('expires_at');
      setUser(null);
      throw err;
    }
  };

  // OAuth login function
  const oauthLogin = async (provider: 'google') => {
    try {
      setError(null);
      
      // Use a simpler approach - redirect directly to Supabase OAuth
      const oauthUrl = `https://cgpjekmxzuztwyghpamk.supabase.co/auth/v1/authorize?provider=google&redirect_to=http://localhost:3000`;
      
      console.log('OAuth login - URL:', oauthUrl);
      
      // Redirect to OAuth provider
      window.location.href = oauthUrl;
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'OAuth login failed';
      setError(message);
      throw err;
    }
  };

  // Clear error
  const clearError = () => {
    setError(null);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
    login,
    register,
    oauthLogin,
    logout,
    refreshUser,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook to use the auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Hook for protected routes
export function useRequireAuth() {
  const { isAuthenticated, isLoading } = useAuth();
  
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      // Redirect to login or show login modal
      // This can be customized based on your routing setup
      window.location.href = '/login';
    }
  }, [isAuthenticated, isLoading]);

  return { isAuthenticated, isLoading };
} 