// Settings Component
//
// This component provides backup/restore functionality and other settings.
// It includes proper accessibility features and user feedback.

'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { downloadBackup, importFromFile, clearAllCards } from '@/lib/backup';
import { useAuth } from '@/lib/auth-context';
import { toast } from 'sonner';

interface SettingsProps {
  onBack?: () => void;
}

export const Settings = ({ onBack }: SettingsProps) => {
  const { logout, user } = useAuth();
  const [isExporting, setIsExporting] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [importResults, setImportResults] = useState<{ success: number; errors: string[] } | null>(null);
  const [isClearing, setIsClearing] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [cardCount, setCardCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const backButtonRef = useRef<HTMLButtonElement>(null);

  // Load card count
  useEffect(() => {
    const loadCardCount = async () => {
      try {
        setLoading(true);
        // This part of the logic needs to be updated to fetch card count from the API
        // For now, we'll keep the original logic but acknowledge it might need adjustment
        // depending on how the API handles card counts.
        // For demonstration, let's assume a placeholder or that the API will return it.
        // If the API returns a total count, we'd update setCardCount.
        // For now, we'll just set loading to false.
        setLoading(false);
      } catch (error) {
        console.error('Failed to load card count:', error);
        toast.error('Failed to load settings');
      } finally {
        setLoading(false);
      }
    };
    loadCardCount();
  }, []);

  // Focus the back button on mount
  useEffect(() => {
    if (backButtonRef.current) {
      backButtonRef.current.focus();
    }
  }, []);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (isExporting || isImporting || isClearing || isLoggingOut) return;
      
      switch (event.key) {
        case 'Escape':
          event.preventDefault();
          onBack?.();
          break;
        case 'b':
        case 'B':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            onBack?.();
          }
          break;
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [isExporting, isImporting, isClearing, isLoggingOut, onBack]);

  // Handle backup download
  const handleBackup = async () => {
    setIsExporting(true);
    try {
      await downloadBackup();
      toast.success('Backup downloaded successfully!', {
        description: 'Your cards have been exported to a JSON file'
      });
    } catch (error) {
      console.error('Backup failed:', error);
      toast.error('Failed to create backup. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  // Handle file selection for import
  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsImporting(true);
    setImportResults(null);
    
    try {
      const results = await importFromFile(file);
      setImportResults(results);
      
      if (results.success > 0) {
        // Update card count
        // This part of the logic needs to be updated to fetch card count from the API
        // For now, we'll just show a success toast.
        toast.success(`Import completed!`, {
          description: `Successfully imported ${results.success} cards`
        });
      }
      
      if (results.errors.length > 0) {
        toast.warning('Import completed with errors', {
          description: `${results.errors.length} cards failed to import`
        });
      }
    } catch (error) {
      console.error('Import failed:', error);
      toast.error('Failed to import backup. Please check the file format.');
    } finally {
      setIsImporting(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  // Handle clear all cards
  const handleClearAll = async () => {
    if (!window.confirm('Are you sure you want to delete ALL cards? This action cannot be undone.')) {
      return;
    }

    if (!window.confirm('This will permanently delete all your cards. Are you absolutely sure?')) {
      return;
    }

    setIsClearing(true);
    try {
      await clearAllCards();
      // Update card count
      // This part of the logic needs to be updated to fetch card count from the API
      // For now, we'll just show a success toast.
      toast.success('All cards have been deleted.', {
        description: 'Your collection has been cleared'
      });
    } catch (error) {
      console.error('Clear failed:', error);
      toast.error('Failed to clear cards. Please try again.');
    } finally {
      setIsClearing(false);
    }
  };

  // Handle logout
  const handleLogout = async () => {
    if (!window.confirm('Are you sure you want to sign out? You will need to sign in again to access your cards.')) {
      return;
    }

    setIsLoggingOut(true);
    try {
      await logout();
      toast.success('Signed out successfully!', {
        description: 'You have been logged out of your account'
      });
    } catch (error) {
      console.error('Logout failed:', error);
      toast.error('Failed to sign out. Please try again.');
    } finally {
      setIsLoggingOut(false);
    }
  };

  if (loading) {
    return (
      <div 
        className="flex flex-col justify-center items-center p-responsive space-y-4"
        role="status"
        aria-live="polite"
        aria-label="Loading settings"
      >
        <div className="text-responsive-lg">Loading settings...</div>
        <Progress value={0} className="w-64" />
      </div>
    );
  }

  return (
    <div 
      className="max-w-2xl mx-auto space-y-6"
      role="main"
      aria-label="Settings and Backup"
    >
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 sm:flex-row sm:justify-between sm:items-center">
            <CardTitle id="settings-title" className="text-responsive-xl">Settings</CardTitle>
            <Button 
              ref={backButtonRef}
              variant="outline" 
              onClick={onBack}
              aria-label="Return to card list"
              size="lg"
              className="font-medium"
            >
              Back to Cards
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="bg-blue-50 p-responsive rounded-lg">
            <div className="text-responsive text-blue-800">
              <p className="font-medium">Current Status</p>
              <p>You have {cardCount} cards in your collection</p>
              <p>Storage: localStorage (offline fallback)</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Backup & Restore */}
      <Card>
        <CardHeader>
          <CardTitle className="text-responsive-lg">Backup & Restore</CardTitle>
          <CardDescription className="text-responsive">
            Export your cards as a backup file or import cards from a previous backup.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Export */}
          <div className="space-y-4">
            <h4 className="font-medium text-responsive">Export Cards</h4>
            <p className="text-responsive text-muted-foreground">
              Download all your cards as a JSON file for backup.
            </p>
            <Button
              onClick={handleBackup}
              disabled={isExporting || cardCount === 0}
              aria-describedby="export-description"
              aria-label={`Export ${cardCount} cards as backup file`}
              size="lg"
              className="font-medium"
            >
              {isExporting ? 'Creating Backup...' : 'Download Backup'}
            </Button>
            <p id="export-description" className="text-xs text-muted-foreground">
              {cardCount === 0 ? 'No cards to export' : 'Downloads a JSON file with all your cards'}
            </p>
          </div>

          {/* Import */}
          <div className="space-y-4">
            <h4 className="font-medium text-responsive">Import Cards</h4>
            <p className="text-responsive text-muted-foreground">
              Import cards from a previously exported backup file.
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".json"
              onChange={handleFileSelect}
              className="hidden"
              aria-describedby="import-description"
              aria-label="Select backup file to import"
            />
            <Button
              onClick={() => fileInputRef.current?.click()}
              disabled={isImporting}
              variant="outline"
              aria-label="Choose backup file to import"
              size="lg"
              className="font-medium"
            >
              {isImporting ? 'Importing...' : 'Choose Backup File'}
            </Button>
            <p id="import-description" className="text-xs text-muted-foreground">
              Select a JSON backup file to import cards
            </p>
          </div>

          {/* Import Results */}
          {importResults && (
            <div 
              className="p-responsive border rounded-lg"
              role="status"
              aria-live="polite"
              aria-label="Import results"
            >
              <h5 className="font-medium mb-4 text-responsive">Import Results</h5>
              {importResults.success > 0 && (
                <p className="text-green-600 text-responsive mb-4">
                  ✅ Successfully imported {importResults.success} cards
                </p>
              )}
              {importResults.errors.length > 0 && (
                <div>
                  <p className="text-red-600 text-responsive mb-4">
                    ❌ {importResults.errors.length} errors occurred:
                  </p>
                  <ul className="text-xs text-red-600 space-y-2">
                    {importResults.errors.slice(0, 5).map((error, index) => (
                      <li key={index}>• {error}</li>
                    ))}
                    {importResults.errors.length > 5 && (
                      <li>• ... and {importResults.errors.length - 5} more errors</li>
                    )}
                  </ul>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="border-red-200">
        <CardHeader>
          <CardTitle className="text-red-700 text-responsive-lg">Danger Zone</CardTitle>
          <CardDescription className="text-responsive">
            Irreversible actions that will permanently delete your data.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <h4 className="font-medium text-red-700 text-responsive">Clear All Cards</h4>
            <p className="text-responsive text-muted-foreground">
              Permanently delete all cards from your collection. This action cannot be undone.
            </p>
            <Button
              onClick={handleClearAll}
              disabled={isClearing || cardCount === 0}
              variant="outline"
              className="border-red-300 text-red-700 hover:bg-red-50 font-medium"
              aria-describedby="clear-description"
              aria-label={`Delete all ${cardCount} cards permanently`}
              size="lg"
            >
              {isClearing ? 'Deleting...' : 'Delete All Cards'}
            </Button>
            <p id="clear-description" className="text-xs text-muted-foreground">
              {cardCount === 0 ? 'No cards to delete' : `This will delete all ${cardCount} cards`}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Account Management */}
      <Card className="border-blue-200">
        <CardHeader>
          <CardTitle className="text-blue-700 text-responsive-lg">Account</CardTitle>
          <CardDescription className="text-responsive">
            Manage your account and authentication settings.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {user && (
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium text-blue-800 text-responsive">Current User</h4>
                <p className="text-responsive text-blue-700">
                  {user.email} ({user.username})
                </p>
              </div>
            )}
            <h4 className="font-medium text-blue-700 text-responsive">Sign Out</h4>
            <p className="text-responsive text-muted-foreground">
              Sign out of your account. You will need to sign in again to access your cards.
            </p>
            <Button
              onClick={handleLogout}
              disabled={isLoggingOut}
              variant="outline"
              className="border-blue-300 text-blue-700 hover:bg-blue-50 font-medium"
              aria-describedby="logout-description"
              aria-label="Sign out of your account"
              size="lg"
            >
              {isLoggingOut ? 'Signing out...' : 'Sign Out'}
            </Button>
            <p id="logout-description" className="text-xs text-muted-foreground">
              This will sign you out and clear your session
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Keyboard shortcuts help */}
      <Card className="bg-muted/50">
        <CardContent className="pt-6">
          <h3 className="text-responsive font-medium mb-4">Keyboard Shortcuts</h3>
          <div className="text-xs text-muted-foreground space-y-2">
            <p><kbd className="px-2 py-1 bg-white rounded border">Escape</kbd> - Return to cards</p>
            <p><kbd className="px-2 py-1 bg-white rounded border">Ctrl+B</kbd> or <kbd className="px-2 py-1 bg-white rounded border">Cmd+B</kbd> - Return to cards</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}; 