'use client';

import { useState } from 'react';
import { Section } from '@/components/section';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { ProviderCredentialsForm } from '@/components/provider-credentials-form';
import type { ProviderConfiguration } from '@/components/provider-credentials-form';
import { Info, Server, Database, Globe, Triangle, Wifi, Train, Plane, Layers } from 'lucide-react';

// Provider icons
const AwsIcon = () => (
  <svg className="h-6 w-6" viewBox="0 0 24 24" fill="currentColor">
    <path d="M6.763 10.036c0 .296.032.535.088.71.064.176.144.368.256.576.04.063.056.127.056.183 0 .08-.048.16-.152.24l-.503.335c-.072.048-.144.072-.208.072-.08 0-.16-.04-.239-.112a2.417 2.417 0 0 1-.287-.375 6.18 6.18 0 0 1-.248-.471c-.622.734-1.405 1.101-2.347 1.101-.67 0-1.205-.191-1.596-.574-.391-.384-.59-.894-.59-1.533 0-.678.239-1.23.726-1.644.487-.415 1.133-.623 1.955-.623.272 0 .551.024.846.064.296.04.6.104.918.176V6.759c0-.623-.13-1.062-.383-1.31-.264-.248-.71-.374-1.342-.374-.288 0-.583.032-.886.104-.303.07-.583.16-.862.264-.128.048-.224.08-.272.096-.048.016-.08.024-.104.024-.096 0-.144-.072-.144-.216v-.336c0-.112.016-.2.056-.256a.614.614 0 0 1 .224-.16 4.844 4.844 0 0 1 .97-.368 4.692 4.692 0 0 1 1.199-.152c.91 0 1.579.207 2.005.615.423.408.632 1.038.632 1.887v2.478zm-3.24 1.214c.263 0 .535-.048.822-.144.287-.096.543-.271.758-.51.128-.152.224-.32.272-.512.048-.191.08-.423.08-.694V9.665a7.107 7.107 0 0 0-.734-.136 6.351 6.351 0 0 0-.75-.048c-.535 0-.926.104-1.19.32-.263.215-.39.518-.39.917 0 .375.095.655.295.846.191.2.47.295.838.295zm6.41.862c-.12 0-.2-.024-.256-.064-.056-.048-.104-.144-.152-.271L7.869 5.739c-.048-.16-.072-.263-.072-.32 0-.127.064-.2.191-.2h.783c.128 0 .215.025.264.065.056.047.104.143.151.27l1.735 6.826 1.615-6.826c.04-.16.088-.24.144-.271a.754.754 0 0 1 .271-.064h.638c.128 0 .216.025.272.065.056.047.104.143.144.27l1.635 6.922 1.783-6.922c.048-.16.104-.24.152-.271a.716.716 0 0 1 .263-.064h.742c.128 0 .2.063.2.2 0 .055-.008.111-.024.175-.016.063-.048.159-.104.271l-2.471 6.04c-.048.16-.096.256-.152.272-.056.047-.136.063-.256.063h-.687c-.128 0-.216-.023-.272-.063-.056-.048-.104-.144-.144-.272l-1.596-6.634-1.588 6.634c-.04.16-.087.24-.143.272-.056.047-.144.063-.272.063zm10.376.215c-.415 0-.83-.048-1.229-.143-.399-.096-.71-.2-.918-.32-.128-.071-.215-.151-.247-.223a.563.563 0 0 1-.048-.224v-.336c0-.144.056-.216.16-.216.064 0 .128.016.2.04.071.023.175.063.295.111.375.144.774.24 1.189.24.631 0 1.117-.112 1.476-.343.36-.232.543-.558.543-.99 0-.295-.096-.543-.287-.742-.192-.2-.559-.384-1.097-.56L18.1 8.1c-.783-.239-1.36-.59-1.707-1.046-.346-.455-.518-.958-.518-1.501 0-.431.096-.814.287-1.15.192-.335.455-.622.79-.862.336-.239.734-.415 1.198-.534a5.13 5.13 0 0 1 1.517-.224c.176 0 .359.008.543.032.192.024.367.056.535.088.16.04.312.08.455.127.144.048.256.096.336.144a.69.69 0 0 1 .255.215c.048.08.072.168.072.264v.304c0 .144-.056.223-.168.223-.064 0-.168-.032-.32-.095-.479-.224-1.021-.336-1.628-.336-.575 0-1.021.104-1.34.319-.319.215-.479.535-.479.966 0 .295.104.551.32.758.215.208.607.416 1.165.615l1.309.407c.767.24 1.324.575 1.66 1.006.337.431.506.926.506 1.485 0 .439-.096.838-.288 1.189-.191.352-.455.655-.798.91-.336.256-.742.447-1.229.583a5.184 5.184 0 0 1-1.533.216z" />
  </svg>
);

