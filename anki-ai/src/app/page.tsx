'use client';

import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'next/navigation';
import { CardList } from '@/components/CardList';
import { AddCardForm } from '@/components/AddCardForm';
import { EditCardForm } from '@/components/EditCardForm';
import { ReviewMode } from '@/components/ReviewMode';
import { Settings } from '@/components/Settings';
import { AuthModal } from '@/components/auth/AuthModal';
import { Card } from '@/lib/types';
import { useAuth } from '@/lib/auth-context';
import { useCards } from '@/lib/hooks/useCards';
import { apiClient } from '@/lib/api';
import { toast } from 'sonner';

type View = 'list' | 'add' | 'edit' | 'review' | 'settings';

export default function Home() {
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading: authLoading, user, refreshUser, oauthLogin } = useAuth();
  const { cards, dueCards, isLoading: cardsLoading, error: cardsError } = useCards();
  const [currentView, setCurrentView] = useState<View>('list');
  const [editingCard, setEditingCard] = useState<Card | null>(null);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');

  // Handle view transitions with feedback
  const transitionToView = (newView: View) => {
    setIsTransitioning(true);
    
    // Small delay for smooth transition
    setTimeout(() => {
      setCurrentView(newView);
      setIsTransitioning(false);
    }, 150);
  };

  // Handle card list actions
  const handleAddCard = useCallback(() => {
    transitionToView('add');
  }, []);

  const handleEditCard = useCallback((card: Card) => {
    setEditingCard(card);
    transitionToView('edit');
  }, []);

  const handleDeleteCard = useCallback((card: Card) => {
    // Card deletion feedback is handled in CardList component
    // Just refresh the list view
    if (currentView === 'list') {
      toast.success('Card list updated');
    }
  }, [currentView]);

  const handleReviewCards = useCallback(() => {
    transitionToView('review');
  }, []);

  const handleSettings = useCallback(() => {
    transitionToView('settings');
  }, []);

  // Handle form completions
  const handleCardAdded = () => {
    toast.success('Card created successfully!', {
      description: 'Returning to card list'
    });
    transitionToView('list');
  };

  const handleCardUpdated = () => {
    setEditingCard(null);
    // Removed duplicate toast - EditCardForm already shows success toast
    // toast.success('Card updated successfully!', {
    //   description: 'Returning to card list'
    // });
    transitionToView('list');
  };

  const handleReviewComplete = () => {
    toast.success('Review session completed!', {
      description: 'Returning to card list'
    });
    transitionToView('list');
  };

  // Handle cancellations
  const handleCancel = useCallback(() => {
    // Removed all cancellation toasts to reduce noise
    // const viewMessages: Record<View, string> = {
    //   list: '',
    //   add: 'Card creation cancelled',
    //   edit: 'Card editing cancelled',
    //   review: 'Review session cancelled',
    //   settings: '' // Removed "Settings closed" toast
    // };
    
    // const message = viewMessages[currentView];
    // if (message) {
    //   toast.info(message);
    // }
    
    if (currentView === 'edit') {
      setEditingCard(null);
    }
    transitionToView('list');
  }, [currentView]);

  // Remove modal state and handlers

  // Handle Google OAuth directly
  const handleGoogleLogin = () => {
    oauthLogin('google');
  };

  // Handle keyboard shortcuts for main navigation
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (isTransitioning) return;
      
      switch (event.key) {
        case 'a':
        case 'A':
          if (currentView === 'list' && isAuthenticated) {
            event.preventDefault();
            handleAddCard();
          }
          break;
        case 'r':
        case 'R':
          if (currentView === 'list' && isAuthenticated) {
            event.preventDefault();
            handleReviewCards();
          }
          break;
        case 's':
        case 'S':
          if (currentView === 'list') {
            event.preventDefault();
            handleSettings();
          }
          break;
        case 'Escape':
          if (currentView !== 'list') {
            event.preventDefault();
            handleCancel();
          }
          break;
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [currentView, isTransitioning, isAuthenticated]);

  // Handle OAuth callback and errors from URL parameters
  useEffect(() => {
    const error = searchParams.get('error');
    const errorDescription = searchParams.get('error_description');
    const code = searchParams.get('code');
    
    console.log('URL parameters:', { error, errorDescription, code });
    
    if (error) {
      console.error('OAuth error from URL:', error, errorDescription);
      toast.error(`OAuth authentication failed: ${errorDescription || error}`);
      
      // Clear the URL parameters
      const url = new URL(window.location.href);
      url.search = '';
      window.history.replaceState({}, '', url.toString());
      return;
    }

    // Handle OAuth callback with code parameter
    if (code) {
      const handleOAuthCallback = async () => {
        try {
          console.log('Processing OAuth callback from main page');
          
          // Exchange code for session
          const response = await apiClient.oauthLogin(
            'google',
            code,
            window.location.origin
          );

          console.log('OAuth login successful:', response);

          // Refresh the auth context to update the user state
          await refreshUser();

          if (response.is_new_user) {
            toast.success('Welcome to Anki-AI! Your account has been created.');
          } else {
            toast.success('Welcome back to Anki-AI!');
          }

          // Clear the URL parameters
          const url = new URL(window.location.href);
          url.search = '';
          window.history.replaceState({}, '', url.toString());
        } catch (error) {
          console.error('OAuth callback error:', error);
          toast.error('Authentication failed. Please try again.');
          
          // Clear the URL parameters
          const url = new URL(window.location.href);
          url.search = '';
          window.history.replaceState({}, '', url.toString());
        }
      };

      handleOAuthCallback();
    }
  }, [searchParams, refreshUser]);

  // Handle OAuth callback with access token in URL hash
  useEffect(() => {
    const handleAccessToken = async () => {
      // Check if we have an access token in the URL hash
      const hash = window.location.hash;
      if (hash && hash.includes('access_token=')) {
        console.log('Found access token in URL hash');
        
        try {
          // Parse the hash parameters
          const hashParams = new URLSearchParams(hash.substring(1));
          const accessToken = hashParams.get('access_token');
          const expiresAt = hashParams.get('expires_at');
          const refreshToken = hashParams.get('refresh_token');
          
          console.log('Access token found:', { accessToken: accessToken ? 'present' : 'missing', expiresAt, refreshToken: refreshToken ? 'present' : 'missing' });
          
          if (accessToken) {
            // Store the tokens
            localStorage.setItem('access_token', accessToken);
            if (refreshToken) {
              localStorage.setItem('refresh_token', refreshToken);
            }
            if (expiresAt) {
              localStorage.setItem('expires_at', expiresAt);
            }
            
            // Refresh the auth context to update the user state
            await refreshUser();
            
            toast.success('Welcome to Anki-AI!');
            
            // Clear the URL hash
            window.history.replaceState({}, '', window.location.pathname);
          }
        } catch (error) {
          console.error('Error processing access token:', error);
          toast.error('Authentication failed. Please try again.');
          
          // Clear the URL hash
          window.history.replaceState({}, '', window.location.pathname);
        }
      }
    };

    handleAccessToken();
  }, [refreshUser]);

  // Show loading state while auth is initializing
  if (authLoading) {
    return (
      <div className="flex flex-col justify-center items-center min-h-screen space-y-4">
        <div className="text-lg">Loading Anki-AI...</div>
        <div className="w-64 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div className="h-full bg-blue-600 animate-pulse"></div>
        </div>
      </div>
    );
  }

  // Show authentication prompt if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="container mx-auto p-4 min-h-screen flex flex-col justify-center items-center">
        <div className="text-center space-y-6 max-w-md">
          <div>
            <h1 className="text-3xl font-bold mb-2">Welcome to Anki-AI</h1>
            <p className="text-muted-foreground">
              Your intelligent spaced repetition learning companion
            </p>
          </div>
          <div className="space-y-4">
            <button
              onClick={handleGoogleLogin}
              className="w-full bg-primary text-primary-foreground px-6 py-3 rounded-md hover:bg-primary/90 transition-colors text-lg font-medium"
            >
              Continue with Google
            </button>
          </div>
          <p className="text-sm text-muted-foreground">
            Sign in with Google to sync your cards across devices and start learning.
          </p>
        </div>
      </div>
    );
  }

  // Render loading state during transitions
  if (isTransitioning) {
    return (
      <div 
        className="flex flex-col justify-center items-center min-h-screen space-y-4"
        role="status"
        aria-live="polite"
        aria-label="Transitioning between views"
      >
        <div className="text-lg">Loading...</div>
        <div className="w-64 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div className="h-full bg-blue-600 animate-pulse"></div>
        </div>
      </div>
    );
  }

  // Render appropriate view
  switch (currentView) {
    case 'add':
      return (
        <div className="container mx-auto p-responsive min-h-screen">
          <AddCardForm 
            onCardAdded={handleCardAdded}
            onCancel={handleCancel}
          />
        </div>
      );

    case 'edit':
      return editingCard ? (
        <div className="container mx-auto p-responsive min-h-screen">
          <EditCardForm 
            card={editingCard}
            onCardUpdated={handleCardUpdated}
            onCancel={handleCancel}
          />
        </div>
      ) : (
        <div className="container mx-auto p-responsive min-h-screen">
          <div className="text-center">
            <p>Card not found. Returning to list...</p>
          </div>
        </div>
      );

    case 'review':
      return (
        <div className="container mx-auto p-responsive min-h-screen">
          <ReviewMode 
            onReviewComplete={handleReviewComplete}
            onCancel={handleCancel}
          />
        </div>
      );

    case 'settings':
      return (
        <div className="container mx-auto p-responsive min-h-screen">
          <Settings onBack={handleCancel} />
        </div>
      );

    default:
      return (
        <>
          <div className="container mx-auto p-responsive min-h-screen">
            <CardList 
              onAddCard={handleAddCard}
              onEditCard={handleEditCard}
              onDeleteCard={handleDeleteCard}
              onReviewCards={handleReviewCards}
              onSettings={handleSettings}
            />
          </div>
          
          {/* Removed AuthModal */}
        </>
      );
  }
}
