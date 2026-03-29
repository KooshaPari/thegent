'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ProviderBadge } from '@/components/provider-badge';
import { connectProvider } from '@/lib/api';
import type { ProviderName, ProviderConfig } from '@/lib/types';
import { CheckCircle2, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';

interface ProviderConnectDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
  initialProvider?: ProviderName;
}

const PROVIDERS: ProviderName[] = ['vercel', 'netlify', 'render', 'railway', 'fly', 'aws', 'gcp', 'azure'];

const PROVIDER_FIELDS: Record<ProviderName, { label: string; fields: Array<{ name: string; label: string; placeholder: string; type?: string }> }> = {
  vercel: {
    label: 'Vercel',
    fields: [
      { name: 'api_token', label: 'API Token', placeholder: 'Enter your Vercel API token', type: 'password' },
      { name: 'team_id', label: 'Team ID (optional)', placeholder: 'team_xxxxxxxxxxxxx' }
    ]
  },
  netlify: {
    label: 'Netlify',
    fields: [
      { name: 'access_token', label: 'Personal Access Token', placeholder: 'Enter your Netlify token', type: 'password' }
    ]
  },
  render: {
    label: 'Render',
    fields: [
      { name: 'api_key', label: 'API Key', placeholder: 'Enter your Render API key', type: 'password' }
    ]
  },
  railway: {
    label: 'Railway',
    fields: [
      { name: 'api_token', label: 'API Token', placeholder: 'Enter your Railway token', type: 'password' },
      { name: 'project_id', label: 'Project ID (optional)', placeholder: 'project_xxxxxxxxxxxxx' }
    ]
  },
  fly: {
    label: 'Fly.io',
    fields: [
      { name: 'api_token', label: 'API Token', placeholder: 'Enter your Fly.io token', type: 'password' },
      { name: 'organization_id', label: 'Organization ID (optional)', placeholder: 'org_xxxxxxxxxxxxx' }
    ]
  },
  aws: {
    label: 'AWS',
    fields: [
      { name: 'access_key_id', label: 'Access Key ID', placeholder: 'AKIA...' },
      { name: 'secret_access_key', label: 'Secret Access Key', placeholder: 'Enter secret key', type: 'password' },
      { name: 'region', label: 'Default Region', placeholder: 'us-east-1' }
    ]
  },
  gcp: {
    label: 'Google Cloud Platform',
    fields: [
      { name: 'project_id', label: 'Project ID', placeholder: 'my-project-12345' },
      { name: 'service_account_key', label: 'Service Account Key (JSON)', placeholder: 'Paste JSON key', type: 'password' }
    ]
  },
  azure: {
    label: 'Microsoft Azure',
    fields: [
      { name: 'subscription_id', label: 'Subscription ID', placeholder: 'Enter subscription ID' },
      { name: 'tenant_id', label: 'Tenant ID', placeholder: 'Enter tenant ID' },
      { name: 'client_id', label: 'Client ID', placeholder: 'Enter client ID' },
      { name: 'client_secret', label: 'Client Secret', placeholder: 'Enter client secret', type: 'password' }
    ]
  },
  supabase: {
    label: 'Supabase',
    fields: [
      { name: 'access_token', label: 'Access Token', placeholder: 'Enter your Supabase access token', type: 'password' }
    ]
  }
};

export function ProviderConnectDialog({
  open,
  onOpenChange,
  onSuccess,
  initialProvider
}: ProviderConnectDialogProps) {
  const [step, setStep] = useState<'select' | 'configure'>('select');
  const [selectedProvider, setSelectedProvider] = useState<ProviderName | null>(initialProvider || null);
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleProviderSelect = (provider: ProviderName) => {
    setSelectedProvider(provider);
    setStep('configure');
    setFormData({});
    setError(null);
  };

  const handleBack = () => {
    setStep('select');
    setSelectedProvider(null);
    setFormData({});
    setError(null);
  };

  const handleInputChange = (name: string, value: string) => {
    setFormData(prev => ({ ...prev, [name]: value }));
    setError(null);
  };

  const handleConnect = async () => {
    if (!selectedProvider) return;

    try {
      setConnecting(true);
      setError(null);

      const credentials: Record<string, any> = {};
      Object.entries(formData).forEach(([key, value]) => {
        if (value) {
          credentials[key] = value;
        }
      });

      const config: ProviderConfig = {
        name: selectedProvider,
        credentials
      };

      await connectProvider(config);
      toast.success(`Successfully connected to ${PROVIDER_FIELDS[selectedProvider].label}`);

      onOpenChange(false);
      setStep('select');
      setSelectedProvider(null);
      setFormData({});

      if (onSuccess) {
        onSuccess();
      }
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to connect provider';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setConnecting(false);
    }
  };

  const providerConfig = selectedProvider ? PROVIDER_FIELDS[selectedProvider] : null;
  const isFormValid = providerConfig?.fields.filter(f => !f.label.includes('optional')).every(
    field => formData[field.name]?.trim()
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {step === 'select' ? 'Connect Provider' : `Connect to ${providerConfig?.label}`}
          </DialogTitle>
          <DialogDescription>
            {step === 'select'
              ? 'Choose a cloud provider to connect to your account'
              : 'Enter your credentials to connect this provider'}
          </DialogDescription>
        </DialogHeader>

        {step === 'select' && (
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-3">
              {PROVIDERS.map((provider) => (
                <button
                  key={provider}
                  onClick={() => handleProviderSelect(provider)}
                  className="flex items-center justify-center p-4 border rounded-lg hover:border-primary hover:bg-accent transition-colors"
                >
                  <ProviderBadge provider={provider} size="lg" />
                </button>
              ))}
            </div>
          </div>
        )}

        {step === 'configure' && providerConfig && (
          <div className="space-y-4 py-4">
            {error && (
              <div className="flex items-start gap-2 p-3 border border-destructive bg-destructive/10 rounded-lg">
                <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-destructive">Connection Failed</p>
                  <p className="text-sm text-destructive/80 mt-1">{error}</p>
                </div>
              </div>
            )}

            <div className="flex items-center justify-center py-2">
            {selectedProvider ? (
              <ProviderBadge provider={selectedProvider} size="lg" />
            ) : null}
            </div>

            <div className="space-y-4">
              {providerConfig.fields.map((field) => (
                <div key={field.name} className="space-y-2">
                  <Label htmlFor={field.name}>{field.label}</Label>
                  <Input
                    id={field.name}
                    type={field.type || 'text'}
                    placeholder={field.placeholder}
                    value={formData[field.name] || ''}
                    onChange={(e) => handleInputChange(field.name, e.target.value)}
                    disabled={connecting}
                  />
                </div>
              ))}
            </div>

            <div className="flex items-start gap-2 p-3 border bg-muted/50 rounded-lg">
              <AlertCircle className="h-4 w-4 text-muted-foreground flex-shrink-0 mt-0.5" />
              <p className="text-xs text-muted-foreground">
                Your credentials are encrypted and stored securely. They are only used to manage
                deployments on your behalf.
              </p>
            </div>

            <div className="flex gap-2 pt-4">
              <Button
                variant="outline"
                onClick={handleBack}
                disabled={connecting}
                className="flex-1"
              >
                Back
              </Button>
              <Button
                onClick={handleConnect}
                disabled={!isFormValid || connecting}
                className="flex-1"
              >
                {connecting ? (
                  'Connecting...'
                ) : (
                  <>
                    <CheckCircle2 className="h-4 w-4 mr-2" />
                    Connect
                  </>
                )}
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