const GcpIcon = () => (
  <svg className="h-6 w-6" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12.19 2.38a9.344 9.344 0 0 0-9.234 6.893c.053-.02-.11.096-.151.167-.012.021-.02.045-.029.067a9.344 9.344 0 0 0 .124 6.506l.03.068c.035.077.068.156.105.233l.088.183.066.134a9.344 9.344 0 0 0 4.475 4.475l.068.03c.076.035.155.068.232.105l.184.088.134.066a9.344 9.344 0 0 0 6.506.124l.068-.03c.077-.035.156-.068.233-.105l.183-.088.134-.066a9.344 9.344 0 0 0 4.475-4.475l.03-.068c.035-.076.068-.155.105-.232.03-.062.059-.123.088-.184.022-.044.044-.088.066-.134a9.344 9.344 0 0 0 .124-6.506l-.03-.068c-.035-.077-.068-.156-.105-.233l-.088-.183-.066-.134a9.344 9.344 0 0 0-4.475-4.475l-.068-.03c-.076-.035-.155-.068-.232-.105l-.184-.088-.134-.066A9.344 9.344 0 0 0 12.19 2.38zM8.43 9.66h1.832v5.148h3.103v1.555H8.43V9.66zm5.29 0h1.832v6.703h-1.832V9.66z" />
  </svg>
);

const AzureIcon = () => (
  <svg className="h-6 w-6" viewBox="0 0 24 24" fill="currentColor">
    <path d="M22.379 23.343a1.62 1.62 0 0 0 1.536-2.14v.002L17.35 1.76A1.62 1.62 0 0 0 15.816.657H8.184A1.62 1.62 0 0 0 6.65 1.76L.086 21.204a1.62 1.62 0 0 0 1.536 2.139h4.741a1.62 1.62 0 0 0 1.535-1.103l.977-2.892 4.947 3.675c.28.208.617.32.966.32h7.591Z" />
  </svg>
);

const DigitalOceanIcon = () => <Server className="h-6 w-6 text-blue-500" />;
const LinodeIcon = () => <Database className="h-6 w-6 text-green-600" />;
const VultrIcon = () => <Globe className="h-6 w-6 text-blue-600" />;
const VercelIcon = () => <Triangle className="h-6 w-6 text-white fill-white" />;
const NetlifyIcon = () => <Wifi className="h-6 w-6 text-teal-400" />;
const RailwayIcon = () => <Train className="h-6 w-6 text-violet-400" />;
const FlyIoIcon = () => <Plane className="h-6 w-6 text-purple-500" />;
const SupabaseIcon = () => <Layers className="h-6 w-6 text-emerald-400" />;

