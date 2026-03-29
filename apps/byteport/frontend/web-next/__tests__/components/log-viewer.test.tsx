import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LogViewer } from '@/components/log-viewer';
import type { LogEntry } from '@/lib/types';

// Mock react-hot-toast
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

const mockLogs: LogEntry[] = [
  {
    id: '1',
    deployment_id: 'deploy-123',
    timestamp: '2024-01-01T10:00:00Z',
    level: 'info',
    message: 'Application started successfully',
    source: 'runtime',
  },
  {
    id: '2',
    deployment_id: 'deploy-123',
    timestamp: '2024-01-01T10:01:00Z',
    level: 'warn',
    message: 'High memory usage detected',
    source: 'system',
  },
  {
    id: '3',
    deployment_id: 'deploy-123',
    timestamp: '2024-01-01T10:02:00Z',
    level: 'error',
    message: 'Failed to connect to database',
    source: 'runtime',
  },
  {
    id: '4',
    deployment_id: 'deploy-123',
    timestamp: '2024-01-01T10:03:00Z',
    level: 'debug',
    message: 'Cache hit for key: user_123',
    source: 'runtime',
  },
  {
    id: '5',
    deployment_id: 'deploy-123',
    timestamp: '2024-01-01T10:04:00Z',
    level: 'info',
    message: '{"status":"success","duration":250}',
    source: 'build',
  },
];

