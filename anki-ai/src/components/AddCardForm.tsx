// Add Card Form Component
//
// This component provides a form for creating new flashcards with validation.
// It handles the front and back content, validates input, and saves to the database.

'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api';

interface AddCardFormProps {
  onCardAdded?: () => void;
  onCancel?: () => void;
}

export const AddCardForm = ({ onCardAdded, onCancel }: AddCardFormProps) => {
  const [front, setFront] = useState('');
  const [back, setBack] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<{ front?: string; back?: string }>({});
  const [progress, setProgress] = useState(0);
  const frontTextareaRef = useRef<HTMLTextAreaElement>(null);

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
      // Call the backend API to create the card
      await apiClient.createCard({
        front: front.trim(),
        back: back.trim()
      });

      // Reset form
      setFront('');
      setBack('');
      setErrors({});
      setProgress(0);
      
      toast.success('Card created successfully!', {
        description: 'Your new flashcard has been created and is ready for review'
      });
      
      // Notify parent component
      onCardAdded?.();
    } catch (error) {
      console.error('Failed to add card:', error);
      toast.error('Failed to add card. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }, [front, back, onCardAdded]);

  // Handle cancel
  const handleCancel = useCallback(() => {
    if (front.trim() || back.trim()) {
      if (window.confirm('Are you sure you want to cancel? Your changes will be lost.')) {
        toast.info('Card creation cancelled');
        onCancel?.();
      }
    } else {
      onCancel?.();
    }
  }, [front, back, onCancel]);

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
  }, [isSubmitting, front, back]);

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle id="add-card-title" className="text-responsive-xl">Add New Card</CardTitle>
        <CardDescription className="text-responsive">
          Create a new flashcard with a question on the front and answer on the back.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form 
          onSubmit={handleSubmit} 
          className="space-y-6"
          aria-labelledby="add-card-title"
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

          {/* Action buttons */}
          <div className="flex flex-col gap-3 sm:flex-row sm:gap-3 pt-6">
            <Button
              type="submit"
              disabled={isSubmitting || progress < 100}
              className="flex-1 font-medium"
              aria-describedby="form-instructions"
              size="lg"
            >
              {isSubmitting ? 'Adding Card...' : 'Add Card'}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={handleCancel}
              disabled={isSubmitting}
              aria-label="Cancel adding new card"
              size="lg"
              className="font-medium"
            >
              Cancel
            </Button>
          </div>
          <div id="form-instructions" className="text-xs text-muted-foreground space-y-2">
            <p>Press Ctrl+Enter (or Cmd+Enter) to submit the form</p>
            <p>Press Escape to cancel</p>
            {progress < 100 && (
              <p className="text-blue-600">Complete both fields to enable submission</p>
            )}
          </div>
        </form>
      </CardContent>
    </Card>
  );
}; 