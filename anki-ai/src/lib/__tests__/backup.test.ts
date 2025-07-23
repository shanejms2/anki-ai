import { downloadBackup, importFromFile, clearAllCards } from '../backup';
import { storage } from '../storage';

// Mock the storage module
jest.mock('../storage', () => ({
  storage: {
    getAllCards: jest.fn(),
    deleteCard: jest.fn(),
    addCard: jest.fn(),
    updateCard: jest.fn(),
  },
}));

// Mock DOM elements and operations
const mockAppendChild = jest.fn();
const mockRemoveChild = jest.fn();
const mockClick = jest.fn();

// Mock document.createElement
Object.defineProperty(document, 'createElement', {
  value: jest.fn(() => ({
    appendChild: mockAppendChild,
    removeChild: mockRemoveChild,
    click: mockClick,
    style: {},
  })),
  writable: true,
});

// Mock document.body
Object.defineProperty(document, 'body', {
  value: {
    appendChild: mockAppendChild,
    removeChild: mockRemoveChild,
  },
  writable: true,
});

// Mock URL.createObjectURL and URL.revokeObjectURL
global.URL.createObjectURL = jest.fn(() => 'mock-url');
global.URL.revokeObjectURL = jest.fn();

describe('Backup Module', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (storage.getAllCards as jest.Mock).mockResolvedValue([]);
    (storage.addCard as jest.Mock).mockResolvedValue('test-id');
    (storage.updateCard as jest.Mock).mockResolvedValue(undefined);
    (storage.deleteCard as jest.Mock).mockResolvedValue(undefined);
  });

  describe('downloadBackup', () => {
    it('should create and download a backup file', async () => {
      const mockCards = [
        {
          id: '1',
          front: 'Test Front',
          back: 'Test Back',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          nextReview: new Date().toISOString(),
          interval: 1,
          ease: 2.5,
          reviewHistory: [],
        },
      ];

      (storage.getAllCards as jest.Mock).mockResolvedValue(mockCards);

      await downloadBackup();

      expect(storage.getAllCards).toHaveBeenCalled();
      expect(document.createElement).toHaveBeenCalledWith('a');
      expect(global.URL.createObjectURL).toHaveBeenCalled();
      expect(mockClick).toHaveBeenCalled();
      expect(global.URL.revokeObjectURL).toHaveBeenCalled();
    });

    it('should handle empty card list', async () => {
      await downloadBackup();

      expect(storage.getAllCards).toHaveBeenCalled();
      expect(document.createElement).toHaveBeenCalledWith('a');
    });

    it('should handle storage errors', async () => {
      (storage.getAllCards as jest.Mock).mockRejectedValue(new Error('Storage error'));

      await expect(downloadBackup()).rejects.toThrow('Failed to download backup');
    });
  });

  describe('importFromFile', () => {
    it('should import valid backup file successfully', async () => {
      // Mock FileReader to return valid JSON
      const mockFileReader = {
        onload: null as unknown as (ev: unknown) => void,
        readAsText: jest.fn().mockImplementation(() => {
          setTimeout(() => {
            if (mockFileReader.onload) {
              mockFileReader.onload({
                target: { result: '{"cards":[]}' }
              });
            }
          }, 0);
        })
      };

      global.FileReader = jest.fn(() => mockFileReader) as unknown as typeof FileReader;

      const mockFile = new File(['{"cards":[]}'], 'backup.json', { type: 'application/json' });

      const result = await importFromFile(mockFile);

      expect(result.success).toBe(0);
      expect(result.errors).toHaveLength(0);
    });

    it('should handle invalid JSON file', async () => {
      // Mock FileReader to return invalid JSON
      const mockFileReader = {
        onload: null as unknown as (ev: unknown) => void,
        readAsText: jest.fn().mockImplementation(() => {
          setTimeout(() => {
            if (mockFileReader.onload) {
              mockFileReader.onload({
                target: { result: 'invalid json' }
              });
            }
          }, 0);
        })
      };

      global.FileReader = jest.fn(() => mockFileReader) as unknown as typeof FileReader;

      const mockFile = new File(['invalid json'], 'backup.json', { type: 'application/json' });

      await expect(importFromFile(mockFile)).rejects.toThrow('Failed to import cards: Invalid file format');
    });

    it('should handle non-array data', async () => {
      // Mock FileReader to return non-array data
      const mockFileReader = {
        onload: null as unknown as (ev: unknown) => void,
        readAsText: jest.fn().mockImplementation(() => {
          setTimeout(() => {
            if (mockFileReader.onload) {
              mockFileReader.onload({
                target: { result: '{"cards":"not an array"}' }
              });
            }
          }, 0);
        })
      };

      global.FileReader = jest.fn(() => mockFileReader) as unknown as typeof FileReader;

      const mockFile = new File(['{"cards":"not an array"}'], 'backup.json', { type: 'application/json' });

      await expect(importFromFile(mockFile)).rejects.toThrow('Failed to import cards: Invalid file format');
    });
  });

  describe('clearAllCards', () => {
    it('should clear all cards successfully', async () => {
      const mockCards = [
        { id: '1', front: 'Test 1', back: 'Answer 1' },
        { id: '2', front: 'Test 2', back: 'Answer 2' },
      ];

      (storage.getAllCards as jest.Mock).mockResolvedValue(mockCards);

      await clearAllCards();

      expect(storage.getAllCards).toHaveBeenCalled();
      expect(storage.deleteCard).toHaveBeenCalledTimes(2);
    });

    it('should handle empty card list', async () => {
      await clearAllCards();

      expect(storage.getAllCards).toHaveBeenCalled();
      expect(storage.deleteCard).not.toHaveBeenCalled();
    });

    it('should handle storage errors', async () => {
      (storage.getAllCards as jest.Mock).mockRejectedValue(new Error('Storage error'));

      await expect(clearAllCards()).rejects.toThrow('Failed to clear cards');
    });
  });
}); 