// Database setup using Dexie.js for IndexedDB
//
// This file sets up our local database to store flashcards and reviews.
// Dexie.js is a wrapper around IndexedDB that makes it easier to work with.
// IndexedDB is like a local database in your browser—similar to SQLite but for web apps.

import Dexie, { Table } from 'dexie';
import { Card, Review } from './types';

// Extend Dexie to add our tables
export class AnkiDatabase extends Dexie {
  // Define our tables
  cards!: Table<Card>;
  reviews!: Table<Review>;

  constructor() {
    super('AnkiDatabase'); // Database name
    this.version(1).stores({
      // Define the schema for our tables
      cards: 'id, front, back, createdAt, updatedAt, nextReview, interval, ease',
      reviews: 'id, cardId, date, rating'
    });
  }
}

// Create and export a single database instance
export const db = new AnkiDatabase();

// Helper functions for common database operations
export const dbHelpers = {
  // Add a new card
  async addCard(card: Omit<Card, 'id'>): Promise<Card> {
    const id = crypto.randomUUID(); // Generate unique ID
    const newCard: Card = {
      ...card,
      id,
      createdAt: new Date(),
      updatedAt: new Date(),
      reviewHistory: [],
      nextReview: new Date(), // Review immediately
      interval: 1, // Start with 1 day interval
      ease: 2.5 // Default ease factor
    };
    
    await db.cards.add(newCard);
    return newCard;
  },

  // Get all cards
  async getAllCards(): Promise<Card[]> {
    return await db.cards.toArray();
  },

  // Get cards due for review today
  async getDueCards(): Promise<Card[]> {
    const today = new Date();
    today.setHours(23, 59, 59, 999); // End of today to include all of today
    
    return await db.cards
      .where('nextReview')
      .belowOrEqual(today)
      .toArray();
  },

  // Update a card
  async updateCard(card: Card): Promise<void> {
    const updatedCard = {
      ...card,
      updatedAt: new Date()
    };
    await db.cards.put(updatedCard);
  },

  // Delete a card
  async deleteCard(id: string): Promise<void> {
    await db.cards.delete(id);
  },

  // Add a review to a card
  async addReview(cardId: string, review: Omit<Review, 'id'>): Promise<void> {
    const card = await db.cards.get(cardId);
    if (!card) throw new Error('Card not found');

    const newReview: Review & { id: string } = {
      ...review,
      id: crypto.randomUUID()
    };

    // Add review to card's history
    card.reviewHistory.push(newReview);
    card.updatedAt = new Date();
    
    await db.cards.put(card);
  }
}; 