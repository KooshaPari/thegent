'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { ProviderBadge } from '@/components/provider-badge';
import { getProviders, registerHost } from '@/lib/api';
import type { Provider, ProviderName, HostConfig } from '@/lib/types';
import {
  CheckCircle2,
  ChevronRight,
  ChevronLeft,
  Server,
  Settings,
  Shield,
  AlertCircle,
  Plus,
  X
} from 'lucide-react';
import toast from 'react-hot-toast';

interface HostSetupWizardProps {
  onSuccess?: (hostId: string) => void;
  onCancel?: () => void;
  onRegisteringChange?: (isRegistering: boolean) => void;
}

const REGIONS_BY_PROVIDER: Record<ProviderName, string[]> = {
  vercel: ['iad1', 'sfo1', 'cdg1', 'hnd1', 'gru1'],
  netlify: ['us-east-1', 'us-west-1', 'eu-west-1', 'ap-southeast-1'],
  render: ['oregon', 'frankfurt', 'singapore'],
  railway: ['us-west', 'us-east', 'eu-west'],
  fly: ['iad', 'lax', 'ams', 'sin', 'syd'],
  aws: ['us-east-1', 'us-west-2', 'eu-west-1', 'eu-central-1', 'ap-southeast-1', 'ap-northeast-1'],
  gcp: ['us-central1', 'us-east1', 'europe-west1', 'asia-southeast1', 'australia-southeast1'],
  azure: ['eastus', 'westus2', 'northeurope', 'southeastasia', 'australiaeast'],
  supabase: ['us-east-1', 'us-west-1', 'eu-west-1', 'ap-southeast-1']
};

type WizardStep = 'provider' | 'details' | 'credentials' | 'review';

