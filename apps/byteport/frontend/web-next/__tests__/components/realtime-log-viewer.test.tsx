import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { RealtimeLogViewer } from '@/components/realtime-log-viewer';
import type { LogEntry } from '@/lib/types';

// Mock the hooks
const mockLogStream = {
  logs: [] as LogEntry[],
  isConnected: false,
  isConnecting: false,
  error: null as Event | null,
  reconnectAttempts: 0,
  clearLogs: vi.fn(),
  reconnect: vi.fn(),
};

vi.mock('@/lib/hooks/use-log-stream', () => ({
  useLogStream: vi.fn(() => mockLogStream),
}));

// Mock the LogViewer component
vi.mock('@/components/log-viewer', () => ({
  LogViewer: vi.fn(({ logs }) => (
    <div data-testid="log-viewer">
      {logs.map((log: LogEntry) => (
        <div key={log.id}>{log.message}</div>
      ))}
    </div>
  )),
}));

const mockLogs: LogEntry[] = [
  {
    id: '1',
    deployment_id: 'deploy-123',
    timestamp: '2024-01-01T10:00:00Z',
    level: 'info',
    message: 'Application started',
    source: 'runtime',
  },
  {
    id: '2',
    deployment_id: 'deploy-123',
    timestamp: '2024-01-01T10:01:00Z',
    level: 'info',
    message: 'Server listening on port 3000',
    source: 'runtime',
  },
];

