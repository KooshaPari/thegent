'use client';

import { useState } from 'react';
import { deployApp } from '@/lib/api';
import type { DeployRequest, DeploymentResponse } from '@/lib/types';

export default function DeployPage() {
  const [deploying, setDeploying] = useState(false);
  const [result, setResult] = useState<DeploymentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<DeployRequest>({
    name: '',
    type: 'frontend',
    git_url: '',
    branch: 'main',
    env_vars: {},
  });

  const handleDeploy = async (e: React.FormEvent) => {
    e.preventDefault();
    setDeploying(true);
    setError(null);
    setResult(null);

    try {
      const response = await deployApp(formData);
      setResult(response);
    } catch (err: any) {
      setError(err.message || 'Deployment failed');
    } finally {
      setDeploying(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <div className="container mx-auto p-8 max-w-4xl">
      <h1 className="text-4xl font-bold mb-2">Deploy Your App</h1>
      <p className="text-gray-600 mb-8">
        Deploy to the best free-tier cloud providers automatically
      </p>

      {!result ? (
        <div className="bg-white rounded-lg shadow-lg p-8">
          <form onSubmit={handleDeploy} className="space-y-6">
            {/* App Name */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                App Name *
              </label>
              <input
                type="text"
                id="name"
                name="name"
                required
                value={formData.name}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="my-awesome-app"
              />
            </div>

            {/* App Type */}
            <div>
              <label htmlFor="type" className="block text-sm font-medium text-gray-700 mb-2">
                App Type *
              </label>
              <select
                id="type"
                name="type"
                required
                value={formData.type}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="frontend">Frontend (React, Next.js, Static)</option>
                <option value="backend">Backend (Node.js, Go, Python)</option>
                <option value="database">Database (PostgreSQL)</option>
              </select>
            </div>

            {/* Provider (Optional) */}
            <div>
              <label htmlFor="provider" className="block text-sm font-medium text-gray-700 mb-2">
                Provider (Auto-detected if empty)
              </label>
              <select
                id="provider"
                name="provider"
                value={formData.provider}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Auto-select best provider</option>
                <option value="vercel">Vercel (Best for Frontend)</option>
                <option value="netlify">Netlify (Frontend)</option>
                <option value="render">Render (Backend)</option>
                <option value="railway">Railway (Backend)</option>
                <option value="supabase">Supabase (Database)</option>
                <option value="cloudflare-pages">Cloudflare Pages (Static)</option>
              </select>
            </div>

            {/* Git URL (Optional) */}
            <div>
              <label htmlFor="git_url" className="block text-sm font-medium text-gray-700 mb-2">
                Git Repository URL (Optional)
              </label>
              <input
                type="url"
                id="git_url"
                name="git_url"
                value={formData.git_url}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="https://github.com/user/repo"
              />
            </div>

            {/* Branch */}
            <div>
              <label htmlFor="branch" className="block text-sm font-medium text-gray-700 mb-2">
                Branch
              </label>
              <input
                type="text"
                id="branch"
                name="branch"
                value={formData.branch}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="main"
              />
            </div>

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                <p className="font-medium">Deployment Failed</p>
                <p className="text-sm">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={deploying}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
            >
              {deploying ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Deploying...
                </span>
              ) : (
                'Deploy Now (100% Free)'
              )}
            </button>

            <p className="text-center text-sm text-gray-500">
              ✨ All deployments use free tiers - zero cost, zero config
            </p>
          </form>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
              <svg
                className="w-8 h-8 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Deployment Started!</h2>
            <p className="text-gray-600">{result.message}</p>
          </div>

          <div className="bg-gray-50 rounded-lg p-6 space-y-4">
            <div className="flex justify-between items-center pb-2 border-b">
              <span className="text-gray-600">Deployment ID</span>
              <span className="font-mono text-sm">{result.id}</span>
            </div>
            <div className="flex justify-between items-center pb-2 border-b">
              <span className="text-gray-600">Status</span>
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                {result.status}
              </span>
            </div>
            <div className="flex justify-between items-center pb-2 border-b">
              <span className="text-gray-600">Provider</span>
              <span className="font-medium">{result.provider}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">URL</span>
              <a
                href={result.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                {result.url}
              </a>
            </div>
          </div>

          <div className="mt-6 flex gap-4">
            <a
              href={`/deployments/${result.id}`}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg text-center transition-colors duration-200"
            >
              View Deployment Status
            </a>
            <button
              onClick={() => {
                setResult(null);
                setFormData({
                  name: '',
                  type: 'frontend',
                  git_url: '',
                  branch: 'main',
                  env_vars: {},
                });
              }}
              className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
            >
              Deploy Another App
            </button>
          </div>
        </div>
      )}

      {/* Feature Highlights */}
      <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="text-center">
          <div className="text-3xl mb-2">⚡</div>
          <h3 className="font-semibold mb-1">Lightning Fast</h3>
          <p className="text-sm text-gray-600">Deploy in 2-5 minutes</p>
        </div>
        <div className="text-center">
          <div className="text-3xl mb-2">💰</div>
          <h3 className="font-semibold mb-1">100% Free</h3>
          <p className="text-sm text-gray-600">All free tier providers</p>
        </div>
        <div className="text-center">
          <div className="text-3xl mb-2">🔧</div>
          <h3 className="font-semibold mb-1">Zero Config</h3>
          <p className="text-sm text-gray-600">Auto-detect everything</p>
        </div>
      </div>
    </div>
  );
}
