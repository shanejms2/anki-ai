// Custom hook for managing cards with API integration
//
// This hook provides a clean interface for card operations with automatic
// API integration and offline fallback to IndexedDB.

import { useState, useEffect, useCallback } from 'react';
import { Card, Review, ReviewRating } from '../types';
import { apiClient, ApiCard, apiHelpers } from '../api';

interface UseCardsReturn {
  // State
  cards: Card[];
  dueCards: Card[];
  isLoading: boolean;
  error: string | null;
  
  // Card operations
  createCard: (front: string, back: string, tags?: string[]) => Promise<Card>;
  updateCard: (id: string, updates: Partial<Card>) => Promise<void>;
  deleteCard: (id: string) => Promise<void>;
  getCard: (id: string) => Promise<Card | null>;
  
  // Review operations
  submitReview: (cardId: string, rating: ReviewRating) => Promise<void>;
  getDueCount: () => Promise<number>;
  
  // Utility
  refreshCards: () => Promise<void>;
  clearError: () => void;
  clearCards: () => Promise<void>;
}

export function useCards(): UseCardsReturn {
  const [cards, setCards] = useState<Card[]>([]);
  const [dueCards, setDueCards] = useState<Card[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load cards from API
  const loadCards = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await apiClient.getCards({ page_size: 100 });
      const apiCards = response.items.map(apiHelpers.apiCardToCard);
      setCards(apiCards);
      const dueResponse = await apiClient.getDueCards({ page_size: 100 });
      const apiDueCards = dueResponse.map(apiHelpers.apiCardToCard);
      setDueCards(apiDueCards);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load cards';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createCard = useCallback(async (front: string, back: string, tags?: string[]): Promise<Card> => {
    try {
      setError(null);
      const apiCard = await apiClient.createCard({ front, back, tags });
      const card = apiHelpers.apiCardToCard(apiCard);
      setCards(prev => [...prev, card]);
      return card;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create card';
      setError(message);
      throw err;
    }
  }, []);

  const updateCard = useCallback(async (id: string, updates: Partial<Card>): Promise<void> => {
    try {
      setError(null);
      const apiUpdates = apiHelpers.cardToApiCard(updates as Card);
      await apiClient.updateCard(id, apiUpdates);
      setCards(prev => prev.map(card => card.id === id ? { ...card, ...updates, updatedAt: new Date() } : card));
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update card';
      setError(message);
      throw err;
    }
  }, []);

  const deleteCard = useCallback(async (id: string): Promise<void> => {
    try {
      setError(null);
      await apiClient.deleteCard(id);
      setCards(prev => prev.filter(card => card.id !== id));
      setDueCards(prev => prev.filter(card => card.id !== id));
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete card';
      setError(message);
      throw err;
    }
  }, []);

  const getCard = useCallback(async (id: string): Promise<Card | null> => {
    try {
      const apiCard = await apiClient.getCard(id);
      return apiHelpers.apiCardToCard(apiCard);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get card';
      setError(message);
      return null;
    }
  }, []);

  const submitReview = useCallback(async (cardId: string, rating: ReviewRating): Promise<void> => {
    try {
      setError(null);
      const apiRating = apiHelpers.ratingToApi(rating);
      await apiClient.submitReview(cardId, apiRating);
      await loadCards();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to submit review';
      setError(message);
      throw err;
    }
  }, [loadCards]);

  const getDueCount = useCallback(async (): Promise<number> => {
    try {
      const response = await apiClient.getDueCount();
      return response.count;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get due count';
      setError(message);
      return 0;
    }
  }, []);

  const refreshCards = useCallback(async () => {
    await loadCards();
  }, [loadCards]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const clearCards = useCallback(async () => {
    setCards([]);
    setDueCards([]);
  }, []);

  useEffect(() => {
    loadCards();
  }, [loadCards]);

  useEffect(() => {
    const interval = setInterval(() => {
      loadCards();
    }, 60000);
    return () => clearInterval(interval);
  }, [loadCards]);

  return {
    cards,
    dueCards,
    isLoading,
    error,
    createCard,
    updateCard,
    deleteCard,
    getCard,
    submitReview,
    getDueCount,
    refreshCards,
    clearError,
    clearCards,
  };
} 