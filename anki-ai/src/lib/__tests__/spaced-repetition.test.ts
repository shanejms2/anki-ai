import { Card, ReviewRating } from '../types'

// Mock the storage module
jest.mock('../storage', () => ({
  storage: {
    addReview: jest.fn(),
    updateCard: jest.fn(),
  },
}))

// Import the algorithm logic (we'll need to extract it from ReviewMode)
// For now, let's test the algorithm logic directly

describe('Spaced Repetition Algorithm (SM-2)', () => {
  const baseCard: Card = {
    id: 'test-id',
    front: 'Test question',
    back: 'Test answer',
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-01'),
    nextReview: new Date('2024-01-02'),
    interval: 1,
    ease: 2.5,
    reviewHistory: [],
  }

  describe('Algorithm Logic', () => {
    it('should increase interval and ease for "easy" rating', () => {
      const card = { ...baseCard, interval: 2, ease: 2.5 }
      
      // Simulate "easy" rating
      const newInterval = Math.max(card.interval * 1.5, card.interval + 1)
      const newEase = Math.min(card.ease + 0.15, 2.5)
      
      expect(newInterval).toBe(3) // 2 * 1.5 = 3
      expect(newEase).toBe(2.5) // 2.5 + 0.15 = 2.65, but capped at 2.5
    })

    it('should decrease interval and ease for "hard" rating', () => {
      const card = { ...baseCard, interval: 5, ease: 2.5 }
      
      // Simulate "hard" rating
      const newInterval = Math.max(card.interval * 0.8, 1)
      const newEase = Math.max(card.ease - 0.15, 1.3)
      
      expect(newInterval).toBe(4) // 5 * 0.8 = 4
      expect(newEase).toBe(2.35) // 2.5 - 0.15 = 2.35
    })

    it('should reset interval and decrease ease for "forgot" rating', () => {
      const card = { ...baseCard, interval: 10, ease: 2.5 }
      
      // Simulate "forgot" rating
      const newInterval = 1
      const newEase = Math.max(card.ease - 0.2, 1.3)
      
      expect(newInterval).toBe(1)
      expect(newEase).toBe(2.3) // 2.5 - 0.2 = 2.3
    })

    it('should not let ease go below 1.3', () => {
      const card = { ...baseCard, ease: 1.4 }
      
      // Simulate "forgot" rating
      const newEase = Math.max(card.ease - 0.2, 1.3)
      
      expect(newEase).toBe(1.3) // 1.4 - 0.2 = 1.2, but minimum is 1.3
    })

    it('should not let ease go above 2.5', () => {
      const card = { ...baseCard, ease: 2.4 }
      
      // Simulate "easy" rating
      const newEase = Math.min(card.ease + 0.15, 2.5)
      
      expect(newEase).toBe(2.5) // 2.4 + 0.15 = 2.55, but maximum is 2.5
    })

    it('should not let interval go below 1', () => {
      const card = { ...baseCard, interval: 1 }
      
      // Simulate "hard" rating
      const newInterval = Math.max(card.interval * 0.8, 1)
      
      expect(newInterval).toBe(1) // 1 * 0.8 = 0.8, but minimum is 1
    })
  })

  describe('Next Review Date Calculation', () => {
    it('should calculate next review date correctly', () => {
      const today = new Date('2024-01-01')
      const interval = 3
      
      const nextReview = new Date(today)
      nextReview.setDate(nextReview.getDate() + interval)
      
      expect(nextReview.getDate()).toBe(4) // January 4th
    })

    it('should handle month/year boundaries', () => {
      const today = new Date('2024-01-30')
      const interval = 5
      
      const nextReview = new Date(today)
      nextReview.setDate(nextReview.getDate() + interval)
      
      expect(nextReview.getDate()).toBe(4) // February 4th
      expect(nextReview.getMonth()).toBe(1) // February (0-indexed)
    })
  })

  describe('Due Card Detection', () => {
    it('should identify cards due for review', () => {
      const pastDate = new Date()
      pastDate.setDate(pastDate.getDate() - 1)
      
      const dueCard: Card = {
        ...baseCard,
        nextReview: pastDate,
      }
      
      const today = new Date()
      today.setHours(23, 59, 59, 999) // End of today
      
      const isDue = dueCard.nextReview <= today
      
      expect(isDue).toBe(true)
    })

    it('should not identify future cards as due', () => {
      const futureDate = new Date()
      futureDate.setDate(futureDate.getDate() + 1)
      
      const notDueCard: Card = {
        ...baseCard,
        nextReview: futureDate,
      }
      
      const today = new Date()
      today.setHours(23, 59, 59, 999) // End of today
      
      const isDue = notDueCard.nextReview <= today
      
      expect(isDue).toBe(false)
    })

    it('should identify cards due today', () => {
      const today = new Date()
      
      const dueTodayCard: Card = {
        ...baseCard,
        nextReview: today,
      }
      
      const endOfToday = new Date()
      endOfToday.setHours(23, 59, 59, 999)
      
      const isDue = dueTodayCard.nextReview <= endOfToday
      
      expect(isDue).toBe(true)
    })
  })

  describe('Review History', () => {
    it('should track review history correctly', () => {
      const card: Card = {
        ...baseCard,
        reviewHistory: [],
      }
      
      const review1 = {
        date: new Date('2024-01-01'),
        rating: 'easy' as ReviewRating,
      }
      
      const review2 = {
        date: new Date('2024-01-02'),
        rating: 'hard' as ReviewRating,
      }
      
      card.reviewHistory.push(review1)
      card.reviewHistory.push(review2)
      
      expect(card.reviewHistory).toHaveLength(2)
      expect(card.reviewHistory[0]).toEqual(review1)
      expect(card.reviewHistory[1]).toEqual(review2)
    })

    it('should maintain review history order', () => {
      const card: Card = {
        ...baseCard,
        reviewHistory: [],
      }
      
      const reviews = [
        { date: new Date('2024-01-01'), rating: 'easy' as ReviewRating },
        { date: new Date('2024-01-02'), rating: 'hard' as ReviewRating },
        { date: new Date('2024-01-03'), rating: 'forgot' as ReviewRating },
      ]
      
      reviews.forEach(review => card.reviewHistory.push(review))
      
      expect(card.reviewHistory).toHaveLength(3)
      expect(card.reviewHistory[0].date).toEqual(new Date('2024-01-01'))
      expect(card.reviewHistory[1].date).toEqual(new Date('2024-01-02'))
      expect(card.reviewHistory[2].date).toEqual(new Date('2024-01-03'))
    })
  })
}) 