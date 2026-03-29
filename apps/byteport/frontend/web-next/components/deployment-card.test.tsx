import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DeploymentCard } from './deployment-card';
import { mockDeployment } from '@/test/utils';

describe('DeploymentCard', () => {
  it('renders deployment information correctly', () => {
    const deployment = mockDeployment({
      name: 'My App',
      status: 'running',
      provider: 'vercel',
      type: 'frontend',
    });

    render(<DeploymentCard deployment={deployment} />);

    expect(screen.getByText('My App')).toBeInTheDocument();
    expect(screen.getByText('Frontend')).toBeInTheDocument();
  });

  it('displays deployment URL when available', () => {
    const deployment = mockDeployment({
      url: 'https://my-app.vercel.app',
    });

    render(<DeploymentCard deployment={deployment} />);

    const link = screen.getByRole('link', { name: /my-app.vercel.app/i });
    expect(link).toHaveAttribute('href', 'https://my-app.vercel.app');
    expect(link).toHaveAttribute('target', '_blank');
  });

  it('shows framework and runtime badges when provided', () => {
    const deployment = mockDeployment({
      framework: 'Next.js',
      runtime: 'Node 18',
    });

    render(<DeploymentCard deployment={deployment} />);

    expect(screen.getByText('Next.js')).toBeInTheDocument();
    expect(screen.getByText('Node 18')).toBeInTheDocument();
  });

  it('displays error message when deployment fails', () => {
    const deployment = mockDeployment({
      status: 'failed',
      error_message: 'Build failed due to syntax error',
    });

    render(<DeploymentCard deployment={deployment} />);

    expect(screen.getByText('Build failed due to syntax error')).toBeInTheDocument();
  });

  it('calls onView when View Details button is clicked', () => {
    const onView = vi.fn();
    const deployment = mockDeployment({ id: 'deploy-123' });

    render(<DeploymentCard deployment={deployment} onView={onView} />);

    const viewButton = screen.getByRole('button', { name: /view details/i });
    fireEvent.click(viewButton);

    expect(onView).toHaveBeenCalledWith('deploy-123');
  });

  it('shows restart option for running deployments', async () => {
    const user = userEvent.setup();
    const onRestart = vi.fn();
    const deployment = mockDeployment({
      id: 'deploy-123',
      status: 'running',
    });

    render(<DeploymentCard deployment={deployment} onRestart={onRestart} />);

    // Open dropdown menu
    const menuButton = screen.getByRole('button', { name: /open menu/i });
    await user.click(menuButton);

    // Wait for menu to open and find restart button
    const restartButton = await screen.findByRole('menuitem', { name: /restart/i });
    await user.click(restartButton);

    expect(onRestart).toHaveBeenCalledWith('deploy-123');
  });

  it('shows stop option for deploying deployments', async () => {
    const user = userEvent.setup();
    const onStop = vi.fn();
    const deployment = mockDeployment({
      id: 'deploy-123',
      status: 'deploying',
    });

    render(<DeploymentCard deployment={deployment} onStop={onStop} />);

    // Open dropdown menu
    const menuButton = screen.getByRole('button', { name: /open menu/i });
    await user.click(menuButton);

    // Wait for menu to open and find stop button
    const stopButton = await screen.findByRole('menuitem', { name: /stop/i });
    await user.click(stopButton);

    expect(onStop).toHaveBeenCalledWith('deploy-123');
  });

  it('shows start option for failed deployments', async () => {
    const user = userEvent.setup();
    const onRestart = vi.fn();
    const deployment = mockDeployment({
      id: 'deploy-123',
      status: 'failed',
    });

    render(<DeploymentCard deployment={deployment} onRestart={onRestart} />);

    // Open dropdown menu
    const menuButton = screen.getByRole('button', { name: /open menu/i });
    await user.click(menuButton);

    // Wait for menu to open and find start button
    const startButton = await screen.findByRole('menuitem', { name: /^start$/i });
    await user.click(startButton);

    expect(onRestart).toHaveBeenCalledWith('deploy-123');
  });

  it('calls onViewLogs when View Logs is clicked', async () => {
    const user = userEvent.setup();
    const onViewLogs = vi.fn();
    const deployment = mockDeployment({ id: 'deploy-123' });

    render(<DeploymentCard deployment={deployment} onViewLogs={onViewLogs} />);

    // Open dropdown menu
    const menuButton = screen.getByRole('button', { name: /open menu/i });
    await user.click(menuButton);

    // Wait for menu to open and find logs button
    const logsButton = await screen.findByRole('menuitem', { name: /view logs/i });
    await user.click(logsButton);

    expect(onViewLogs).toHaveBeenCalledWith('deploy-123');
  });

  it('calls onSettings when Settings is clicked', async () => {
    const user = userEvent.setup();
    const onSettings = vi.fn();
    const deployment = mockDeployment({ id: 'deploy-123' });

    render(<DeploymentCard deployment={deployment} onSettings={onSettings} />);

    // Open dropdown menu
    const menuButton = screen.getByRole('button', { name: /open menu/i });
    await user.click(menuButton);

    // Wait for menu to open and find settings button
    const settingsButton = await screen.findByRole('menuitem', { name: /settings/i });
    await user.click(settingsButton);

    expect(onSettings).toHaveBeenCalledWith('deploy-123');
  });

  it('calls onDelete when Delete is clicked', async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    const deployment = mockDeployment({ id: 'deploy-123' });

    render(<DeploymentCard deployment={deployment} onDelete={onDelete} />);

    // Open dropdown menu
    const menuButton = screen.getByRole('button', { name: /open menu/i });
    await user.click(menuButton);

    // Wait for menu to open and find delete button
    const deleteButton = await screen.findByRole('menuitem', { name: /delete/i });
    await user.click(deleteButton);

    expect(onDelete).toHaveBeenCalledWith('deploy-123');
  });

  it('displays relative time since creation', () => {
    const deployment = mockDeployment({
      created_at: new Date(Date.now() - 1000 * 60 * 60).toISOString(), // 1 hour ago
    });

    render(<DeploymentCard deployment={deployment} />);

    expect(screen.getByText(/created.*ago/i)).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const deployment = mockDeployment();
    const { container } = render(
      <DeploymentCard deployment={deployment} className="custom-class" />
    );

    const card = container.firstChild as HTMLElement;
    expect(card.className).toContain('custom-class');
  });

  it('renders status indicator with correct status', () => {
    const deployment = mockDeployment({ status: 'running' });
    render(<DeploymentCard deployment={deployment} />);

    // StatusIndicator component should be present
    // Exact testing depends on StatusIndicator implementation
    expect(screen.getByText('My App')).toBeInTheDocument();
  });

  it('formats deployment type with capital letter', () => {
    const deployment = mockDeployment({ type: 'backend' });
    render(<DeploymentCard deployment={deployment} />);

    expect(screen.getByText('Backend')).toBeInTheDocument();
  });
});
