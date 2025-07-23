// Type definitions for Anki-AI MVP
//
// This file defines the main data structures (types and interfaces) used in the app.
// In TypeScript, types and interfaces are like Python classes or type hints—they help you describe what kind of data your code expects.
// This makes your code safer and easier to understand.
//
// You can import these types anywhere in your project to ensure you use the correct structure for your data.

// This type restricts the allowed values for a review rating.
// It's similar to an Enum in Python, but simpler.
export type ReviewRating = 'easy' | 'hard' | 'forgot';

// This interface describes the shape of a Review object.
// It's like a Python class with only attributes (no methods).
export interface Review {
  date: Date; // When the review happened (JavaScript Date object)
  rating: ReviewRating; // How well you remembered (must be 'easy', 'hard', or 'forgot')
}

// This interface describes a flashcard.
// It lists all the properties a Card should have.
export interface Card {
  id: string; // Unique identifier for the card (like a UUID string)
  front: string; // The question or prompt
  back: string; // The answer
  createdAt: Date; // When the card was created
  updatedAt: Date; // When the card was last updated
  reviewHistory: Review[]; // List of all past reviews for this card
  nextReview: Date; // When this card should be reviewed next
  interval: number; // Days until next review (spaced repetition)
  ease: number; // Algorithm parameter for how easy this card is
} 