// Edit Card Form Component
//
// This component provides a form for editing existing flashcards.
// It pre-populates the form with the current card data and handles updates.

'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Card as CardType } from '@/lib/types';
import { toast } from 'sonner';

interface EditCardFormProps {
  card: CardType;
  onCardUpdated?: (updatedCard: CardType) => void;
  onCancel?: () => void;
}

export const EditCardForm = ({ card, onCardUpdated, onCancel }: EditCardFormProps) => {
  const [front, setFront] = useState(card.front);
  const [back, setBack] = useState(card.back);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<{ front?: string; back?: string }>({});
  const [progress, setProgress] = useState(0);
  const frontTextareaRef = useRef<HTMLTextAreaElement>(null);

  // Update form when card prop changes
  useEffect(() => {
    setFront(card.front);
    setBack(card.back);
    setErrors({});
  }, [card]);

  // Focus the first input on mount
  useEffect(() => {
    if (frontTextareaRef.current) {
      frontTextareaRef.current.focus();
    }
  }, []);

  // Update progress based on form completion
  useEffect(() => {
    const frontProgress = front.trim().length >= 3 ? 50 : (front.trim().length / 3) * 50;
    const backProgress = back.trim().length >= 3 ? 50 : (back.trim().length / 3) * 50;
    setProgress(frontProgress + backProgress);
  }, [front, back]);

  // Validate form inputs
  const validateForm = (): boolean => {
    const newErrors: { front?: string; back?: string } = {};

    if (!front.trim()) {
      newErrors.front = 'Front content is required';
    } else if (front.trim().length < 3) {
      newErrors.front = 'Front content must be at least 3 characters';
    }

    if (!back.trim()) {
      newErrors.back = 'Back content is required';
    } else if (back.trim().length < 3) {
      newErrors.back = 'Back content must be at least 3 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

    // Handle form submission
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      toast.error('Please fix the errors before submitting');
      return;
    }

    setIsSubmitting(true);
    
    try {
      const updatedCard: CardType = {
        ...card,
        front: front.trim(),
        back: back.trim(),
        updatedAt: new Date()
      };
      
      // In a real application, you would call an API endpoint here
      // For example: await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/cards`, { method: 'PUT', body: JSON.stringify(updatedCard) });
      // This is a placeholder for actual API interaction
      console.log('Simulating API update for:', updatedCard);
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate network delay
      
      toast.success('Card updated successfully!', {
        description: 'Your flashcard has been saved'
      });
      
      // Notify parent component
      onCardUpdated?.(updatedCard);
    } catch (error) {
      console.error('Failed to update card:', error);
      toast.error('Failed to update card. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }, [front, back, card, onCardUpdated]);

  // Handle cancel
  const handleCancel = useCallback(() => {
    const hasChanges = front !== card.front || back !== card.back;
    
    if (hasChanges) {
      if (window.confirm('Are you sure you want to cancel? Your changes will be lost.')) {
        toast.info('Card editing cancelled');
        onCancel?.();
      }
    } else {
      onCancel?.();
    }
  }, [front, back, card.front, card.back, onCancel]);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (isSubmitting) return;
      
      switch (event.key) {
        case 'Escape':
          event.preventDefault();
          handleCancel();
          break;
        case 'Enter':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            // Trigger form submission
            const form = document.querySelector('form');
            if (form) {
              form.requestSubmit();
            }
          }
          break;
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [isSubmitting, front, back, card.front, card.back]);

  // Check if form has unsaved changes
  const hasChanges = front !== card.front || back !== card.back;

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle id="edit-card-title" className="text-responsive-xl">Edit Card</CardTitle>
        <CardDescription className="text-responsive">
          Update the front and back content of your flashcard.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form 
          onSubmit={handleSubmit} 
          className="space-y-6"
          aria-labelledby="edit-card-title"
          noValidate
        >
          {/* Progress indicator */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-responsive font-medium">Form Progress</span>
              <span className="text-responsive text-muted-foreground">{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>

          {/* Front (Question) */}
          <div className="space-y-3">
            <label htmlFor="front" className="text-responsive font-medium">
              Front (Question)
            </label>
            <Textarea
              id="front"
              ref={frontTextareaRef}
              value={front}
              onChange={(e) => setFront(e.target.value)}
              placeholder="Enter the question or prompt..."
              className={`min-h-[120px] text-responsive ${errors.front ? 'border-red-500' : ''}`}
              rows={4}
              disabled={isSubmitting}
              aria-describedby={errors.front ? 'front-error' : 'front-help'}
              aria-invalid={!!errors.front}
              aria-required="true"
            />
            {errors.front ? (
              <p id="front-error" className="text-responsive text-red-600" role="alert">
                {errors.front}
              </p>
            ) : (
              <p id="front-help" className="text-xs text-muted-foreground">
                Minimum 3 characters required
              </p>
            )}
          </div>

          {/* Back (Answer) */}
          <div className="space-y-3">
            <label htmlFor="back" className="text-responsive font-medium">
              Back (Answer)
            </label>
            <Textarea
              id="back"
              value={back}
              onChange={(e) => setBack(e.target.value)}
              placeholder="Enter the answer..."
              className={`min-h-[120px] text-responsive ${errors.back ? 'border-red-500' : ''}`}
              rows={4}
              disabled={isSubmitting}
              aria-describedby={errors.back ? 'back-error' : 'back-help'}
              aria-invalid={!!errors.back}
              aria-required="true"
            />
            {errors.back ? (
              <p id="back-error" className="text-responsive text-red-600" role="alert">
                {errors.back}
              </p>
            ) : (
              <p id="back-help" className="text-xs text-muted-foreground">
                Minimum 3 characters required
              </p>
            )}
          </div>

          {/* Card info */}
          <Card className="bg-muted/50">
            <CardContent className="pt-6">
              <h3 className="text-responsive font-medium mb-4">Card Information</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-responsive">
                <div>
                  <p className="text-muted-foreground">Created</p>
                  <p>{new Date(card.createdAt).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Last updated</p>
                  <p>{new Date(card.updatedAt).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Reviews</p>
                  <Badge variant="secondary" className="text-responsive">{card.reviewHistory.length}</Badge>
                </div>
                <div>
                  <p className="text-muted-foreground">Next review</p>
                  <p>{new Date(card.nextReview).toLocaleDateString()}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Action buttons */}
          <div className="flex flex-col gap-3 sm:flex-row sm:gap-3 pt-6">
            <Button
              type="submit"
              disabled={isSubmitting || !hasChanges || progress < 100}
              className="flex-1 font-medium"
              aria-describedby="form-instructions"
              size="lg"
            >
              {isSubmitting ? 'Updating Card...' : 'Update Card'}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={handleCancel}
              disabled={isSubmitting}
              aria-label="Cancel editing card"
              size="lg"
              className="font-medium"
            >
              Cancel
            </Button>
          </div>
          <div id="form-instructions" className="text-xs text-muted-foreground space-y-2">
            <p>Press Ctrl+Enter (or Cmd+Enter) to save changes</p>
            <p>Press Escape to cancel</p>
            {hasChanges && (
              <p className="text-blue-600">You have unsaved changes</p>
            )}
            {progress < 100 && (
              <p className="text-orange-600">Complete both fields to enable submission</p>
            )}
          </div>
        </form>
      </CardContent>
    </Card>
  );
}; 