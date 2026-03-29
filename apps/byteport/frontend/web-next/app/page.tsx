import Link from 'next/link';
import { ArrowRight, Cloud, Zap, Shield, Code, Server, LayoutDashboard, Terminal } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-dark-surface via-dark-surfaceContainer to-dark-surface">
      {/* Navigation */}
      <nav className="border-b border-dark-surfaceVariant bg-dark-surfaceContainer/50 backdrop-blur-sm">
        <div className="container mx-auto flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <Terminal className="h-6 w-6 text-dark-primary" />
            <span className="text-xl font-bold text-dark-onSurface">BytePort</span>
          </div>
          <div className="flex items-center gap-4">
            <Link
              href="/login"
              className="text-sm font-medium text-dark-onSurfaceVariant transition hover:text-dark-primary"
            >
              Sign In
            </Link>
            <Link
              href="/login"
              className="rounded-lg bg-dark-primary px-4 py-2 text-sm font-medium text-white transition hover:bg-dark-primary/90"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-6 py-24 text-center lg:py-32">
        <div className="mx-auto max-w-4xl space-y-8">
          <div className="inline-flex items-center gap-2 rounded-full border border-dark-surfaceVariant bg-dark-surfaceContainerHigh px-4 py-2 text-sm text-dark-onSurfaceVariant">
            <Zap className="h-4 w-4 text-dark-primary" />
            <span>Deploy to any cloud in minutes</span>
          </div>

          <h1 className="bg-gradient-to-r from-dark-onSurface via-dark-onSurfaceVariant to-dark-onSurface bg-clip-text text-5xl font-bold leading-tight text-transparent lg:text-7xl">
            Deploy Anywhere,
            <br />
            <span className="bg-gradient-to-r from-dark-primary to-blue-400 bg-clip-text">
              From One Plan
            </span>
          </h1>

          <p className="mx-auto max-w-2xl text-lg text-dark-onSurfaceVariant lg:text-xl">
            BytePort is your universal deployment platform. Write once, deploy everywhere.
            Support for Vercel, Netlify, Render, AWS, and more - all from a single declarative configuration.
          </p>

          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link
              href="/login"
              className="group flex items-center gap-2 rounded-lg bg-dark-primary px-6 py-3 text-base font-medium text-white transition hover:bg-dark-primary/90"
            >
              Start Deploying
              <ArrowRight className="h-5 w-5 transition group-hover:translate-x-1" />
            </Link>
            <Link
              href="#features"
              className="rounded-lg border border-dark-surfaceVariant px-6 py-3 text-base font-medium text-dark-onSurface transition hover:bg-dark-surfaceContainerHigh"
            >
              Learn More
            </Link>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-8 pt-12">
            <div className="space-y-1">
              <div className="text-3xl font-bold text-dark-primary">10+</div>
              <div className="text-sm text-dark-secondary">Cloud Providers</div>
            </div>
            <div className="space-y-1">
              <div className="text-3xl font-bold text-dark-primary">99.9%</div>
              <div className="text-sm text-dark-secondary">Uptime SLA</div>
            </div>
            <div className="space-y-1">
              <div className="text-3xl font-bold text-dark-primary">1000+</div>
              <div className="text-sm text-dark-secondary">Deployments/day</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="container mx-auto px-6 py-24">
        <div className="mb-16 text-center">
          <h2 className="text-3xl font-bold text-dark-onSurface lg:text-4xl">
            Everything you need to ship faster
          </h2>
          <p className="mt-4 text-lg text-dark-onSurfaceVariant">
            Powerful features that make deployment a breeze
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {/* Feature 1 */}
          <div className="group rounded-xl border border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-6 transition hover:border-dark-primary hover:shadow-lg">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-dark-primary/10">
              <Cloud className="h-6 w-6 text-dark-primary" />
            </div>
            <h3 className="mb-2 text-xl font-semibold text-dark-onSurface">Multi-Cloud Support</h3>
            <p className="text-dark-onSurfaceVariant">
              Deploy to Vercel, Netlify, Render, Railway, AWS, GCP, and Azure from one unified platform.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="group rounded-xl border border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-6 transition hover:border-dark-primary hover:shadow-lg">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-dark-primary/10">
              <Zap className="h-6 w-6 text-dark-primary" />
            </div>
            <h3 className="mb-2 text-xl font-semibold text-dark-onSurface">Lightning Fast</h3>
            <p className="text-dark-onSurfaceVariant">
              Optimized build pipelines and intelligent caching ensure your deployments complete in seconds.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="group rounded-xl border border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-6 transition hover:border-dark-primary hover:shadow-lg">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-dark-primary/10">
              <Shield className="h-6 w-6 text-dark-primary" />
            </div>
            <h3 className="mb-2 text-xl font-semibold text-dark-onSurface">Enterprise Security</h3>
            <p className="text-dark-onSurfaceVariant">
              End-to-end encryption, SOC 2 compliance, and advanced access controls keep your deployments secure.
            </p>
          </div>

          {/* Feature 4 */}
          <div className="group rounded-xl border border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-6 transition hover:border-dark-primary hover:shadow-lg">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-dark-primary/10">
              <Code className="h-6 w-6 text-dark-primary" />
            </div>
            <h3 className="mb-2 text-xl font-semibold text-dark-onSurface">GitOps Native</h3>
            <p className="text-dark-onSurfaceVariant">
              Connect your GitHub, GitLab, or Bitbucket repository and deploy automatically on every push.
            </p>
          </div>

          {/* Feature 5 */}
          <div className="group rounded-xl border border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-6 transition hover:border-dark-primary hover:shadow-lg">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-dark-primary/10">
              <Server className="h-6 w-6 text-dark-primary" />
            </div>
            <h3 className="mb-2 text-xl font-semibold text-dark-onSurface">Auto-Scaling</h3>
            <p className="text-dark-onSurfaceVariant">
              Automatically scale your applications based on traffic patterns and resource utilization.
            </p>
          </div>

          {/* Feature 6 */}
          <div className="group rounded-xl border border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-6 transition hover:border-dark-primary hover:shadow-lg">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-dark-primary/10">
              <LayoutDashboard className="h-6 w-6 text-dark-primary" />
            </div>
            <h3 className="mb-2 text-xl font-semibold text-dark-onSurface">Unified Dashboard</h3>
            <p className="text-dark-onSurfaceVariant">
              Monitor all your deployments, view logs, and manage configurations from a single interface.
            </p>
          </div>
        </div>
      </section>

      {/* Code Example Section */}
      <section className="container mx-auto px-6 py-24">
        <div className="mb-16 text-center">
          <h2 className="text-3xl font-bold text-dark-onSurface lg:text-4xl">
            Deploy with a single YAML file
          </h2>
          <p className="mt-4 text-lg text-dark-onSurfaceVariant">
            Define your infrastructure once, deploy anywhere
          </p>
        </div>

        <div className="mx-auto max-w-4xl">
          <div className="overflow-hidden rounded-xl border border-dark-surfaceVariant bg-dark-surfaceContainerHigh">
            <div className="flex items-center justify-between border-b border-dark-surfaceVariant bg-dark-surfaceContainer px-4 py-3">
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-red-500" />
                <div className="h-3 w-3 rounded-full bg-yellow-500" />
                <div className="h-3 w-3 rounded-full bg-green-500" />
              </div>
              <span className="text-xs text-dark-secondary">byteport.yaml</span>
            </div>
            <pre className="overflow-x-auto p-6">
              <code className="font-mono text-sm text-dark-onSurfaceVariant">
{`name: my-app
version: 1.0.0

services:
  frontend:
    type: nextjs
    provider: vercel
    branch: main
    auto_deploy: true

  backend:
    type: nodejs
    provider: render
    env:
      - DATABASE_URL: \${database.url}

  database:
    type: postgres
    provider: supabase
    plan: free`}
              </code>
            </pre>
          </div>

          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            <div className="rounded-lg border border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-4 text-center">
              <Code className="mx-auto mb-2 h-8 w-8 text-dark-primary" />
              <p className="text-sm font-medium text-dark-onSurface">One Config</p>
              <p className="mt-1 text-xs text-dark-secondary">Single source of truth</p>
            </div>
            <div className="rounded-lg border border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-4 text-center">
              <Cloud className="mx-auto mb-2 h-8 w-8 text-dark-primary" />
              <p className="text-sm font-medium text-dark-onSurface">Any Provider</p>
              <p className="mt-1 text-xs text-dark-secondary">10+ cloud platforms</p>
            </div>
            <div className="rounded-lg border border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-4 text-center">
              <Zap className="mx-auto mb-2 h-8 w-8 text-dark-primary" />
              <p className="text-sm font-medium text-dark-onSurface">Zero Config</p>
              <p className="mt-1 text-xs text-dark-secondary">Auto-detection & setup</p>
            </div>
          </div>
        </div>
      </section>

      {/* Providers Section */}
      <section className="container mx-auto px-6 py-24">
        <div className="mb-12 text-center">
          <h2 className="text-2xl font-bold text-dark-onSurface lg:text-3xl">
            Deploy to your favorite platforms
          </h2>
          <p className="mt-3 text-dark-onSurfaceVariant">
            BytePort integrates seamlessly with all major cloud providers
          </p>
        </div>

        <div className="mx-auto grid max-w-5xl grid-cols-2 gap-8 md:grid-cols-4 lg:grid-cols-6">
          {['Vercel', 'Netlify', 'Render', 'Railway', 'AWS', 'Azure', 'GCP', 'Fly.io', 'Supabase', 'Cloudflare', 'DigitalOcean', 'Heroku'].map((provider) => (
            <div
              key={provider}
              className="flex items-center justify-center rounded-lg border border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-4 transition hover:border-dark-primary hover:bg-dark-surfaceContainerHighest"
            >
              <span className="text-sm font-medium text-dark-onSurfaceVariant">{provider}</span>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-6 py-24">
        <div className="rounded-2xl border border-dark-surfaceVariant bg-gradient-to-br from-dark-surfaceContainerHigh to-dark-surfaceContainer p-12 text-center">
          <h2 className="mb-4 text-3xl font-bold text-dark-onSurface lg:text-4xl">
            Ready to deploy anywhere?
          </h2>
          <p className="mb-8 text-lg text-dark-onSurfaceVariant">
            Join thousands of developers shipping to production with confidence.
          </p>
          <Link
            href="/login"
            className="inline-flex items-center gap-2 rounded-lg bg-dark-primary px-8 py-4 text-base font-medium text-white transition hover:bg-dark-primary/90"
          >
            Get Started for Free
            <ArrowRight className="h-5 w-5" />
          </Link>
          <p className="mt-4 text-sm text-dark-secondary">
            No credit card required • Deploy in 5 minutes
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-dark-surfaceVariant bg-dark-surfaceContainer py-8">
        <div className="container mx-auto px-6 text-center text-sm text-dark-secondary">
          <p>&copy; 2025 BytePort. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