// Mock provider configurations
const providerConfigurations: ProviderConfiguration[] = [
  {
    provider: 'aws',
    icon: <AwsIcon />,
    name: 'Amazon Web Services',
    description: 'Deploy to AWS using your credentials',
    configured: true,
    lastVerified: '2024-03-01T10:00:00Z',
    fields: [
      {
        name: 'accessKeyId',
        label: 'Access Key ID',
        type: 'text' as const,
        placeholder: 'AKIAIOSFODNN7EXAMPLE',
        required: true,
        helpText: 'Your AWS access key ID',
      },
      {
        name: 'secretAccessKey',
        label: 'Secret Access Key',
        type: 'password' as const,
        placeholder: 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
        required: true,
        helpText: 'Your AWS secret access key',
      },
      {
        name: 'region',
        label: 'Default Region',
        type: 'text' as const,
        placeholder: 'us-east-1',
        required: true,
        helpText: 'Default AWS region for deployments',
      },
    ],
  },
  {
    provider: 'gcp',
    icon: <GcpIcon />,
    name: 'Google Cloud Platform',
    description: 'Deploy to GCP using service account credentials',
    configured: false,
    fields: [
      {
        name: 'projectId',
        label: 'Project ID',
        type: 'text' as const,
        placeholder: 'my-project-123456',
        required: true,
        helpText: 'Your GCP project ID',
      },
      {
        name: 'serviceAccountKey',
        label: 'Service Account Key (JSON)',
        type: 'textarea' as const,
        placeholder: '{\n  "type": "service_account",\n  "project_id": "...",\n  ...\n}',
        required: true,
        helpText: 'Paste the full service account JSON key file contents',
      },
    ],
  },
  {
    provider: 'azure',
    icon: <AzureIcon />,
    name: 'Microsoft Azure',
    description: 'Deploy to Azure using your credentials',
    configured: false,
    fields: [
      {
        name: 'subscriptionId',
        label: 'Subscription ID',
        type: 'text' as const,
        placeholder: '00000000-0000-0000-0000-000000000000',
        required: true,
        helpText: 'Your Azure subscription ID',
      },
      {
        name: 'tenantId',
        label: 'Tenant ID',
        type: 'text' as const,
        placeholder: '00000000-0000-0000-0000-000000000000',
        required: true,
        helpText: 'Your Azure Active Directory tenant ID',
      },
      {
        name: 'clientId',
        label: 'Client ID',
        type: 'text' as const,
        placeholder: '00000000-0000-0000-0000-000000000000',
        required: true,
        helpText: 'Your application (client) ID',
      },
      {
        name: 'clientSecret',
        label: 'Client Secret',
        type: 'password' as const,
        placeholder: 'Your client secret',
        required: true,
        helpText: 'Your application client secret',
      },
    ],
  },
  {
    provider: 'digitalocean',
    icon: <DigitalOceanIcon />,
    name: 'DigitalOcean',
    description: 'Deploy to DigitalOcean using your API token',
    configured: false,
    fields: [
      {
        name: 'apiToken',
        label: 'API Token',
        type: 'password' as const,
        placeholder: 'dop_v1_...',
        required: true,
        helpText: 'Your DigitalOcean API token',
      },
    ],
  },
  {
    provider: 'linode',
    icon: <LinodeIcon />,
    name: 'Linode',
    description: 'Deploy to Linode using your API token',
    configured: false,
    fields: [
      {
        name: 'apiToken',
        label: 'API Token',
        type: 'password' as const,
        placeholder: 'Your Linode API token',
        required: true,
        helpText: 'Your Linode personal access token',
      },
    ],
  },
  {
    provider: 'vultr',
    icon: <VultrIcon />,
    name: 'Vultr',
    description: 'Deploy to Vultr using your API key',
    configured: false,
    fields: [
      {
        name: 'apiKey',
        label: 'API Key',
        type: 'password' as const,
        placeholder: 'Your Vultr API key',
        required: true,
        helpText: 'Your Vultr API key',
      },
    ],
  },
  {
    provider: 'vercel',
    icon: <VercelIcon />,
    name: 'Vercel',
    description: 'Deploy to Vercel using your personal access token',
    configured: false,
    fields: [
      {
        name: 'token',
        label: 'API Token',
        type: 'password' as const,
        placeholder: 'Your Vercel personal access token',
        required: true,
        helpText: 'Create a token at vercel.com/account/tokens',
      },
    ],
  },
  {
    provider: 'netlify',
    icon: <NetlifyIcon />,
    name: 'Netlify',
    description: 'Deploy to Netlify using your personal access token',
    configured: false,
    fields: [
      {
        name: 'token',
        label: 'API Token',
        type: 'password' as const,
        placeholder: 'Your Netlify personal access token',
        required: true,
        helpText: 'Create a token at app.netlify.com/user/applications/personal',
      },
    ],
  },
  {
    provider: 'railway',
    icon: <RailwayIcon />,
    name: 'Railway',
    description: 'Deploy to Railway using your API token',
    configured: false,
    fields: [
      {
        name: 'token',
        label: 'API Token',
        type: 'password' as const,
        placeholder: 'Your Railway API token',
        required: true,
        helpText: 'Generate a token at railway.app/account/tokens',
      },
    ],
  },
  {
    provider: 'fly',
    icon: <FlyIoIcon />,
    name: 'Fly.io',
    description: 'Deploy to Fly.io using your API token',
    configured: false,
    fields: [
      {
        name: 'token',
        label: 'API Token',
        type: 'password' as const,
        placeholder: 'Your Fly.io API token',
        required: true,
        helpText: 'Generate a token with: flyctl auth token',
      },
    ],
  },
  {
    provider: 'supabase',
    icon: <SupabaseIcon />,
    name: 'Supabase',
    description: 'Connect to Supabase using your access token',
    configured: false,
    fields: [
      {
        name: 'token',
        label: 'Access Token',
        type: 'password' as const,
        placeholder: 'Your Supabase access token',
        required: true,
        helpText: 'Generate a token at supabase.com/dashboard/account/tokens',
      },
    ],
  },
];

export default function ProvidersPage() {
  const [providers, setProviders] = useState(providerConfigurations);

  const handleSave = async (provider: string, _values: Record<string, string>) => {
    // TODO: Implement API call to save credentials
    await new Promise((resolve) => setTimeout(resolve, 1000));

    setProviders((prev) =>
      prev.map((p) =>
        p.provider === provider
          ? { ...p, configured: true, lastVerified: new Date().toISOString() }
          : p
      )
    );
  };

  const handleTest = async (_provider: string, _values: Record<string, string>) => {
    // TODO: Implement API call to test credentials
    await new Promise((resolve) => setTimeout(resolve, 1500));
    return Math.random() > 0.2; // 80% success rate for demo
  };

  const handleRemove = async (provider: string) => {
    // TODO: Implement API call to remove credentials
    await new Promise((resolve) => setTimeout(resolve, 1000));

    setProviders((prev) =>
      prev.map((p) => (p.provider === provider ? { ...p, configured: false, lastVerified: undefined } : p))
    );
  };

  return (
    <div className="space-y-6">
      <Section>
        <Alert>
          <Info className="h-4 w-4" />
          <AlertTitle>Cloud Provider Credentials</AlertTitle>
          <AlertDescription>
            Configure your cloud provider credentials to enable deployments. All credentials are
            encrypted at rest and in transit. We recommend using dedicated service accounts with
            minimal required permissions.
          </AlertDescription>
        </Alert>
      </Section>

      <Section>
        <div className="space-y-4">
          {providers.map((credential) => (
            <ProviderCredentialsForm
              key={credential.provider}
              credential={credential}
              onSave={handleSave}
              onTest={handleTest}
              onRemove={handleRemove}
            />
          ))}
        </div>
      </Section>
    </div>
  );
}
