// Review Mode Component
//
// This component handles the spaced repetition review process.
// It shows cards due for review, displays front/back, and collects ratings.

'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Card as CardType, ReviewRating } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

interface ReviewModeProps {
  onReviewComplete?: () => void;
  onCancel?: () => void;
}

export const ReviewMode = ({ onReviewComplete, onCancel }: ReviewModeProps) => {
  const [dueCards, setDueCards] = useState<CardType[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [progress, setProgress] = useState(0);
  const showAnswerButtonRef = useRef<HTMLButtonElement>(null);
  const forgotButtonRef = useRef<HTMLButtonElement>(null);

  // Load due cards on component mount
  useEffect(() => {
    const loadDueCards = async () => {
      try {
        setLoading(true);
        const cards = await fetchDueCards();
        setDueCards(cards);
        
        // Only show toast for significant events, not on initial load
        // if (cards.length > 0) {
        //   toast.success(`Loaded ${cards.length} cards for review`);
        // }
      } catch (error) {
        console.error('Failed to load due cards:', error);
        toast.error('Failed to load cards for review');
      } finally {
        setLoading(false);
      }
    };

    loadDueCards();
  }, []);

  // Update progress when current index changes
  useEffect(() => {
    if (dueCards.length > 0) {
      // Progress should be based on completed cards, not current index
      const progressValue = (currentIndex / dueCards.length) * 100;
      setProgress(progressValue);
    }
  }, [currentIndex, dueCards.length]);

  // Focus management
  useEffect(() => {
    if (!loading && dueCards.length > 0) {
      if (showAnswer && forgotButtonRef.current) {
        forgotButtonRef.current.focus();
      } else if (!showAnswer && showAnswerButtonRef.current) {
        showAnswerButtonRef.current.focus();
      }
    }
  }, [showAnswer, loading, dueCards.length]);

  // Handle rating submission
  const handleRating = useCallback(async (rating: ReviewRating) => {
    if (!dueCards[currentIndex]) return;

    setSubmitting(true);
    
    try {
      const card = dueCards[currentIndex];
      
      // Add review to card
      await addReview(card.id, {
        date: new Date(),
        rating
      });

      // Update card's spaced repetition parameters
      const updatedCard = await updateCardScheduling(card, rating);
      await updateCard(updatedCard);

      // Move to next card or complete review
      if (currentIndex + 1 < dueCards.length) {
        // Show feedback for individual card rating (only for non-final cards)
        const ratingMessages = {
          easy: 'Great job! This card will be reviewed later.',
          hard: 'Keep practicing! This card will be reviewed soon.',
          forgot: 'No worries! This card will be reviewed tomorrow.'
        };
        
        toast.success(ratingMessages[rating], {
          description: `Card ${currentIndex + 1} of ${dueCards.length} completed`
        });
        
        setCurrentIndex(currentIndex + 1);
        setShowAnswer(false);
      } else {
        // Review complete - let the parent component handle the completion toast
        onReviewComplete?.();
      }
    } catch (error) {
      console.error('Failed to submit rating:', error);
      toast.error('Failed to submit rating. Please try again.');
    } finally {
      setSubmitting(false);
    }
  }, [currentIndex, dueCards, onReviewComplete]);

  // Update card scheduling based on rating (simplified SM-2 algorithm)
  const updateCardScheduling = async (card: CardType, rating: ReviewRating): Promise<CardType> => {
    const updatedCard = { ...card };
    
    switch (rating) {
      case 'easy':
        updatedCard.interval = Math.max(card.interval * 1.5, card.interval + 1);
        updatedCard.ease = Math.min(card.ease + 0.15, 2.5);
        break;
      case 'hard':
        updatedCard.interval = Math.max(card.interval * 0.8, 1);
        updatedCard.ease = Math.max(card.ease - 0.15, 1.3);
        break;
      case 'forgot':
        updatedCard.interval = 1;
        updatedCard.ease = Math.max(card.ease - 0.2, 1.3);
        break;
    }

    // Calculate next review date
    const nextReview = new Date();
    nextReview.setDate(nextReview.getDate() + updatedCard.interval);
    updatedCard.nextReview = nextReview;

    return updatedCard;
  };

  // Handle cancel review
  const handleCancel = useCallback(() => {
    if (currentIndex > 0) {
      if (window.confirm('Are you sure you want to cancel the review? Your progress will be lost.')) {
        toast.info('Review session cancelled', {
          description: `Progress on ${currentIndex} cards was saved`
        });
        onCancel?.();
      }
    } else {
      onCancel?.();
    }
  }, [currentIndex, onCancel]);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (submitting || loading) return;
      
      switch (event.key) {
        case '1':
        case 'f':
        case 'F':
          if (showAnswer) {
            event.preventDefault();
            handleRating('forgot');
          }
          break;
        case '2':
        case 'h':
        case 'H':
          if (showAnswer) {
            event.preventDefault();
            handleRating('hard');
          }
          break;
        case '3':
        case 'e':
        case 'E':
          if (showAnswer) {
            event.preventDefault();
            handleRating('easy');
          }
          break;
        case ' ':
        case 'Enter':
          if (!showAnswer) {
            event.preventDefault();
            setShowAnswer(true);
          }
          break;
        case 'Escape':
          event.preventDefault();
          handleCancel();
          break;
        case 'ArrowLeft':
          if (showAnswer) {
            event.preventDefault();
            handleRating('forgot');
          }
          break;
        case 'ArrowDown':
          if (showAnswer) {
            event.preventDefault();
            handleRating('hard');
          }
          break;
        case 'ArrowRight':
          if (showAnswer) {
            event.preventDefault();
            handleRating('easy');
          }
          break;
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [showAnswer, submitting, currentIndex, loading]);

  if (loading) {
    return (
      <div 
        className="flex flex-col justify-center items-center p-responsive space-y-4"
        role="status"
        aria-live="polite"
        aria-label="Loading due cards"
      >
        <div className="text-responsive-lg">Loading due cards...</div>
        <Progress value={0} className="w-64" />
      </div>
    );
  }

  if (dueCards.length === 0) {
    return (
      <Card className="max-w-2xl mx-auto">
        <CardContent className="text-center py-responsive">
          <div className="text-6xl mb-6" role="img" aria-label="Celebration">🎉</div>
          <h3 className="text-responsive-lg font-semibold mb-4">No cards due for review!</h3>
          <p className="text-responsive text-muted-foreground mb-6">
            Great job! All your cards are up to date.
          </p>
          <Button 
            onClick={onCancel}
            aria-label="Return to card list"
            size="lg"
            className="font-medium"
          >
            Back to Cards
          </Button>
        </CardContent>
      </Card>
    );
  }

  const currentCard = dueCards[currentIndex];
  const progressText = `${currentIndex + 1} of ${dueCards.length}`;

  return (
    <div 
      className="max-w-2xl mx-auto space-y-6"
      role="main"
      aria-label="Review mode"
    >
      {/* Header with Progress */}
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 sm:flex-row sm:justify-between sm:items-center">
            <CardTitle className="text-responsive-xl">Review Cards</CardTitle>
            <Button 
              variant="outline" 
              onClick={handleCancel} 
              disabled={submitting}
              aria-label="Cancel review session"
              size="lg"
              className="font-medium"
            >
              Cancel Review
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-responsive font-medium">Progress</span>
              <span className="text-responsive text-muted-foreground">{progressText}</span>
            </div>
            <Progress value={progress} className="h-3" />
            <p className="text-responsive text-muted-foreground">
              {Math.round(progress)}% complete
            </p>
          </div>
          
          <div className="bg-blue-50 p-responsive rounded-lg">
            <div className="text-responsive text-blue-800">
              <p className="font-medium">
                {showAnswer ? 'Rate how well you remembered each card' : 'Click "Show Answer" to reveal the answer'}
              </p>
              <details className="mt-4">
                <summary className="cursor-pointer font-medium">Keyboard shortcuts</summary>
                <div className="mt-4 space-y-2 text-xs">
                  <p><kbd className="px-2 py-1 bg-white rounded border">Space</kbd> or <kbd className="px-2 py-1 bg-white rounded border">Enter</kbd> - Show answer</p>
                  <p><kbd className="px-2 py-1 bg-white rounded border">1</kbd>, <kbd className="px-2 py-1 bg-white rounded border">F</kbd>, or <kbd className="px-2 py-1 bg-white rounded border">←</kbd> - Forgot</p>
                  <p><kbd className="px-2 py-1 bg-white rounded border">2</kbd>, <kbd className="px-2 py-1 bg-white rounded border">H</kbd>, or <kbd className="px-2 py-1 bg-white rounded border">↓</kbd> - Hard</p>
                  <p><kbd className="px-2 py-1 bg-white rounded border">3</kbd>, <kbd className="px-2 py-1 bg-white rounded border">E</kbd>, or <kbd className="px-2 py-1 bg-white rounded border">→</kbd> - Easy</p>
                  <p><kbd className="px-2 py-1 bg-white rounded border">Esc</kbd> - Cancel review</p>
                </div>
              </details>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Card Display */}
      <div className="space-y-6">
        {/* Front of card */}
        <Card>
          <CardContent className="p-responsive min-h-[200px] flex items-center justify-center">
            <div className="text-center">
              <h3 className="text-responsive-lg font-medium mb-4">Question</h3>
              <p className="text-responsive-xl" aria-label={`Question: ${currentCard.front}`}>
                {currentCard.front}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Show Answer Button */}
        {!showAnswer && (
          <div className="text-center">
            <Button 
              ref={showAnswerButtonRef}
              onClick={() => setShowAnswer(true)}
              size="lg"
              className="px-8 py-6 text-responsive font-medium bg-black text-white hover:bg-gray-800 border-2 border-gray-300"
              aria-label="Show answer to the question"
            >
              Show Answer
            </Button>
          </div>
        )}

        {/* Back of card */}
        {showAnswer && (
          <>
            <Card className="border-green-200 bg-green-50">
              <CardContent className="p-responsive min-h-[200px] flex items-center justify-center">
                <div className="text-center">
                  <h3 className="text-responsive-lg font-medium mb-4 text-green-800">Answer</h3>
                  <p className="text-responsive-xl" aria-label={`Answer: ${currentCard.back}`}>
                    {currentCard.back}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Rating buttons */}
            <Card>
              <CardContent className="p-responsive">
                <div className="space-y-6">
                  <p className="text-center font-medium text-responsive" id="rating-question">
                    How well did you remember this?
                  </p>
                  <div 
                    className="flex flex-col gap-4 sm:flex-row sm:gap-3 sm:justify-center"
                    role="group"
                    aria-labelledby="rating-question"
                  >
                    <Button
                      ref={forgotButtonRef}
                      onClick={() => handleRating('forgot')}
                      disabled={submitting}
                      variant="outline"
                      className="bg-red-50 border-red-200 text-red-700 hover:bg-red-100 font-medium py-6 text-responsive"
                      aria-label="Rate as forgot - card will be reviewed again tomorrow"
                      aria-describedby="forgot-description"
                      size="lg"
                    >
                      Forgot
                    </Button>
                    <Button
                      onClick={() => handleRating('hard')}
                      disabled={submitting}
                      variant="outline"
                      className="bg-yellow-50 border-yellow-200 text-yellow-700 hover:bg-yellow-100 font-medium py-6 text-responsive"
                      aria-label="Rate as hard - card will be reviewed again soon"
                      aria-describedby="hard-description"
                      size="lg"
                    >
                      Hard
                    </Button>
                    <Button
                      onClick={() => handleRating('easy')}
                      disabled={submitting}
                      variant="outline"
                      className="bg-green-50 border-green-200 text-green-700 hover:bg-green-100 font-medium py-6 text-responsive"
                      aria-label="Rate as easy - card will be reviewed later"
                      aria-describedby="easy-description"
                      size="lg"
                    >
                      Easy
                    </Button>
                  </div>
                  <div className="text-xs text-muted-foreground space-y-2 text-center sm:text-left">
                    <p id="forgot-description">Forgot: Card will be reviewed again tomorrow</p>
                    <p id="hard-description">Hard: Card will be reviewed again soon</p>
                    <p id="easy-description">Easy: Card will be reviewed later</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  );
}; 