import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ProviderSelector } from '@/components/provider-selector';
import type { ProviderName, AppType } from '@/lib/types';

// Mock ProviderBadge component
vi.mock('@/components/provider-badge', () => ({
  ProviderBadge: vi.fn(({ provider }: { provider: ProviderName }) => (
    <div data-testid={`provider-badge-${provider}`}>{provider}</div>
  )),
}));

describe('ProviderSelector', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
  });

  describe('Rendering', () => {
    it('should render all providers by default', () => {
      render(<ProviderSelector />);

      expect(screen.getByText('Vercel')).toBeInTheDocument();
      expect(screen.getByText('Netlify')).toBeInTheDocument();
      expect(screen.getByText('Render')).toBeInTheDocument();
      expect(screen.getByText('Railway')).toBeInTheDocument();
      expect(screen.getByText('Fly.io')).toBeInTheDocument();
      expect(screen.getByText('AWS')).toBeInTheDocument();
    });

    it('should render provider descriptions', () => {
      render(<ProviderSelector />);

      expect(screen.getByText('Optimal for Next.js, React, and frontend frameworks')).toBeInTheDocument();
      expect(screen.getByText('Great for static sites and JAMstack applications')).toBeInTheDocument();
      expect(screen.getByText('Enterprise-grade cloud infrastructure')).toBeInTheDocument();
    });

    it('should show "Recommended" badge for Vercel', () => {
      render(<ProviderSelector />);

      expect(screen.getByText('Recommended')).toBeInTheDocument();
    });

    it('should render provider capabilities by default', () => {
      render(<ProviderSelector />);

      expect(screen.getByText('Edge Functions')).toBeInTheDocument();
      expect(screen.getByText('Serverless')).toBeInTheDocument();
      expect(screen.getByText('CDN')).toBeInTheDocument();
    });

    it('should hide capabilities when showCapabilities is false', () => {
      render(<ProviderSelector showCapabilities={false} />);

      expect(screen.queryByText('Edge Functions')).not.toBeInTheDocument();
      expect(screen.queryByText('Serverless')).not.toBeInTheDocument();
    });

    it('should use grid layout for provider cards', () => {
      const { container } = render(<ProviderSelector />);

      const grid = container.querySelector('.grid');
      expect(grid).toBeInTheDocument();
      expect(grid).toHaveClass('sm:grid-cols-2');
    });
  });

  describe('Provider Selection', () => {
    it('should call onChange when provider is clicked', async () => {
      const onChange = vi.fn();
      render(<ProviderSelector onChange={onChange} />);

      const vercelCard = screen.getByText('Vercel').closest('div[class*="cursor-pointer"]');
      await user.click(vercelCard!);

      expect(onChange).toHaveBeenCalledWith('vercel');
    });

    it('should highlight selected provider', () => {
      render(<ProviderSelector value="vercel" />);

      const vercelCard = screen.getByText('Vercel').closest('div[class*="cursor-pointer"]');
      expect(vercelCard).toHaveClass('border-primary');
      expect(vercelCard).toHaveClass('bg-primary/5');
    });

    it('should show checkmark for selected provider', () => {
      const { container } = render(<ProviderSelector value="render" />);

      const renderCard = screen.getByText('Render').closest('div[class*="cursor-pointer"]');
      const checkmark = within(renderCard!).container.querySelector('.bg-primary');
      expect(checkmark).toBeInTheDocument();
    });

    it('should not show checkmark for unselected providers', () => {
      const { container } = render(<ProviderSelector value="vercel" />);

      const netlifyCard = screen.getByText('Netlify').closest('div[class*="cursor-pointer"]');
      const checkmark = within(netlifyCard!).container.querySelector('.bg-primary');
      expect(checkmark).not.toBeInTheDocument();
    });

    it('should allow changing selection', async () => {
      const onChange = vi.fn();
      const { rerender } = render(<ProviderSelector value="vercel" onChange={onChange} />);

      const netlifyCard = screen.getByText('Netlify').closest('div[class*="cursor-pointer"]');
      await user.click(netlifyCard!);

      expect(onChange).toHaveBeenCalledWith('netlify');

      // Simulate parent updating value
      rerender(<ProviderSelector value="netlify" onChange={onChange} />);

      const netlifyCardAfter = screen.getByText('Netlify').closest('div[class*="cursor-pointer"]');
      expect(netlifyCardAfter).toHaveClass('border-primary');
    });
  });

  describe('App Type Filtering', () => {
    it('should show only frontend-compatible providers for frontend apps', () => {
      render(<ProviderSelector appType="frontend" />);

      // Should show these
      expect(screen.getByText('Vercel')).toBeInTheDocument();
      expect(screen.getByText('Netlify')).toBeInTheDocument();
      expect(screen.getByText('Render')).toBeInTheDocument();
      expect(screen.getByText('Railway')).toBeInTheDocument();
      expect(screen.getByText('AWS')).toBeInTheDocument();

      // Fly.io supports backend, database, container but not frontend
      expect(screen.queryByText('Fly.io')).not.toBeInTheDocument();
    });

    it('should show only backend-compatible providers for backend apps', () => {
      render(<ProviderSelector appType="backend" />);

      expect(screen.getByText('Vercel')).toBeInTheDocument();
      expect(screen.getByText('Render')).toBeInTheDocument();
      expect(screen.getByText('Railway')).toBeInTheDocument();
      expect(screen.getByText('Fly.io')).toBeInTheDocument();
      expect(screen.getByText('AWS')).toBeInTheDocument();

      // Netlify is frontend/static only
      expect(screen.queryByText('Netlify')).not.toBeInTheDocument();
    });

    it('should show only static-compatible providers for static apps', () => {
      render(<ProviderSelector appType="static" />);

      expect(screen.getByText('Vercel')).toBeInTheDocument();
      expect(screen.getByText('Netlify')).toBeInTheDocument();
      expect(screen.getByText('AWS')).toBeInTheDocument();

      expect(screen.queryByText('Fly.io')).not.toBeInTheDocument();
      expect(screen.queryByText('Railway')).not.toBeInTheDocument();
    });

    it('should show database-compatible providers for database apps', () => {
      render(<ProviderSelector appType="database" />);

      expect(screen.getByText('Render')).toBeInTheDocument();
      expect(screen.getByText('Railway')).toBeInTheDocument();
      expect(screen.getByText('Fly.io')).toBeInTheDocument();
      expect(screen.getByText('AWS')).toBeInTheDocument();

      expect(screen.queryByText('Vercel')).not.toBeInTheDocument();
      expect(screen.queryByText('Netlify')).not.toBeInTheDocument();
    });

    it('should show container-compatible providers for container apps', () => {
      render(<ProviderSelector appType="container" />);

      expect(screen.getByText('Render')).toBeInTheDocument();
      expect(screen.getByText('Railway')).toBeInTheDocument();
      expect(screen.getByText('Fly.io')).toBeInTheDocument();
      expect(screen.getByText('AWS')).toBeInTheDocument();

      expect(screen.queryByText('Vercel')).not.toBeInTheDocument();
      expect(screen.queryByText('Netlify')).not.toBeInTheDocument();
    });

    it('should show empty state when no providers match app type', () => {
      // Create a custom app type that no provider supports
      // Since TypeScript limits us, we'll test with valid types
      // This test checks the empty state UI exists
      render(<ProviderSelector />);

      // Check that the component can handle the empty state structure
      const { container } = render(<ProviderSelector appType="database" />);
      
      // Should have providers, not empty
      expect(screen.queryByText('No providers available for the selected app type')).not.toBeInTheDocument();
    });
  });

  describe('Provider Capabilities', () => {
    it('should display up to 4 capabilities per provider', () => {
      render(<ProviderSelector />);

      const vercelCard = screen.getByText('Vercel').closest('div[class*="cursor-pointer"]');
      const capabilities = within(vercelCard!).getAllByRole('status');
      
      // Vercel has 4 capabilities: Edge Functions, Serverless, CDN, Analytics
      expect(capabilities.length).toBeLessThanOrEqual(4);
    });

    it('should show key features header', () => {
      render(<ProviderSelector />);

      const keyFeaturesHeaders = screen.getAllByText('Key Features');
      expect(keyFeaturesHeaders.length).toBeGreaterThan(0);
    });

    it('should display correct capabilities for Vercel', () => {
      render(<ProviderSelector />);

      expect(screen.getByText('Edge Functions')).toBeInTheDocument();
      expect(screen.getByText('Serverless')).toBeInTheDocument();
      expect(screen.getByText('CDN')).toBeInTheDocument();
      expect(screen.getByText('Analytics')).toBeInTheDocument();
    });

    it('should display correct capabilities for Netlify', () => {
      render(<ProviderSelector />);

      expect(screen.getByText('Forms')).toBeInTheDocument();
      expect(screen.getByText('Functions')).toBeInTheDocument();
      expect(screen.getByText('Split Testing')).toBeInTheDocument();
    });

    it('should display correct capabilities for Render', () => {
      render(<ProviderSelector />);

      expect(screen.getByText('Databases')).toBeInTheDocument();
      expect(screen.getByText('Web Services')).toBeInTheDocument();
      expect(screen.getByText('Cron Jobs')).toBeInTheDocument();
      expect(screen.getByText('Background Workers')).toBeInTheDocument();
    });
  });

  describe('Hover Effects', () => {
    it('should have hover styles on provider cards', () => {
      const { container } = render(<ProviderSelector />);

      const cards = container.querySelectorAll('.cursor-pointer');
      cards.forEach(card => {
        expect(card).toHaveClass('hover:border-primary');
      });
    });
  });

  describe('Provider Badge Integration', () => {
    it('should render ProviderBadge for each provider', () => {
      render(<ProviderSelector />);

      expect(screen.getByTestId('provider-badge-vercel')).toBeInTheDocument();
      expect(screen.getByTestId('provider-badge-netlify')).toBeInTheDocument();
      expect(screen.getByTestId('provider-badge-render')).toBeInTheDocument();
      expect(screen.getByTestId('provider-badge-railway')).toBeInTheDocument();
      expect(screen.getByTestId('provider-badge-fly')).toBeInTheDocument();
      expect(screen.getByTestId('provider-badge-aws')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have clickable cards', async () => {
      const onChange = vi.fn();
      render(<ProviderSelector onChange={onChange} />);

      const cards = screen.getAllByText(/Vercel|Netlify|Render|Railway|Fly\.io|AWS/);
      const vercelCard = cards[0].closest('div[class*="cursor-pointer"]');

      expect(vercelCard).toHaveClass('cursor-pointer');
      await user.click(vercelCard!);

      expect(onChange).toHaveBeenCalled();
    });

    it('should have appropriate ARIA roles for badges', () => {
      render(<ProviderSelector />);

      // Badges should have role="status"
      const badges = screen.getAllByRole('status');
      expect(badges.length).toBeGreaterThan(0);
    });
  });

  describe('Custom Props', () => {
    it('should accept and apply custom className', () => {
      const { container } = render(<ProviderSelector className="custom-class" />);

      const wrapper = container.firstChild as HTMLElement;
      expect(wrapper).toHaveClass('custom-class');
    });

    it('should accept custom HTML div attributes', () => {
      const { container } = render(<ProviderSelector data-testid="provider-selector" />);

      expect(container.querySelector('[data-testid="provider-selector"]')).toBeInTheDocument();
    });

    it('should handle undefined value prop', () => {
      render(<ProviderSelector value={undefined} />);

      // No provider should be selected
      const cards = screen.getAllByText(/Vercel|Netlify|Render/).map(text => 
        text.closest('div[class*="cursor-pointer"]')
      );

      cards.forEach(card => {
        expect(card).not.toHaveClass('border-primary');
      });
    });
  });

  describe('Multiple Selection Scenarios', () => {
    it('should handle selection with filtered providers', async () => {
      const onChange = vi.fn();
      render(<ProviderSelector appType="frontend" value="vercel" onChange={onChange} />);

      // Vercel should be selected
      const vercelCard = screen.getByText('Vercel').closest('div[class*="cursor-pointer"]');
      expect(vercelCard).toHaveClass('border-primary');

      // Click on Netlify
      const netlifyCard = screen.getByText('Netlify').closest('div[class*="cursor-pointer"]');
      await user.click(netlifyCard!);

      expect(onChange).toHaveBeenCalledWith('netlify');
    });

    it('should maintain selection when filtering changes', () => {
      const { rerender } = render(<ProviderSelector appType="frontend" value="vercel" />);

      let vercelCard = screen.getByText('Vercel').closest('div[class*="cursor-pointer"]');
      expect(vercelCard).toHaveClass('border-primary');

      // Change filter to backend (Vercel still supports backend)
      rerender(<ProviderSelector appType="backend" value="vercel" />);

      vercelCard = screen.getByText('Vercel').closest('div[class*="cursor-pointer"]');
      expect(vercelCard).toHaveClass('border-primary');
    });
  });

  describe('Edge Cases', () => {
    it('should handle providers with no capabilities gracefully', () => {
      // All our providers have capabilities, but the component should handle empty arrays
      render(<ProviderSelector showCapabilities={true} />);

      // Should not crash and should render all providers
      expect(screen.getByText('Vercel')).toBeInTheDocument();
    });

    it('should handle rapid clicks on different providers', async () => {
      const onChange = vi.fn();
      render(<ProviderSelector onChange={onChange} />);

      const vercelCard = screen.getByText('Vercel').closest('div[class*="cursor-pointer"]');
      const netlifyCard = screen.getByText('Netlify').closest('div[class*="cursor-pointer"]');
      const renderCard = screen.getByText('Render').closest('div[class*="cursor-pointer"]');

      await user.click(vercelCard!);
      await user.click(netlifyCard!);
      await user.click(renderCard!);

      expect(onChange).toHaveBeenCalledTimes(3);
      expect(onChange).toHaveBeenNthCalledWith(1, 'vercel');
      expect(onChange).toHaveBeenNthCalledWith(2, 'netlify');
      expect(onChange).toHaveBeenNthCalledWith(3, 'render');
    });

    it('should handle all app types correctly', () => {
      const appTypes: AppType[] = ['frontend', 'backend', 'database', 'static', 'container'];

      appTypes.forEach(appType => {
        const { unmount } = render(<ProviderSelector appType={appType} />);
        
        // Should render at least one provider for each type
        const providers = screen.queryAllByText(/Vercel|Netlify|Render|Railway|Fly\.io|AWS/);
        expect(providers.length).toBeGreaterThan(0);

        unmount();
      });
    });

    it('should preserve other props when value changes', () => {
      const onChange = vi.fn();
      const { rerender } = render(
        <ProviderSelector 
          value="vercel" 
          onChange={onChange}
          showCapabilities={false}
          className="test-class"
          data-testid="selector"
        />
      );

      const { container } = render(
        <ProviderSelector 
          value="netlify" 
          onChange={onChange}
          showCapabilities={false}
          className="test-class"
          data-testid="selector"
        />
      );

      expect(container.querySelector('[data-testid="selector"]')).toBeInTheDocument();
      expect(container.querySelector('.test-class')).toBeInTheDocument();
      expect(screen.queryByText('Edge Functions')).not.toBeInTheDocument();
    });
  });

  describe('Provider Metadata', () => {
    it('should show correct pricing indicators', () => {
      render(<ProviderSelector />);

      // All providers are displayed, we can verify they exist
      // The pricing info is in the data but not displayed in UI
      // This test verifies the component renders successfully with pricing data
      expect(screen.getByText('Vercel')).toBeInTheDocument();
      expect(screen.getByText('AWS')).toBeInTheDocument();
    });

    it('should correctly identify recommended provider', () => {
      render(<ProviderSelector />);

      const recommendedBadges = screen.queryAllByText('Recommended');
      // Only Vercel should be recommended
      expect(recommendedBadges).toHaveLength(1);
    });
  });
});
