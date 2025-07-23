'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { apiClient } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { toast } from 'sonner';

export default function AuthCallback() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refreshUser } = useAuth();
  const [isProcessing, setIsProcessing] = useState(true);

  useEffect(() => {
    const handleOAuthCallback = async () => {
      try {
        // Log all search params for debugging
        console.log('OAuth callback search params:', Object.fromEntries(searchParams.entries()));
        
        const code = searchParams.get('code');
        const state = searchParams.get('state');
        const error = searchParams.get('error');
        const errorDescription = searchParams.get('error_description');
        const provider = searchParams.get('provider') || 'google';

        // Verify state parameter
        const storedState = sessionStorage.getItem('oauth_state');
        if (state && storedState && state !== storedState) {
          console.error('State parameter mismatch');
          toast.error('OAuth security verification failed');
          router.push('/');
          return;
        }

        // Clear stored state
        sessionStorage.removeItem('oauth_state');

        if (error) {
          console.error('OAuth error:', error, errorDescription);
          toast.error(`OAuth authentication failed: ${errorDescription || error}`);
          router.push('/');
          return;
        }

        if (!code) {
          console.error('No authorization code received');
          console.log('Available params:', Object.fromEntries(searchParams.entries()));
          toast.error('No authorization code received');
          router.push('/');
          return;
        }

        console.log('Processing OAuth callback with code:', code.substring(0, 10) + '...');

        // Exchange code for session
        const response = await apiClient.oauthLogin(
          provider as 'google',
          code,
          window.location.origin + '/auth/callback'
        );

        console.log('OAuth login successful:', response);

        // Refresh the auth context to update the user state
        await refreshUser();

        if (response.is_new_user) {
          toast.success('Your account has been created.');
        } else {
          toast.success('Welcome back to Anki-AI!');
        }

        // Small delay to ensure auth context is updated
        setTimeout(() => {
          // Redirect to main app
          router.push('/');
        }, 500);
      } catch (error) {
        console.error('OAuth callback error:', error);
        toast.error('Authentication failed. Please try again.');
        router.push('/');
      } finally {
        setIsProcessing(false);
      }
    };

    handleOAuthCallback();
  }, [searchParams, router, refreshUser]);

  return (
    <div className="flex flex-col justify-center items-center min-h-screen space-y-4">
      <div className="text-lg">Completing authentication...</div>
      <div className="w-64 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div className="h-full bg-blue-600 animate-pulse"></div>
      </div>
      <div className="text-sm text-gray-500">Please wait while we set up your account</div>
    </div>
  );
} 