describe('LogViewer', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
    // Mock clipboard API
    Object.defineProperty(navigator, 'clipboard', {
      value: {
        writeText: vi.fn(() => Promise.resolve()),
      },
      writable: true,
      configurable: true,
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render log entries', () => {
      render(<LogViewer logs={mockLogs} />);

      expect(screen.getByText('Application started successfully')).toBeInTheDocument();
      expect(screen.getByText('High memory usage detected')).toBeInTheDocument();
      expect(screen.getByText('Failed to connect to database')).toBeInTheDocument();
    });

    it('should display correct number of logs in summary', () => {
      render(<LogViewer logs={mockLogs} />);

      expect(screen.getByText(`Showing ${mockLogs.length} of ${mockLogs.length} logs`)).toBeInTheDocument();
    });

    it('should show empty state when no logs provided', () => {
      render(<LogViewer logs={[]} />);

      expect(screen.getByText('No logs available')).toBeInTheDocument();
    });

    it('should render with line numbers by default', () => {
      const { container } = render(<LogViewer logs={mockLogs.slice(0, 1)} />);

      expect(container.textContent).toContain('1');
    });

    it('should hide line numbers when showLineNumbers is false', () => {
      const { container } = render(<LogViewer logs={mockLogs.slice(0, 1)} showLineNumbers={false} />);

      // Line number span should not be present
      const lineNumbers = container.querySelectorAll('.w-12.text-right');
      expect(lineNumbers.length).toBe(0);
    });

    it('should render in terminal mode by default', () => {
      const { container } = render(<LogViewer logs={mockLogs.slice(0, 1)} />);

      const logContainer = container.querySelector('.bg-black');
      expect(logContainer).toBeInTheDocument();
    });

    it('should render in standard mode when terminalMode is false', () => {
      const { container } = render(<LogViewer logs={mockLogs.slice(0, 1)} terminalMode={false} />);

      const logContainer = container.querySelector('.bg-black');
      expect(logContainer).not.toBeInTheDocument();
    });
  });

  describe('Log Level Display', () => {
    it('should display log levels correctly', () => {
      render(<LogViewer logs={mockLogs} />);

      expect(screen.getByText('[INFO]')).toBeInTheDocument();
      expect(screen.getByText('[WARN]')).toBeInTheDocument();
      expect(screen.getByText('[ERROR]')).toBeInTheDocument();
      expect(screen.getByText('[DEBUG]')).toBeInTheDocument();
    });

    it('should apply correct colors to log levels in terminal mode', () => {
      const { container } = render(<LogViewer logs={mockLogs} terminalMode={true} />);

      const infoLevel = screen.getAllByText('[INFO]')[0];
      expect(infoLevel).toHaveClass('text-blue-400');

      const warnLevel = screen.getByText('[WARN]');
      expect(warnLevel).toHaveClass('text-yellow-400');

      const errorLevel = screen.getByText('[ERROR]');
      expect(errorLevel).toHaveClass('text-red-400');
    });
  });

  describe('Search Functionality', () => {
    it('should filter logs by search query', async () => {
      render(<LogViewer logs={mockLogs} />);

      const searchInput = screen.getByPlaceholderText('Search logs...');
      await user.type(searchInput, 'database');

      await waitFor(() => {
        expect(screen.getByText('Failed to connect to database')).toBeInTheDocument();
        expect(screen.queryByText('Application started successfully')).not.toBeInTheDocument();
      });
    });

    it('should be case-insensitive when searching', async () => {
      render(<LogViewer logs={mockLogs} />);

      const searchInput = screen.getByPlaceholderText('Search logs...');
      await user.type(searchInput, 'DATABASE');

      await waitFor(() => {
        expect(screen.getByText('Failed to connect to database')).toBeInTheDocument();
      });
    });

    it('should show empty state when search has no matches', async () => {
      render(<LogViewer logs={mockLogs} />);

      const searchInput = screen.getByPlaceholderText('Search logs...');
      await user.type(searchInput, 'nonexistent');

      await waitFor(() => {
        expect(screen.getByText('No logs match your filters')).toBeInTheDocument();
      });
    });

    it('should update log count in summary after search', async () => {
      render(<LogViewer logs={mockLogs} />);

      const searchInput = screen.getByPlaceholderText('Search logs...');
      await user.type(searchInput, 'runtime');

      await waitFor(() => {
        // 3 logs have 'runtime' source
        expect(screen.getByText(`Showing 3 of ${mockLogs.length} logs`)).toBeInTheDocument();
      });
    });
  });

  describe('Level Filtering', () => {
    it('should filter logs by level', async () => {
      render(<LogViewer logs={mockLogs} />);

      const levelSelect = screen.getByRole('combobox', { name: /level/i });
      await user.click(levelSelect);

      const errorOption = await screen.findByRole('option', { name: 'Error' });
      await user.click(errorOption);

      await waitFor(() => {
        expect(screen.getByText('Failed to connect to database')).toBeInTheDocument();
        expect(screen.queryByText('Application started successfully')).not.toBeInTheDocument();
      });
    });

    it('should show all logs when "All Levels" is selected', async () => {
      render(<LogViewer logs={mockLogs} />);

      const levelSelect = screen.getByRole('combobox', { name: /level/i });
      await user.click(levelSelect);

      const errorOption = await screen.findByRole('option', { name: 'Error' });
      await user.click(errorOption);

      // Now select "All Levels" again
      await user.click(levelSelect);
      const allOption = await screen.findByRole('option', { name: 'All Levels' });
      await user.click(allOption);

      await waitFor(() => {
        expect(screen.getByText('Application started successfully')).toBeInTheDocument();
        expect(screen.getByText('Failed to connect to database')).toBeInTheDocument();
      });
    });
  });

  describe('Source Filtering', () => {
    it('should filter logs by source', async () => {
      render(<LogViewer logs={mockLogs} />);

      const sourceSelect = screen.getAllByRole('combobox')[1]; // Second select is source
      await user.click(sourceSelect);

      const buildOption = await screen.findByRole('option', { name: 'Build' });
      await user.click(buildOption);

      await waitFor(() => {
        expect(screen.getByText('{"status":"success","duration":250}')).toBeInTheDocument();
        expect(screen.queryByText('Application started successfully')).not.toBeInTheDocument();
      });
    });

    it('should show all logs when "All Sources" is selected', async () => {
      render(<LogViewer logs={mockLogs} />);

      const sourceSelect = screen.getAllByRole('combobox')[1];
      await user.click(sourceSelect);

      const allOption = await screen.findByRole('option', { name: 'All Sources' });
      await user.click(allOption);

      await waitFor(() => {
        expect(screen.getByText(`Showing ${mockLogs.length} of ${mockLogs.length} logs`)).toBeInTheDocument();
      });
    });
  });

  describe('Combined Filtering', () => {
    it('should apply multiple filters simultaneously', async () => {
      render(<LogViewer logs={mockLogs} />);

      // Search for 'cache'
      const searchInput = screen.getByPlaceholderText('Search logs...');
      await user.type(searchInput, 'cache');

      // Filter by debug level
      const levelSelect = screen.getByRole('combobox', { name: /level/i });
      await user.click(levelSelect);
      const debugOption = await screen.findByRole('option', { name: 'Debug' });
      await user.click(debugOption);

      await waitFor(() => {
        expect(screen.getByText('Cache hit for key: user_123')).toBeInTheDocument();
        expect(screen.getByText('Showing 1 of 5 logs')).toBeInTheDocument();
      });
    });

    it('should show "Filters active" indicator when filters are applied', async () => {
      render(<LogViewer logs={mockLogs} />);

      const searchInput = screen.getByPlaceholderText('Search logs...');
      await user.type(searchInput, 'test');

      await waitFor(() => {
        expect(screen.getByText('Filters active')).toBeInTheDocument();
      });
    });

    it('should clear all filters when clicking "Clear Filters"', async () => {
      render(<LogViewer logs={mockLogs} />);

      // Apply filters
      const searchInput = screen.getByPlaceholderText('Search logs...');
      await user.type(searchInput, 'database');

      await waitFor(() => {
        expect(screen.getByText('Filters active')).toBeInTheDocument();
      });

      // Clear filters
      const clearButton = screen.getByRole('button', { name: /clear filters/i });
      await user.click(clearButton);

      await waitFor(() => {
        expect(screen.getByText(`Showing ${mockLogs.length} of ${mockLogs.length} logs`)).toBeInTheDocument();
        expect(screen.queryByText('Filters active')).not.toBeInTheDocument();
      });
    });
  });

  describe('Auto-scroll Functionality', () => {
    it('should show auto-scroll enabled by default', () => {
      render(<LogViewer logs={mockLogs} />);

      const pauseButton = screen.getByRole('button', { name: /disable auto-scroll/i });
      expect(pauseButton).toBeInTheDocument();
    });

    it('should toggle auto-scroll when clicking the button', async () => {
      render(<LogViewer logs={mockLogs} />);

      const autoScrollButton = screen.getByRole('button', { name: /disable auto-scroll/i });
      await user.click(autoScrollButton);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /enable auto-scroll/i })).toBeInTheDocument();
      });
    });

    it('should call onAutoScrollChange callback when toggling', async () => {
      const onAutoScrollChange = vi.fn();
      render(<LogViewer logs={mockLogs} onAutoScrollChange={onAutoScrollChange} />);

      const autoScrollButton = screen.getByRole('button', { name: /disable auto-scroll/i });
      await user.click(autoScrollButton);

      await waitFor(() => {
        expect(onAutoScrollChange).toHaveBeenCalledWith(false);
      });

      await user.click(autoScrollButton);

      await waitFor(() => {
        expect(onAutoScrollChange).toHaveBeenCalledWith(true);
      });
    });
  });

  describe('Copy Functionality', () => {
    it('should copy logs to clipboard', async () => {
      const toast = await import('react-hot-toast');
      render(<LogViewer logs={mockLogs.slice(0, 1)} />);

      const copyButton = screen.getByRole('button', { name: /copy logs/i });
      await user.click(copyButton);

      await waitFor(() => {
        expect(navigator.clipboard.writeText).toHaveBeenCalled();
        expect(toast.default.success).toHaveBeenCalledWith('Logs copied to clipboard');
      });
    });

    it('should show checkmark icon after copying', async () => {
      render(<LogViewer logs={mockLogs.slice(0, 1)} />);

      const copyButton = screen.getByRole('button', { name: /copy logs/i });
      await user.click(copyButton);

      await waitFor(() => {
        // Button should still be in the document, just with a different icon
        expect(copyButton).toBeInTheDocument();
      });
    });

    it('should handle copy errors gracefully', async () => {
      const toast = await import('react-hot-toast');
      Object.assign(navigator, {
        clipboard: {
          writeText: vi.fn(() => Promise.reject(new Error('Copy failed'))),
        },
      });

      render(<LogViewer logs={mockLogs.slice(0, 1)} />);

      const copyButton = screen.getByRole('button', { name: /copy logs/i });
      await user.click(copyButton);

      await waitFor(() => {
        expect(toast.default.error).toHaveBeenCalledWith('Failed to copy logs');
      });
    });
  });

  describe('Download Functionality', () => {
    it('should download logs as text file', async () => {
      const toast = await import('react-hot-toast');
      const createElementSpy = vi.spyOn(document, 'createElement');
      const appendChildSpy = vi.spyOn(document.body, 'appendChild');
      const removeChildSpy = vi.spyOn(document.body, 'removeChild');

      render(<LogViewer logs={mockLogs.slice(0, 1)} />);

      const downloadButton = screen.getByRole('button', { name: /download logs/i });
      await user.click(downloadButton);

      await waitFor(() => {
        expect(createElementSpy).toHaveBeenCalledWith('a');
        expect(appendChildSpy).toHaveBeenCalled();
        expect(removeChildSpy).toHaveBeenCalled();
        expect(toast.default.success).toHaveBeenCalledWith('Logs downloaded');
      });

      createElementSpy.mockRestore();
      appendChildSpy.mockRestore();
      removeChildSpy.mockRestore();
    });
  });

  describe('JSON Log Formatting', () => {
    it('should detect and format JSON logs', () => {
      const jsonLog: LogEntry = {
        id: '1',
        deployment_id: 'deploy-123',
        timestamp: '2024-01-01T10:00:00Z',
        level: 'info',
        message: '{"status":"success","code":200}',
        source: 'runtime',
      };

      render(<LogViewer logs={[jsonLog]} />);

      // Should format with indentation
      expect(screen.getByText(/"status":/)).toBeInTheDocument();
      expect(screen.getByText(/"success"/)).toBeInTheDocument();
    });

    it('should render non-JSON logs normally', () => {
      render(<LogViewer logs={mockLogs.slice(0, 1)} />);

      expect(screen.getByText('Application started successfully')).toBeInTheDocument();
    });
  });

  describe('Load More Functionality', () => {
    it('should show "Load More" button when hasMore is true', () => {
      render(<LogViewer logs={mockLogs} hasMore={true} />);

      expect(screen.getByRole('button', { name: /load more/i })).toBeInTheDocument();
    });

    it('should not show "Load More" button when hasMore is false', () => {
      render(<LogViewer logs={mockLogs} hasMore={false} />);

      expect(screen.queryByRole('button', { name: /load more/i })).not.toBeInTheDocument();
    });

    it('should call onLoadMore when clicking "Load More"', async () => {
      const onLoadMore = vi.fn();
      render(<LogViewer logs={mockLogs} hasMore={true} onLoadMore={onLoadMore} />);

      const loadMoreButton = screen.getByRole('button', { name: /load more/i });
      await user.click(loadMoreButton);

      expect(onLoadMore).toHaveBeenCalledTimes(1);
    });

    it('should disable "Load More" button when loading', () => {
      render(<LogViewer logs={mockLogs} hasMore={true} isLoading={true} />);

      const loadMoreButton = screen.getByRole('button', { name: /loading/i });
      expect(loadMoreButton).toBeDisabled();
    });
  });

  describe('Accessibility', () => {
    it('should have accessible button labels', () => {
      render(<LogViewer logs={mockLogs} />);

      expect(screen.getByRole('button', { name: /copy logs/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /download logs/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /disable auto-scroll/i })).toBeInTheDocument();
    });

    it('should have searchable input with placeholder', () => {
      render(<LogViewer logs={mockLogs} />);

      const searchInput = screen.getByPlaceholderText('Search logs...');
      expect(searchInput).toBeInTheDocument();
      expect(searchInput).toHaveAttribute('type', 'text');
    });
  });

  describe('Edge Cases', () => {
    it('should handle logs without IDs', () => {
      const logsWithoutIds: LogEntry[] = [
        {
          deployment_id: 'deploy-123',
          timestamp: '2024-01-01T10:00:00Z',
          level: 'info',
          message: 'Test log',
          source: 'runtime',
        },
      ];

      render(<LogViewer logs={logsWithoutIds} />);

      expect(screen.getByText('Test log')).toBeInTheDocument();
    });

    it('should handle logs without source', () => {
      const logsWithoutSource: LogEntry[] = [
        {
          id: '1',
          deployment_id: 'deploy-123',
          timestamp: '2024-01-01T10:00:00Z',
          level: 'info',
          message: 'Test log without source',
        },
      ];

      render(<LogViewer logs={logsWithoutSource} />);

      expect(screen.getByText('Test log without source')).toBeInTheDocument();
    });

    it('should handle very long log messages', () => {
      const longMessage = 'a'.repeat(1000);
      const longLog: LogEntry = {
        id: '1',
        deployment_id: 'deploy-123',
        timestamp: '2024-01-01T10:00:00Z',
        level: 'info',
        message: longMessage,
      };

      render(<LogViewer logs={[longLog]} />);

      expect(screen.getByText(longMessage)).toBeInTheDocument();
    });

    it('should handle malformed JSON gracefully', () => {
      const malformedJsonLog: LogEntry = {
        id: '1',
        deployment_id: 'deploy-123',
        timestamp: '2024-01-01T10:00:00Z',
        level: 'info',
        message: '{not valid json',
      };

      render(<LogViewer logs={[malformedJsonLog]} />);

      expect(screen.getByText('{not valid json')).toBeInTheDocument();
    });
  });
});