describe('RealtimeLogViewer', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
    // Reset mock state
    mockLogStream.logs = [];
    mockLogStream.isConnected = false;
    mockLogStream.isConnecting = false;
    mockLogStream.error = null;
    mockLogStream.reconnectAttempts = 0;
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render with no deployment selected', () => {
      render(<RealtimeLogViewer deploymentId={null} />);

      expect(screen.getByText('No deployment selected')).toBeInTheDocument();
    });

    it('should render log viewer when deployment is selected', () => {
      mockLogStream.isConnected = true;
      mockLogStream.logs = mockLogs;

      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      expect(screen.getByTestId('log-viewer')).toBeInTheDocument();
    });

    it('should pass correct props to LogViewer', () => {
      const LogViewer = require('@/components/log-viewer').LogViewer;
      mockLogStream.logs = mockLogs;
      mockLogStream.isConnected = true;

      render(
        <RealtimeLogViewer
          deploymentId="deploy-123"
          autoScroll={false}
          showLineNumbers={false}
          terminalMode={false}
        />
      );

      expect(LogViewer).toHaveBeenCalledWith(
        expect.objectContaining({
          logs: mockLogs,
          autoScroll: false,
          showLineNumbers: false,
          terminalMode: false,
        }),
        expect.anything()
      );
    });
  });

  describe('Connection Status', () => {
    it('should show "Connecting..." status when connecting', () => {
      mockLogStream.isConnecting = true;

      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      expect(screen.getByText('Connecting...')).toBeInTheDocument();
    });

    it('should show "Live" status when connected', () => {
      mockLogStream.isConnected = true;

      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      expect(screen.getByText('Live')).toBeInTheDocument();
    });

    it('should show "Disconnected" status when not connected', () => {
      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      expect(screen.getByText('Disconnected')).toBeInTheDocument();
    });

    it('should show error status with reconnect attempts', () => {
      mockLogStream.error = new Event('error');
      mockLogStream.reconnectAttempts = 3;

      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      expect(screen.getByText('Error (Attempt 3)')).toBeInTheDocument();
    });
  });

  describe('Log Count Display', () => {
    it('should display log count when connected', () => {
      mockLogStream.isConnected = true;
      mockLogStream.logs = mockLogs;

      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      expect(screen.getByText('2 logs')).toBeInTheDocument();
    });

    it('should show singular "log" when count is 1', () => {
      mockLogStream.isConnected = true;
      mockLogStream.logs = [mockLogs[0]];

      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      expect(screen.getByText('1 log')).toBeInTheDocument();
    });

    it('should show max logs warning when limit is reached', () => {
      mockLogStream.isConnected = true;
      const maxLogs = 100;
      mockLogStream.logs = Array.from({ length: maxLogs }, (_, i) => ({
        id: `${i}`,
        deployment_id: 'deploy-123',
        timestamp: '2024-01-01T10:00:00Z',
        level: 'info' as const,
        message: `Log ${i}`,
      }));

      render(<RealtimeLogViewer deploymentId="deploy-123" maxLogs={maxLogs} />);

      expect(screen.getByText(/showing last 100/i)).toBeInTheDocument();
    });

    it('should not display log count when not connected', () => {
      mockLogStream.isConnected = false;
      mockLogStream.logs = mockLogs;

      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      expect(screen.queryByText(/logs?$/)).not.toBeInTheDocument();
    });
  });

  describe('Clear Logs Functionality', () => {
    it('should render "Clear Logs" button', () => {
      mockLogStream.logs = mockLogs;

      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      expect(screen.getByRole('button', { name: /clear logs/i })).toBeInTheDocument();
    });

    it('should call clearLogs when button is clicked', async () => {
      mockLogStream.logs = mockLogs;

      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      const clearButton = screen.getByRole('button', { name: /clear logs/i });
      await user.click(clearButton);

      expect(mockLogStream.clearLogs).toHaveBeenCalledTimes(1);
    });

    it('should disable "Clear Logs" button when no logs', () => {
      mockLogStream.logs = [];

      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      const clearButton = screen.getByRole('button', { name: /clear logs/i });
      expect(clearButton).toBeDisabled();
    });

    it('should enable "Clear Logs" button when logs are present', () => {
      mockLogStream.logs = mockLogs;

      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      const clearButton = screen.getByRole('button', { name: /clear logs/i });
      expect(clearButton).not.toBeDisabled();
    });
  });

  describe('Reconnect Functionality', () => {
    it('should show "Retry Connection" button when there is an error', () => {
      mockLogStream.error = new Event('error');

      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      expect(screen.getByRole('button', { name: /retry connection/i })).toBeInTheDocument();
    });

    it('should not show "Retry Connection" button when no error', () => {
      mockLogStream.isConnected = true;

      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      expect(screen.queryByRole('button', { name: /retry connection/i })).not.toBeInTheDocument();
    });

    it('should call reconnect when "Retry Connection" is clicked', async () => {
      mockLogStream.error = new Event('error');

      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      const retryButton = screen.getByRole('button', { name: /retry connection/i });
      await user.click(retryButton);

      expect(mockLogStream.reconnect).toHaveBeenCalledTimes(1);
    });
  });

  describe('Empty States', () => {
    it('should show waiting message when not connected and no logs', () => {
      mockLogStream.isConnected = false;
      mockLogStream.isConnecting = false;
      mockLogStream.logs = [];

      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      expect(screen.getByText('Waiting for logs from deployment...')).toBeInTheDocument();
    });

    it('should not show waiting message when connected', () => {
      mockLogStream.isConnected = true;
      mockLogStream.logs = [];

      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      expect(screen.queryByText('Waiting for logs from deployment...')).not.toBeInTheDocument();
    });

    it('should not show waiting message when connecting', () => {
      mockLogStream.isConnecting = true;
      mockLogStream.logs = [];

      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      expect(screen.queryByText('Waiting for logs from deployment...')).not.toBeInTheDocument();
    });

    it('should not show waiting message when logs are present', () => {
      mockLogStream.logs = mockLogs;

      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      expect(screen.queryByText('Waiting for logs from deployment...')).not.toBeInTheDocument();
    });
  });

  describe('Props Handling', () => {
    it('should accept custom className', () => {
      const { container } = render(
        <RealtimeLogViewer deploymentId="deploy-123" className="custom-class" />
      );

      const wrapper = container.firstChild as HTMLElement;
      expect(wrapper).toHaveClass('custom-class');
    });

    it('should pass autoScroll prop to LogViewer', () => {
      const LogViewer = require('@/components/log-viewer').LogViewer;
      mockLogStream.isConnected = true;

      render(<RealtimeLogViewer deploymentId="deploy-123" autoScroll={false} />);

      expect(LogViewer).toHaveBeenCalledWith(
        expect.objectContaining({ autoScroll: false }),
        expect.anything()
      );
    });

    it('should pass showLineNumbers prop to LogViewer', () => {
      const LogViewer = require('@/components/log-viewer').LogViewer;
      mockLogStream.isConnected = true;

      render(<RealtimeLogViewer deploymentId="deploy-123" showLineNumbers={false} />);

      expect(LogViewer).toHaveBeenCalledWith(
        expect.objectContaining({ showLineNumbers: false }),
        expect.anything()
      );
    });

    it('should pass terminalMode prop to LogViewer', () => {
      const LogViewer = require('@/components/log-viewer').LogViewer;
      mockLogStream.isConnected = true;

      render(<RealtimeLogViewer deploymentId="deploy-123" terminalMode={false} />);

      expect(LogViewer).toHaveBeenCalledWith(
        expect.objectContaining({ terminalMode: false }),
        expect.anything()
      );
    });

    it('should handle maxLogs prop', () => {
      const useLogStream = require('@/lib/hooks/use-log-stream').useLogStream;

      render(<RealtimeLogViewer deploymentId="deploy-123" maxLogs={500} />);

      expect(useLogStream).toHaveBeenCalledWith(
        expect.objectContaining({
          deploymentId: 'deploy-123',
          enabled: true,
          maxLogs: 500,
        })
      );
    });
  });

  describe('Connection State Transitions', () => {
    it('should update status badge when connection state changes', async () => {
      mockLogStream.isConnecting = true;

      const { rerender } = render(<RealtimeLogViewer deploymentId="deploy-123" />);

      expect(screen.getByText('Connecting...')).toBeInTheDocument();

      // Simulate connection established
      mockLogStream.isConnecting = false;
      mockLogStream.isConnected = true;

      rerender(<RealtimeLogViewer deploymentId="deploy-123" />);

      await waitFor(() => {
        expect(screen.getByText('Live')).toBeInTheDocument();
      });
    });

    it('should show error state after failed connection', async () => {
      mockLogStream.isConnecting = true;

      const { rerender } = render(<RealtimeLogViewer deploymentId="deploy-123" />);

      expect(screen.getByText('Connecting...')).toBeInTheDocument();

      // Simulate connection error
      mockLogStream.isConnecting = false;
      mockLogStream.error = new Event('error');
      mockLogStream.reconnectAttempts = 1;

      rerender(<RealtimeLogViewer deploymentId="deploy-123" />);

      await waitFor(() => {
        expect(screen.getByText('Error (Attempt 1)')).toBeInTheDocument();
      });
    });
  });

  describe('Real-time Log Updates', () => {
    it('should display new logs as they arrive', async () => {
      mockLogStream.isConnected = true;
      mockLogStream.logs = [mockLogs[0]];

      const { rerender } = render(<RealtimeLogViewer deploymentId="deploy-123" />);

      expect(screen.getByText('Application started')).toBeInTheDocument();
      expect(screen.getByText('1 log')).toBeInTheDocument();

      // Simulate new log arriving
      mockLogStream.logs = mockLogs;

      rerender(<RealtimeLogViewer deploymentId="deploy-123" />);

      await waitFor(() => {
        expect(screen.getByText('Server listening on port 3000')).toBeInTheDocument();
        expect(screen.getByText('2 logs')).toBeInTheDocument();
      });
    });

    it('should update log count when logs are cleared', async () => {
      mockLogStream.isConnected = true;
      mockLogStream.logs = mockLogs;

      const { rerender } = render(<RealtimeLogViewer deploymentId="deploy-123" />);

      expect(screen.getByText('2 logs')).toBeInTheDocument();

      // Simulate logs being cleared
      mockLogStream.logs = [];

      rerender(<RealtimeLogViewer deploymentId="deploy-123" />);

      await waitFor(() => {
        expect(screen.queryByText(/logs?$/)).not.toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have accessible button labels', () => {
      mockLogStream.logs = mockLogs;
      mockLogStream.error = new Event('error');

      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      expect(screen.getByRole('button', { name: /retry connection/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /clear logs/i })).toBeInTheDocument();
    });

    it('should have appropriate status indicators', () => {
      mockLogStream.isConnected = true;

      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      // Status badge should be visible
      expect(screen.getByText('Live')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle null deploymentId gracefully', () => {
      render(<RealtimeLogViewer deploymentId={null} />);

      expect(screen.getByText('No deployment selected')).toBeInTheDocument();
      expect(screen.queryByTestId('log-viewer')).not.toBeInTheDocument();
    });

    it('should handle empty string deploymentId', () => {
      render(<RealtimeLogViewer deploymentId="" />);

      // Should be treated similar to null
      expect(screen.getByText('No deployment selected')).toBeInTheDocument();
    });

    it('should handle very large log counts', () => {
      mockLogStream.isConnected = true;
      const largeLogCount = 10000;
      mockLogStream.logs = Array.from({ length: largeLogCount }, (_, i) => ({
        id: `${i}`,
        deployment_id: 'deploy-123',
        timestamp: '2024-01-01T10:00:00Z',
        level: 'info' as const,
        message: `Log ${i}`,
      }));

      render(<RealtimeLogViewer deploymentId="deploy-123" maxLogs={largeLogCount} />);

      expect(screen.getByText(`${largeLogCount} logs`)).toBeInTheDocument();
    });

    it('should handle multiple reconnect attempts', () => {
      mockLogStream.error = new Event('error');
      mockLogStream.reconnectAttempts = 10;

      render(<RealtimeLogViewer deploymentId="deploy-123" />);

      expect(screen.getByText('Error (Attempt 10)')).toBeInTheDocument();
    });
  });
});
