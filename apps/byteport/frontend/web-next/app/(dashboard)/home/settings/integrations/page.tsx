'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { fetchUserCredentials, updateUserCredentials } from '@/lib/api';
import type { UserCredentials } from '@/lib/types';
import { useAuth } from '@/context/auth-context';
import { DashboardHeader } from '@/components/layout/Header';

const PROVIDERS = [
  // Ollama is the default — free, local, no API key required.
  // Run: ollama pull llama3.2 && ollama serve
  { label: 'Ollama (local — default)', value: 'ollama' },
  { label: 'OpenAI', value: 'openai' },
  { label: 'Anthropic', value: 'anthropic' },
  { label: 'Gemini', value: 'gemini' },
  { label: 'DeepSeek', value: 'deepseek' }
];

const MODELS: Record<string, { label: string; value: string }[]> = {
  // Ollama models — pulled locally via `ollama pull <model>`
  ollama: [
    { label: 'Llama 3.2 (3B — recommended)', value: 'llama3.2' },
    { label: 'Llama 3.2 (1B — fastest)', value: 'llama3.2:1b' },
    { label: 'Llama 3.3 (70B)', value: 'llama3.3' },
    { label: 'Mistral 7B', value: 'mistral' },
    { label: 'Phi-4', value: 'phi4' },
    { label: 'Gemma 3 (4B)', value: 'gemma3:4b' },
    { label: 'DeepSeek-R1 (8B)', value: 'deepseek-r1:8b' },
    { label: 'Qwen 2.5 Coder (7B)', value: 'qwen2.5-coder:7b' }
  ],
  openai: [
    { label: 'GPT-4o', value: 'gpt-4o' },
    { label: 'GPT-4o Mini', value: 'gpt-4o-mini' },
    { label: 'GPT-o1', value: 'gpt-o1' },
    { label: 'GPT-o1 Mini', value: 'gpt-o1-mini' }
  ],
  anthropic: [
    { label: 'Claude 3.5 Sonnet', value: '3.5-sonnet' },
    { label: 'Claude 3.5 Haiku', value: '3.5-haiku' }
  ],
  gemini: [
    { label: 'Gemini 2.0 Flash', value: 'gemini-2.0-flash' },
    { label: 'Gemini 1.5 Pro', value: 'gemini-1.5-pro' }
  ],
  deepseek: [
    { label: 'DeepSeek V3', value: 'deepseek-v3' }
  ]
};

type SaveState = 'idle' | 'saving' | 'saved' | 'error';

enum LoadingState {
  Idle,
  Fetching
}