export function HostSetupWizard({ onSuccess, onCancel, onRegisteringChange }: HostSetupWizardProps) {
  const [currentStep, setCurrentStep] = useState<WizardStep>('provider');
  const [providers, setProviders] = useState<Provider[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<ProviderName | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    hostname: '',
    region: '',
    ssh_key: '',
    tags: [] as string[],
    tagInput: ''
  });
  const [registering, setRegistering] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProviders();
  }, []);

  useEffect(() => {
    onRegisteringChange?.(registering);
  }, [registering, onRegisteringChange]);

  const loadProviders = async () => {
    try {
      const data = await getProviders();
      setProviders(data.filter(p => p.status === 'connected'));
    } catch (error) {
      console.error('Failed to load providers:', error);
      toast.error('Failed to load providers');
    }
  };

  const handleProviderSelect = (provider: ProviderName) => {
    setSelectedProvider(provider);
    setFormData(prev => ({ ...prev, region: '' }));
    setError(null);
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(null);
  };

  const handleAddTag = () => {
    const tag = formData.tagInput.trim();
    if (tag && !formData.tags.includes(tag)) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tag],
        tagInput: ''
      }));
    }
  };

  const handleRemoveTag = (tag: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(t => t !== tag)
    }));
  };

  const handleNext = () => {
    const steps: WizardStep[] = ['provider', 'details', 'credentials', 'review'];
    const currentIndex = steps.indexOf(currentStep);
    if (currentIndex < steps.length - 1) {
      setCurrentStep(steps[currentIndex + 1]);
    }
  };

  const handleBack = () => {
    const steps: WizardStep[] = ['provider', 'details', 'credentials', 'review'];
    const currentIndex = steps.indexOf(currentStep);
    if (currentIndex > 0) {
      setCurrentStep(steps[currentIndex - 1]);
    }
  };

  const handleRegister = async () => {
    if (!selectedProvider) return;

    try {
      setRegistering(true);
      setError(null);

      const config: HostConfig = {
        name: formData.name,
        hostname: formData.hostname,
        provider: selectedProvider,
        region: formData.region,
        tags: formData.tags.length > 0 ? formData.tags : undefined,
        ssh_key: formData.ssh_key || undefined
      };

      const host = await registerHost(config);
      toast.success('Host registered successfully');

      if (onSuccess) {
        onSuccess(host.id);
      }
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to register host';
      setError(errorMessage);
      toast.error(errorMessage);
      setRegistering(false);
    }
  };

  const canProceedFromProvider = selectedProvider !== null;
  const canProceedFromDetails = formData.name && formData.hostname && formData.region;
  const canRegister = canProceedFromProvider && canProceedFromDetails;

  const connectedProviders = providers.filter(p => p.status === 'connected');

  return (
    <div className="space-y-6">
      {/* Progress Steps */}
      <div className="flex items-center justify-between">
        {(['provider', 'details', 'credentials', 'review'] as WizardStep[]).map((step, index) => {
          const steps: WizardStep[] = ['provider', 'details', 'credentials', 'review'];
          const currentIndex = steps.indexOf(currentStep);
          const stepIndex = steps.indexOf(step);
          const isActive = step === currentStep;
          const isCompleted = stepIndex < currentIndex;

          return (
            <div key={step} className="flex items-center flex-1">
              <div className="flex items-center gap-2">
                <div
                  className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                    isActive
                      ? 'border-primary bg-primary text-primary-foreground'
                      : isCompleted
                      ? 'border-green-500 bg-green-500 text-white'
                      : 'border-muted-foreground text-muted-foreground'
                  }`}
                >
                  {isCompleted ? (
                    <CheckCircle2 className="h-4 w-4" />
                  ) : (
                    <span className="text-sm font-medium">{index + 1}</span>
                  )}
                </div>
                <span
                  className={`text-sm font-medium capitalize ${
                    isActive ? 'text-foreground' : 'text-muted-foreground'
                  }`}
                >
                  {step}
                </span>
              </div>
              {index < 3 && (
                <div className="flex-1 h-0.5 mx-2 bg-muted-foreground/20" />
              )}
            </div>
          );
        })}
      </div>

      {/* Error Display */}
      {error && (
        <div className="flex items-start gap-2 p-4 border border-destructive bg-destructive/10 rounded-lg">
          <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-medium text-destructive">Registration Failed</p>
            <p className="text-sm text-destructive/80 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Step Content */}
      {currentStep === 'provider' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Server className="h-5 w-5" />
              Select Provider
            </CardTitle>
            <CardDescription>
              Choose the cloud provider where you want to register your host
            </CardDescription>
          </CardHeader>
          <CardContent>
            {connectedProviders.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-sm text-muted-foreground mb-4">
                  No providers connected. Please connect a provider first.
                </p>
                <Button variant="outline" onClick={() => window.location.href = '/providers'}>
                  Go to Providers
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {connectedProviders.map((provider) => (
                  <button
                    key={provider.name}
                    onClick={() => handleProviderSelect(provider.name)}
                    className={`p-4 border-2 rounded-lg transition-all ${
                      selectedProvider === provider.name
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/50'
                    }`}
                  >
                    <ProviderBadge provider={provider.name} size="lg" />
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {currentStep === 'details' && selectedProvider && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Host Details
            </CardTitle>
            <CardDescription>
              Configure the basic details for your host
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Host Name *</Label>
              <Input
                id="name"
                placeholder="my-production-server"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="hostname">Hostname *</Label>
              <Input
                id="hostname"
                placeholder="server.example.com"
                value={formData.hostname}
                onChange={(e) => handleInputChange('hostname', e.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                The fully qualified domain name or IP address of your host
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="region">Region *</Label>
              <select
                id="region"
                value={formData.region}
                onChange={(e) => handleInputChange('region', e.target.value)}
                className="w-full h-10 px-3 py-2 text-sm border rounded-md bg-background"
              >
                <option value="">Select a region</option>
                {REGIONS_BY_PROVIDER[selectedProvider]?.map((region) => (
                  <option key={region} value={region}>
                    {region}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="tags">Tags (optional)</Label>
              <div className="flex gap-2">
                <Input
                  id="tags"
                  placeholder="production, web-server, etc."
                  value={formData.tagInput}
                  onChange={(e) => handleInputChange('tagInput', e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddTag();
                    }
                  }}
                />
                <Button type="button" variant="outline" onClick={handleAddTag}>
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              {formData.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {formData.tags.map((tag) => (
                    <Badge key={tag} variant="secondary" className="gap-1">
                      {tag}
                      <button
                        type="button"
                        onClick={() => handleRemoveTag(tag)}
                        className="ml-1 hover:text-destructive"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {currentStep === 'credentials' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Credentials (Optional)
            </CardTitle>
            <CardDescription>
              Provide SSH credentials for advanced host management
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="ssh_key">SSH Private Key</Label>
              <textarea
                id="ssh_key"
                placeholder="-----BEGIN RSA PRIVATE KEY-----&#10;...&#10;-----END RSA PRIVATE KEY-----"
                value={formData.ssh_key}
                onChange={(e) => handleInputChange('ssh_key', e.target.value)}
                className="w-full min-h-[200px] px-3 py-2 text-sm border rounded-md bg-background font-mono"
              />
              <p className="text-xs text-muted-foreground">
                Optional: Provide an SSH private key for secure host access
              </p>
            </div>

            <div className="flex items-start gap-2 p-3 border bg-muted/50 rounded-lg">
              <AlertCircle className="h-4 w-4 text-muted-foreground flex-shrink-0 mt-0.5" />
              <p className="text-xs text-muted-foreground">
                Your credentials are encrypted and stored securely. They are only used for host
                management operations.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {currentStep === 'review' && selectedProvider && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5" />
              Review & Register
            </CardTitle>
            <CardDescription>
              Review your host configuration before registering
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between py-2 border-b">
                <span className="text-sm text-muted-foreground">Provider</span>
                <ProviderBadge provider={selectedProvider} size="sm" />
              </div>

              <div className="flex items-center justify-between py-2 border-b">
                <span className="text-sm text-muted-foreground">Host Name</span>
                <span className="text-sm font-medium">{formData.name}</span>
              </div>

              <div className="flex items-center justify-between py-2 border-b">
                <span className="text-sm text-muted-foreground">Hostname</span>
                <span className="text-sm font-mono">{formData.hostname}</span>
              </div>

              <div className="flex items-center justify-between py-2 border-b">
                <span className="text-sm text-muted-foreground">Region</span>
                <span className="text-sm">{formData.region}</span>
              </div>

              {formData.tags.length > 0 && (
                <div className="flex items-start justify-between py-2 border-b">
                  <span className="text-sm text-muted-foreground">Tags</span>
                  <div className="flex flex-wrap gap-1 justify-end max-w-md">
                    {formData.tags.map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex items-center justify-between py-2 border-b">
                <span className="text-sm text-muted-foreground">SSH Key</span>
                <span className="text-sm">
                  {formData.ssh_key ? 'Configured' : 'Not configured'}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Navigation Buttons */}
      <div className="flex gap-2">
        {currentStep !== 'provider' && (
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={registering}
            className="flex-1"
          >
            <ChevronLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
        )}

        {currentStep === 'provider' && onCancel && (
          <Button
            variant="outline"
            onClick={onCancel}
            disabled={registering}
            className="flex-1"
          >
            Cancel
          </Button>
        )}

        {currentStep !== 'review' ? (
          <Button
            onClick={handleNext}
            disabled={
              (currentStep === 'provider' && !canProceedFromProvider) ||
              (currentStep === 'details' && !canProceedFromDetails)
            }
            className="flex-1"
          >
            Next
            <ChevronRight className="h-4 w-4 ml-2" />
          </Button>
        ) : (
          <Button
            onClick={handleRegister}
            disabled={!canRegister || registering}
            className="flex-1"
          >
            {registering ? 'Registering...' : 'Register Host'}
          </Button>
        )}
      </div>
    </div>
  );
}
