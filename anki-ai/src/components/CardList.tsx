// Card List Component
//
// This component displays all cards in a list format, showing only the front of each card.
// It's the main view for browsing and managing cards.

'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Card } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useAuth } from '@/lib/auth-context';
import { toast } from 'sonner';
import { apiClient, apiHelpers } from '@/lib/api';

interface CardListProps {
  onAddCard?: () => void;
  onEditCard?: (card: Card) => void;
  onDeleteCard?: (card: Card) => void;
  onReviewCards?: () => void;
  onSettings?: () => void;
}

export const CardList = ({ 
  onAddCard, 
  onEditCard, 
  onDeleteCard, 
  onReviewCards,
  onSettings
}: CardListProps) => {
  const { logout, user } = useAuth();
  const [cards, setCards] = useState<Card[]>([]);
  const [loading, setLoading] = useState(true);
  const [dueCount, setDueCount] = useState(0);
  const [focusedCardIndex, setFocusedCardIndex] = useState(-1);
  const [deletingCardId, setDeletingCardId] = useState<string | null>(null);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const addCardButtonRef = useRef<HTMLButtonElement>(null);

  // Load cards from storage
  const loadCards = async () => {
    try {
      setLoading(true);
      // Use apiClient for authenticated API calls
      let allCards: Card[] = [];
      let dueCards: Card[] = [];
      try {
        const response = await apiClient.getCards({ page_size: 100 });
        allCards = Array.isArray(response.items) ? response.items.map(apiHelpers.apiCardToCard) : [];
      } catch (err) {
        console.error('Failed to fetch all cards:', err);
        toast.error('Failed to load cards');
        allCards = [];
      }
      try {
        const dueResponse = await apiClient.getDueCards({ page_size: 100 });
        dueCards = Array.isArray(dueResponse) ? dueResponse.map(apiHelpers.apiCardToCard) : [];
      } catch (err) {
        console.error('Failed to fetch due cards:', err);
        dueCards = [];
      }
      
      // Debug logging
      console.log('All cards:', allCards.length);
      console.log('Due cards:', dueCards.length);
      if (allCards.length > 0) {
        console.log('First card nextReview:', allCards[0].nextReview);
        console.log('Today:', new Date());
      }
      
      setCards(allCards);
      setDueCount(dueCards.length);
      
      // Only show toast for significant changes, not on initial load
      // if (allCards.length > 0) {
      //   toast.success(`Loaded ${allCards.length} cards`, {
      //     description: `${dueCards.length} cards due for review`
      //   });
      // }
    } catch (error) {
      console.error('Failed to load cards:', error);
      toast.error('Failed to load cards');
    } finally {
      setLoading(false);
    }
  };

  // Load cards on component mount
  useEffect(() => {
    loadCards();
  }, []);

  // Focus management
  useEffect(() => {
    if (!loading && cards.length === 0 && addCardButtonRef.current) {
      addCardButtonRef.current.focus();
    }
  }, [loading, cards.length]);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (loading || cards.length === 0) return;

      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault();
          setFocusedCardIndex(prev => 
            prev < cards.length - 1 ? prev + 1 : prev
          );
          break;
        case 'ArrowUp':
          event.preventDefault();
          setFocusedCardIndex(prev => prev > 0 ? prev - 1 : prev);
          break;
        case 'Enter':
          if (focusedCardIndex >= 0 && onEditCard) {
            event.preventDefault();
            onEditCard(cards[focusedCardIndex]);
          }
          break;
        case 'Delete':
        case 'Backspace':
          if (focusedCardIndex >= 0 && onDeleteCard) {
            event.preventDefault();
            handleDeleteCard(cards[focusedCardIndex]);
          }
          break;
        case 'a':
        case 'A':
          if (onAddCard) {
            event.preventDefault();
            onAddCard();
          }
          break;
        case 'r':
        case 'R':
          if (onReviewCards && dueCount > 0) {
            event.preventDefault();
            onReviewCards();
          }
          break;
        case 's':
        case 'S':
          if (onSettings) {
            event.preventDefault();
            onSettings();
          }
          break;
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [loading, cards, focusedCardIndex, dueCount, onAddCard, onEditCard, onDeleteCard, onReviewCards, onSettings]);

  // Handle card deletion
  const handleDeleteCard = useCallback(async (card: Card) => {
    if (window.confirm(`Are you sure you want to delete "${card.front}"?`)) {
      try {
        setDeletingCardId(card.id);
        await apiClient.deleteCard(card.id)
        .then(() => loadCards()) // Reload the list
        .then(() => onDeleteCard?.(card));
        
        toast.success('Card deleted successfully', {
          description: `"${card.front}" has been removed`
        });
        
        // Reset focus if the deleted card was focused
        if (focusedCardIndex >= cards.length - 1) {
          setFocusedCardIndex(Math.max(0, cards.length - 2));
        }
      } catch (error) {
        console.error('Failed to delete card:', error);
        toast.error('Failed to delete card');
      } finally {
        setDeletingCardId(null);
      }
    }
  }, [focusedCardIndex, cards.length, onDeleteCard]);

  // Handle logout
  const handleLogout = async () => {
    if (!window.confirm('Are you sure you want to sign out? You will need to sign in again to access your cards.')) {
      return;
    }

    setIsLoggingOut(true);
    try {
      await logout();
      toast.success('Signed out successfully!', {
        description: 'You have been logged out of your account'
      });
    } catch (error) {
      console.error('Logout failed:', error);
      toast.error('Failed to sign out. Please try again.');
    } finally {
      setIsLoggingOut(false);
    }
  };

  if (loading) {
    return (
      <div 
        className="flex flex-col justify-center items-center p-responsive space-y-4"
        role="status"
        aria-live="polite"
        aria-label="Loading cards"
      >
        <div className="text-responsive-lg">Loading cards...</div>
        <Progress value={0} className="w-64" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with actions */}
      <div className="flex flex-col gap-4 sm:flex-row sm:justify-between sm:items-center">
        <div className="space-y-2">
          <div className="flex items-center gap-4">
            <h1 className="text-responsive-xl font-bold">My Cards</h1>
            {user && (
              <div className="text-sm text-muted-foreground">
                Signed in as {user.username}
              </div>
            )}
          </div>
          <p className="text-responsive text-muted-foreground">
            {cards.length} total cards • {dueCount} due for review
          </p>
          {cards.length > 0 && (
            <div className="flex items-center gap-2">
              <Progress 
                value={((cards.length - dueCount) / cards.length) * 100} 
                className="w-32 h-2" 
              />
              <span className="text-xs text-muted-foreground">
                {Math.round(((cards.length - dueCount) / cards.length) * 100)}% up to date
              </span>
            </div>
          )}
        </div>
        
        <div className="flex flex-col gap-3 sm:flex-row sm:gap-2">
          {onReviewCards && dueCount > 0 && (
            <Button 
              onClick={onReviewCards}
              className="bg-green-600 hover:bg-green-700 text-white font-medium"
              aria-label={`Review ${dueCount} cards due for review`}
              size="lg"
            >
              Review Due Cards ({dueCount})
            </Button>
          )}
          {onAddCard && (
            <Button 
              ref={addCardButtonRef}
              onClick={onAddCard}
              aria-label="Add a new flashcard"
              size="lg"
              className="font-medium"
            >
              Add Card
            </Button>
          )}
          {onSettings && (
            <Button 
              variant="outline" 
              onClick={onSettings}
              aria-label="Open settings and backup options"
              size="lg"
              className="font-medium"
            >
              Settings
            </Button>
          )}
          <Button 
            variant="ghost" 
            onClick={handleLogout}
            disabled={isLoggingOut}
            aria-label="Sign out of your account"
            size="lg"
            className="font-medium text-muted-foreground hover:text-foreground"
          >
            {isLoggingOut ? 'Signing out...' : 'Sign Out'}
          </Button>
        </div>
      </div>

      {/* Cards list */}
      {cards.length === 0 ? (
        <div className="text-center py-responsive">
          <div className="text-6xl mb-6" role="img" aria-label="Empty state">📝</div>
          <h3 className="text-responsive-lg font-semibold mb-4">No cards yet</h3>
          <p className="text-responsive text-muted-foreground mb-6 max-w-md mx-auto">
            Create your first flashcard to get started with spaced repetition learning!
          </p>
          {onAddCard && (
            <Button 
              onClick={onAddCard}
              size="lg"
              className="font-medium"
            >
              Create Your First Card
            </Button>
          )}
        </div>
      ) : (
        <div 
          className="space-y-4" 
          role="list" 
          aria-label="Flashcards"
          tabIndex={0}
        >
          {(Array.isArray(cards) ? cards : []).map((card, index) => (
            <div
              key={card.id}
              className={`flex flex-col sm:flex-row sm:items-center sm:justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors ${
                focusedCardIndex === index ? 'ring-2 ring-blue-500 bg-blue-50' : ''
              }`}
              role="listitem"
              tabIndex={0}
              aria-label={`Card ${index + 1}: ${card.front}`}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && onEditCard) {
                  e.preventDefault();
                  onEditCard(card);
                } else if (e.key === 'Delete' || e.key === 'Backspace') {
                  e.preventDefault();
                  handleDeleteCard(card);
                } else if (e.key === 'ArrowDown') {
                  e.preventDefault();
                  setFocusedCardIndex(index + 1 < cards.length ? index + 1 : index);
                } else if (e.key === 'ArrowUp') {
                  e.preventDefault();
                  setFocusedCardIndex(index > 0 ? index - 1 : index);
                }
              }}
              onFocus={() => setFocusedCardIndex(index)}
              onBlur={() => setFocusedCardIndex(-1)}
            >
              <div className="flex-1 min-w-0 mb-4 sm:mb-0">
                <div className="font-medium truncate text-responsive" id={`card-${card.id}-front`}>
                  {card.front}
                </div>
                <div className="text-sm text-muted-foreground mt-1">
                  Created {new Date(card.createdAt).toLocaleDateString()}
                  {card.reviewHistory.length > 0 && (
                    <span> • {card.reviewHistory.length} reviews</span>
                  )}
                </div>
              </div>
              
              <div className="flex gap-2 sm:ml-4">
                {onEditCard && (
                  <Button
                    variant="outline"
                    size="lg"
                    onClick={() => onEditCard(card)}
                    aria-label={`Edit card: ${card.front}`}
                    aria-describedby={`card-${card.id}-front`}
                    className="flex-1 sm:flex-none font-medium"
                  >
                    Edit
                  </Button>
                )}
                {onDeleteCard && (
                  <Button
                    variant="outline"
                    size="lg"
                    onClick={() => handleDeleteCard(card)}
                    aria-label={`Delete card: ${card.front}`}
                    aria-describedby={`card-${card.id}-front`}
                    className="flex-1 sm:flex-none text-red-600 hover:text-red-700 hover:bg-red-50 font-medium"
                    disabled={deletingCardId === card.id}
                  >
                    {deletingCardId === card.id ? 'Deleting...' : 'Delete'}
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Keyboard shortcuts help */}
      {cards.length > 0 && (
        <div className="bg-muted/50 p-responsive rounded-lg">
          <h3 className="text-responsive font-medium mb-3">Keyboard Navigation</h3>
          <div className="text-xs text-muted-foreground space-y-2 sm:space-y-1 sm:grid sm:grid-cols-2 sm:gap-x-4">
            <p><kbd className="px-2 py-1 bg-white rounded border text-xs">↑</kbd> <kbd className="px-2 py-1 bg-white rounded border text-xs">↓</kbd> - Navigate cards</p>
            <p><kbd className="px-2 py-1 bg-white rounded border text-xs">Enter</kbd> - Edit selected card</p>
            <p><kbd className="px-2 py-1 bg-white rounded border text-xs">Delete</kbd> - Delete selected card</p>
            <p><kbd className="px-2 py-1 bg-white rounded border text-xs">A</kbd> - Add new card</p>
            <p><kbd className="px-2 py-1 bg-white rounded border text-xs">R</kbd> - Review due cards</p>
            <p><kbd className="px-2 py-1 bg-white rounded border text-xs">S</kbd> - Open settings</p>
          </div>
        </div>
      )}
    </div>
  );
}; 