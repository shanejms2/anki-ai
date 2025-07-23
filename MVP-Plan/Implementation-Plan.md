# Anki-AI MVP Implementation Plan

## 1. Project Setup
- [x] Initialize Next.js project with TypeScript, TailwindCSS, Shadcn UI, and strict mode.
- [x] Set up folder structure: `src/components/ui`, `src/lib`, etc.
- [x] Configure TailwindCSS and import in `globals.css`.
- [x] Add Shadcn UI and ensure components are accessible and styled.
- [x] Add Dexie.js (or similar) for IndexedDB integration.

---

## 2. Data Model & Storage
- [x] Define TypeScript types/interfaces for `Card` and `Review`.
- [x] Implement Dexie.js database schema for cards and reviews.
- [x] Add fallback to localStorage for small data.
- [x] Implement import/export (JSON) for backup.

---

## 3. Core Features

### Card Management
- [x] Create UI for listing cards (front only).
- [x] Implement "Add Card" functionality (form, validation, save to DB).
- [x] Implement "Edit Card" functionality (load, update, save).
- [x] Implement "Delete Card" functionality (with confirmation).

### Review Flow
- [x] Implement "Review Due Cards" button and logic to fetch due cards.
- [x] Build Review Mode UI:
  - [x] Show card front.
  - [x] "Show Answer" button.
  - [x] After reveal: rating buttons ("Easy", "Hard", "Forgot").
  - [x] Progress indicator (e.g., "2 of 10 due").
- [x] Implement rating logic and update card scheduling.

---

## 4. Spaced Repetition Algorithm
- [x] Implement simplified SM-2 algorithm:
  - [x] Update `interval` and `ease` based on rating.
  - [x] Calculate `nextReview` as `today + interval`.
  - [x] Store review in `reviewHistory`.

---

## 5. UI/UX & Accessibility
- [x] Use Shadcn UI components for all controls.
- [x] Ensure all actions are keyboard accessible (tabindex, aria-labels, roles).
- [x] Ensure color contrast and responsive design.
- [x] Add progress indicators and feedback for user actions.

---

## 6. Testing & Quality
- [x] Add unit tests for core logic (card CRUD, review scheduling).
- [x] Add integration tests for main flows (add/edit/review cards).
- [x] Ensure code follows DRY, best practices, and project conventions.
- [x] Fix all critical linting errors and TypeScript issues.
- [x] Achieve 48 passing tests with comprehensive coverage.

---

## 7. Polish & Documentation
- [x] Write clear README with usage instructions.
- [x] Add comments and types for maintainability.
- [x] Final accessibility audit.
- [x] Complete code documentation and inline comments.

---

## 8. FastAPI Backend Implementation

### Backend Project Setup
- [x] Create FastAPI project structure with proper organization.
- [x] Set up Python virtual environment and dependency management.
- [x] Install required packages: `fastapi`, `uvicorn`, `supabase`, `pydantic`.
- [x] Configure environment variables for Supabase URL and service role key.
- [x] Set up logging and error handling middleware.

### Supabase Integration
- [x] Create Supabase project and get API credentials.
- [x] Install Supabase Python client (`supabase-py`).
- [x] Set up environment variables for Supabase URL and service role key.
- [x] Configure Supabase client in `app/core/supabase.py`.
- [x] Design PostgreSQL schema in Supabase:
  - [x] `users` table with id, email, username, created_at, updated_at (extends auth.users).
  - [x] `cards` table with id, user_id, front, back, interval, ease, next_review, created_at, updated_at.
  - [x] `reviews` table with id, user_id, card_id, rating, reviewed_at.
- [x] Set up Row Level Security (RLS) policies for data isolation.
- [x] Create database indexes for performance optimization.
- [x] Set up foreign key constraints and cascading deletes.
- [x] **Database schema deployed and tested successfully.**

### Authentication & Authorization
- [x] Use Supabase Auth for user management (email/password, social login).
- [x] Implement JWT token validation in FastAPI middleware.
- [x] Create authentication middleware for protected routes.
- [x] Add user profile management endpoints.
- [x] Implement password reset functionality using Supabase Auth.

### API Endpoints
- [x] Design RESTful API structure:
  - [x] `GET /auth/user` - Get current user profile
  - [x] `PUT /auth/user` - Update user profile
  - [x] `GET /cards` - List user's cards
  - [x] `POST /cards` - Create new card
  - [x] `GET /cards/{card_id}` - Get specific card
  - [x] `PUT /cards/{card_id}` - Update card
  - [x] `DELETE /cards/{card_id}` - Delete card
  - [x] `GET /cards/due` - Get due cards for review
  - [x] `POST /cards/{card_id}/review` - Submit card review
  - [x] `GET /reviews` - Get review history
- [x] Implement proper request/response models with Pydantic.
- [x] Add input validation and error handling.
- [x] Implement pagination for list endpoints.

### Business Logic
- [x] Implement spaced repetition algorithm in Python.
- [x] Create card scheduling logic using Supabase database.
- [x] Add review processing and statistics calculation.
- [x] Implement data validation and business rules.
- [x] Add caching for frequently accessed data.

### API Documentation & Testing
- [x] Set up automatic API documentation with Swagger/OpenAPI.
- [x] Write comprehensive API tests with pytest.
- [x] Add integration tests for Supabase operations.
- [x] Implement test fixtures and factories.
- [x] Add performance testing for critical endpoints.

### Security & Performance
- [x] Implement CORS configuration for frontend integration.
- [x] Add rate limiting and request throttling.
- [x] Set up input sanitization and validation.
- [x] Implement proper error handling without exposing internals.
- [x] Add request/response logging and monitoring.

### Frontend Integration
- [x] Create API client service in the frontend.
- [x] Replace IndexedDB operations with API calls.
- [x] Implement authentication state management using Supabase Auth.
- [x] Add loading states and error handling for API calls.
- [x] Create offline fallback to IndexedDB.

### Data Migration
- [ ] Create migration script to transfer existing IndexedDB data to Supabase.
- [ ] Implement data sync between local storage and Supabase.
- [ ] Add offline support with local-first architecture.
- [ ] Handle conflict resolution for concurrent edits.

### Deployment & DevOps
- [ ] Set up Docker containerization for the backend.
- [ ] Configure environment-specific settings (dev/staging/prod).
- [ ] Set up CI/CD pipeline for automated testing and deployment.
- [ ] Configure Supabase backups and monitoring.
- [ ] Set up logging aggregation and error tracking.

---

## 9. Future-Proofing (Post-MVP, Optional)
- [ ] Decks/tags for organization.
- [ ] Image/audio support.
- [ ] Stats and streaks.
- [ ] AI-powered card suggestions.
- [ ] Cloud sync.

