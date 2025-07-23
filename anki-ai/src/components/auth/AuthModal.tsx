'use client';

import React, { useState } from 'react';
import { LoginForm } from './LoginForm';
import { RegisterForm } from './RegisterForm';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';

type AuthMode = 'login' | 'register';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: AuthMode;
  onSuccess?: () => void;
}

export function AuthModal({ 
  isOpen, 
  onClose, 
  initialMode = 'login',
  onSuccess 
}: AuthModalProps) {
  const [mode, setMode] = useState<AuthMode>(initialMode);

  const handleSuccess = () => {
    onSuccess?.();
    onClose();
  };

  const switchMode = () => {
    setMode(mode === 'login' ? 'register' : 'login');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative z-10 w-full max-w-md mx-4">
        {/* Close button */}
        <Button
          variant="ghost"
          size="sm"
          className="absolute -top-2 -right-2 h-8 w-8 rounded-full bg-background border shadow-sm hover:bg-muted"
          onClick={onClose}
        >
          <X className="h-4 w-4" />
        </Button>

        {/* Auth form */}
        {mode === 'login' ? (
          <LoginForm
            onSuccess={handleSuccess}
            onSwitchToRegister={switchMode}
          />
        ) : (
          <RegisterForm
            onSuccess={handleSuccess}
            onSwitchToLogin={switchMode}
          />
        )}
      </div>
    </div>
  );
} 