# Anki-AI MVP Technical Plan

## Overview
Anki-AI is a minimalist web app for spaced repetition learning. The MVP focuses on core features: creating, reviewing, and scheduling flashcards, all stored locally for privacy and speed.

---

## 1. MVP Features
- Add, edit, and delete cards
- Review cards due for today
- Rate recall (e.g., "Easy", "Hard", "Forgot")
- Intelligent scheduling (spaced repetition)
- Local storage (no account required)
- Responsive, clean UI

---

## 2. Data Model
- **Card**
  - `id: string`
  - `front: string`
  - `back: string`
  - `createdAt: Date`
  - `updatedAt: Date`
  - `reviewHistory: Review[]`
  - `nextReview: Date`
  - `interval: number` (days until next review)
  - `ease: number` (algorithm parameter)
- **Review**
  - `date: Date`
  - `rating: 'easy' | 'hard' | 'forgot'`

---

## 3. UI Wireframes (Textual)
- **Home / Deck View**
  - List of cards (front only)
  - Button: Add Card
  - Button: Review Due Cards
- **Add/Edit Card**
  - Input: Front
  - Input: Back
  - Save/Delete buttons
- **Review Mode**
  - Show card front
  - Button: Show Answer
  - After reveal: Buttons for rating (Easy, Hard, Forgot)
  - Progress indicator (e.g., "2 of 10 due")

---

## 4. Spaced Repetition Algorithm
- Use a simplified SM-2 algorithm:
  1. On review, update `interval` and `ease` based on rating
  2. Calculate `nextReview` as `today + interval`
  3. Store review in `reviewHistory`

---

## 5. Storage
- Use **IndexedDB** (via a wrapper like Dexie.js) for cards and reviews
- Fallback: localStorage for small data
- Provide export/import (JSON) for backup

---

## 6. Tech Stack
- **Next.js** (React, TypeScript)
- **TailwindCSS** for styling
- **Shadcn UI** for accessible components
- **Dexie.js** (or similar) for IndexedDB

---

## 7. Accessibility
- Keyboard navigation for all actions
- Proper aria-labels and roles
- Sufficient color contrast
- Responsive design

---

## 8. Future Notes (Post-MVP)
- Decks/tags for organization
- Image/audio support
- Stats and streaks
- AI-powered card suggestions
- Cloud sync (optional)

---

**This plan provides a clear, actionable roadmap for building the Anki-AI MVP.** 