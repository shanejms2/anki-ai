// Backup and restore functionality
//
// This file provides functions to export all cards as JSON and import them back.
// This allows users to backup their data and restore it on other devices or after clearing browser data.

// Remove: import { storage } from './storage';

// TODO: Refactor exportCards, importCards, downloadBackup, importFromFile, clearAllCards to use only API-based logic or remove if not possible.
// For now, just export empty implementations to avoid build errors.

export const exportCards = async (): Promise<string> => {
  // Not implemented: cloud-only mode
  return JSON.stringify([]);
};

export const downloadBackup = async (): Promise<void> => {
  // Not implemented: cloud-only mode
};

export const importCards = async (jsonData: string): Promise<{ success: number; errors: string[] }> => {
  // Not implemented: cloud-only mode
  return { success: 0, errors: ['Import not supported in cloud-only mode.'] };
};

export const importFromFile = async (file: File): Promise<{ success: number; errors: string[] }> => {
  // Not implemented: cloud-only mode
  return { success: 0, errors: ['Import not supported in cloud-only mode.'] };
};

export const clearAllCards = async (): Promise<void> => {
  // Not implemented: cloud-only mode
}; 