export default function IntegrationsPage() {
  const { status, user, refresh } = useAuth();
  const router = useRouter();
  const [credentials, setCredentials] = useState<UserCredentials | null>(null);
  const [loading, setLoading] = useState<LoadingState>(LoadingState.Fetching);
  const [saveState, setSaveState] = useState<SaveState>('idle');
  const [message, setMessage] = useState('');
  const [selectedProvider, setSelectedProvider] = useState('ollama');
  const [selectedModel, setSelectedModel] = useState('llama3.2');

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.replace('/login');
    }
  }, [router, status]);

  useEffect(() => {
    if (status !== 'authenticated' || !user) {
      return;
    }

    let cancelled = false;
    const currentUser = user;
    setLoading(LoadingState.Fetching);

    async function load() {
      try {
        if (!currentUser) {
          return;
        }
        const data = await fetchUserCredentials(currentUser.uuid);
        if (cancelled) return;
        setCredentials(data);
        setSelectedProvider(data.llmConfig.provider ?? 'ollama');
        const defaultModel = data.llmConfig.providers[data.llmConfig.provider ?? 'ollama']?.modal;
        setSelectedModel(defaultModel ?? MODELS[data.llmConfig.provider ?? 'ollama']?.[0]?.value ?? 'llama3.2');
        setMessage('');
      } catch (err) {
        console.error('Failed to load credentials', err);
        if (!cancelled) {
          setMessage('Unable to load integration settings.');
        }
      } finally {
        if (!cancelled) {
          setLoading(LoadingState.Idle);
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, [status, user]);

  const provider = selectedProvider;
  const availableModels = useMemo(() => MODELS[provider] ?? [], [provider]);

  if (status === 'pending') {
    return (
      <div className="flex flex-1 items-center justify-center bg-dark-surface">
        <p className="text-dark-onSurfaceVariant">Loading integration settings…</p>
      </div>
    );
  }

  if (status === 'unauthenticated' || !user) {
    return null;
  }

  if (loading === LoadingState.Fetching) {
    return (
      <div className="flex flex-1 items-center justify-center bg-dark-surface">
        <p className="text-dark-onSurfaceVariant">Loading integration settings…</p>
      </div>
    );
  }

  if (!credentials) {
    return (
      <div className="flex flex-1 items-center justify-center bg-dark-surface">
        <p className="text-sm text-dark-onSurfaceVariant">{message || 'No credentials configured yet.'}</p>
      </div>
    );
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!user) {
      setSaveState('error');
      setMessage('No authenticated user – refresh and try again.');
      return;
    }

    setSaveState('saving');
    setMessage('');

    const formData = new FormData(event.currentTarget);

    const payload = {
      UUID: user.uuid,
      Name: user.name,
      Email: user.email,
      AwsCreds: {
        accessKeyId: formData.get('awsAccessKeyId')?.toString() ?? '',
        secretAccessKey: formData.get('awsSecretAccessKey')?.toString() ?? ''
      },
      LLMConfig: {
        provider: formData.get('llmProvider')?.toString() ?? 'ollama',
        providers: {
          [formData.get('llmProvider')?.toString() ?? selectedProvider]: {
            modal: formData.get('llmModel')?.toString() ?? selectedModel,
            // apiKey is empty for Ollama (no key required); set for cloud providers
            apiKey: formData.get('llmApiKey')?.toString() ?? '',
            // baseURL used by Ollama — defaults to http://localhost:11434 on the backend
            baseUrl: formData.get('llmBaseUrl')?.toString() ?? ''
          }
        }
      },
      Portfolio: {
        rootEndpoint: formData.get('portfolioEndpoint')?.toString() ?? '',
        apiKey: formData.get('portfolioApiKey')?.toString() ?? ''
      }
    };

    try {
      await updateUserCredentials(payload);
      await refresh();
      setSaveState('saved');
      setMessage('Integrations updated successfully.');
    } catch (err) {
      console.error('Failed to update integrations', err);
      setSaveState('error');
      setMessage('Failed to validate and save the provided credentials.');
    }
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <DashboardHeader
        title="Integrations"
        subtitle="Manage cloud credentials, LLM providers, and portfolio endpoints"
      />
      <section className="flex-1 overflow-y-auto px-6 py-8">
        <form onSubmit={handleSubmit} className="grid gap-8 lg:grid-cols-2">
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-dark-onSurface">AWS</h2>
            <p className="text-sm text-dark-onSurfaceVariant">
              Provide an IAM user or role with permissions to provision EC2, IAM, ECR, S3, and networking resources. The
              credentials are encrypted locally before being stored.
            </p>
            <label className="block text-sm text-dark-onSurface">
              Access key ID
              <input
                name="awsAccessKeyId"
                defaultValue={credentials.awsCreds.accessKeyId}
                className="mt-2 w-full rounded-md border border-dark-surfaceVariant bg-dark-surfaceContainerHigh px-4 py-3 text-dark-onSurface focus:border-dark-primary focus:outline-none"
              />
            </label>
            <label className="block text-sm text-dark-onSurface">
              Secret access key
              <input
                name="awsSecretAccessKey"
                defaultValue={credentials.awsCreds.secretAccessKey}
                className="mt-2 w-full rounded-md border border-dark-surfaceVariant bg-dark-surfaceContainerHigh px-4 py-3 text-dark-onSurface focus:border-dark-primary focus:outline-none"
              />
            </label>
          </div>

          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-dark-onSurface">LLM provider</h2>
            <p className="text-sm text-dark-onSurfaceVariant">
              Byteport uses this provider to render deployment summaries, README updates, and interactive demos.
              The default is <span className="font-mono text-dark-primary">Ollama</span> — free, local, no API key
              required. Run <span className="font-mono">ollama pull llama3.2</span> to get started.
            </p>
            <label className="block text-sm text-dark-onSurface">
              Provider
              <select
                name="llmProvider"
                value={provider}
                onChange={(event) => {
                  const next = event.target.value;
                  setSelectedProvider(next);
                  const fallback = MODELS[next]?.[0]?.value ?? '';
                  setSelectedModel(MODELS[next]?.[0]?.value ?? fallback);
                }}
                className="mt-2 w-full rounded-md border border-dark-surfaceVariant bg-dark-surfaceContainerHigh px-4 py-3 text-dark-onSurface focus:border-dark-primary focus:outline-none"
              >
                {PROVIDERS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
            <label className="block text-sm text-dark-onSurface">
              Model
              <select
                name="llmModel"
                value={selectedModel}
                onChange={(event) => setSelectedModel(event.target.value)}
                className="mt-2 w-full rounded-md border border-dark-surfaceVariant bg-dark-surfaceContainerHigh px-4 py-3 text-dark-onSurface focus:border-dark-primary focus:outline-none"
              >
                {availableModels.map((model) => (
                  <option key={model.value} value={model.value}>
                    {model.label}
                  </option>
                ))}
              </select>
            </label>
            {provider === 'ollama' && (
              <label className="block text-sm text-dark-onSurface">
                Ollama base URL
                <input
                  name="llmBaseUrl"
                  defaultValue={credentials.llmConfig.providers[provider]?.baseUrl ?? 'http://localhost:11434'}
                  placeholder="http://localhost:11434"
                  className="mt-2 w-full rounded-md border border-dark-surfaceVariant bg-dark-surfaceContainerHigh px-4 py-3 font-mono text-sm text-dark-onSurface focus:border-dark-primary focus:outline-none"
                />
                <span className="mt-1 block text-xs text-dark-onSurfaceVariant">
                  Keep default unless Ollama runs on a different host or port.
                </span>
              </label>
            )}
            {provider !== 'ollama' && (
              <label className="block text-sm text-dark-onSurface">
                API key
                <input
                  name="llmApiKey"
                  type="password"
                  defaultValue={credentials.llmConfig.providers[provider]?.apiKey ?? ''}
                  className="mt-2 w-full rounded-md border border-dark-surfaceVariant bg-dark-surfaceContainerHigh px-4 py-3 text-dark-onSurface focus:border-dark-primary focus:outline-none"
                />
              </label>
            )}
          </div>

          <div className="space-y-4 lg:col-span-2">
            <h2 className="text-lg font-semibold text-dark-onSurface">Portfolio target</h2>
            <p className="text-sm text-dark-onSurfaceVariant">
              Configure the Byteport portfolio endpoint used to publish generated demos and documentation snippets.
            </p>
            <label className="block text-sm text-dark-onSurface">
              Root endpoint
              <input
                name="portfolioEndpoint"
                defaultValue={credentials.portfolio.rootEndpoint}
                className="mt-2 w-full rounded-md border border-dark-surfaceVariant bg-dark-surfaceContainerHigh px-4 py-3 text-dark-onSurface focus:border-dark-primary focus:outline-none"
              />
            </label>
            <label className="block text-sm text-dark-onSurface">
              API key
              <input
                name="portfolioApiKey"
                defaultValue={credentials.portfolio.apiKey}
                className="mt-2 w-full rounded-md border border-dark-surfaceVariant bg-dark-surfaceContainerHigh px-4 py-3 text-dark-onSurface focus:border-dark-primary focus:outline-none"
              />
            </label>
          </div>

          <div className="lg:col-span-2">
            {message ? (
              <p
                className={
                  saveState === 'error'
                    ? 'text-sm text-red-400'
                    : saveState === 'saved'
                    ? 'text-sm text-dark-primary'
                    : 'text-sm text-dark-onSurfaceVariant'
                }
              >
                {message}
              </p>
            ) : null}
            <button
              type="submit"
              disabled={saveState === 'saving'}
              className="mt-4 rounded-lg bg-dark-primary px-4 py-2 text-sm font-medium text-dark-onSurface shadow hover:bg-dark-primary/90 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {saveState === 'saving' ? 'Validating…' : 'Save integrations'}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
