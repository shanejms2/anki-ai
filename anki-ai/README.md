# Anki-AI

A modern, AI-ready spaced repetition flashcard application built with Next.js, TypeScript, and TailwindCSS.

## Features

- **Spaced Repetition**: Implements the SM-2 algorithm for optimal learning intervals
- **Card Management**: Create, edit, and delete flashcards with ease
- **Review System**: Intelligent review scheduling based on your performance
- **Data Persistence**: Local storage with IndexedDB and localStorage fallback
- **Backup & Restore**: Import/export your cards as JSON files
- **Modern UI**: Beautiful, accessible interface built with Shadcn UI
- **Keyboard Navigation**: Full keyboard accessibility support

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm, yarn, pnpm, or bun

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd anki-ai
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

### Adding Cards

1. Click the "Add Card" button
2. Fill in the front (question) and back (answer) fields
3. Click "Save Card" to add it to your collection

### Reviewing Cards

1. Click "Review Due Cards" to start a review session
2. Read the question on the front of the card
3. Click "Show Answer" to reveal the answer
4. Rate your performance:
   - **Easy**: Card will be scheduled further in the future
   - **Hard**: Card will be reviewed sooner
   - **Forgot**: Card will be reviewed again soon

### Managing Cards

- **Edit**: Click the edit icon on any card to modify it
- **Delete**: Click the delete icon to remove a card (with confirmation)
- **View All**: Browse all your cards in the main list

### Backup & Restore

- **Export**: Click "Export Cards" to download your data as a JSON file
- **Import**: Click "Import Cards" to restore from a previously exported file

## Technical Details

### Architecture

- **Frontend**: Next.js 14 with App Router
- **Styling**: TailwindCSS with Shadcn UI components
- **Database**: Dexie.js (IndexedDB) with localStorage fallback
- **Testing**: Jest with comprehensive test coverage
- **Type Safety**: Full TypeScript implementation

### Data Model

```typescript
interface Card {
  id: string;
  front: string;
  back: string;
  interval: number;
  ease: number;
  nextReview: Date;
  reviewHistory: Review[];
  createdAt: Date;
  updatedAt: Date;
}

interface Review {
  id: string;
  cardId: string;
  rating: 'easy' | 'hard' | 'forgot';
  reviewedAt: Date;
}
```

### Spaced Repetition Algorithm

The app implements a simplified SM-2 algorithm:

- **Easy**: Increases interval and ease factor
- **Hard**: Decreases interval, maintains ease factor
- **Forgot**: Resets interval to 1 day, decreases ease factor

## Development

### Running Tests

```bash
npm test
```

### Building for Production

```bash
npm run build
npm start
```

### Code Quality

- ESLint for code linting
- Prettier for code formatting
- TypeScript for type safety
- Jest for unit testing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Roadmap

- [ ] Decks and tags for organization
- [ ] Image and audio support
- [ ] Statistics and learning analytics
- [ ] AI-powered card suggestions
- [ ] Cloud synchronization
- [ ] Mobile app
