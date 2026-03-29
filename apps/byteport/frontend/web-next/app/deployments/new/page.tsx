'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { z } from 'zod';
import { deployApp, detectAppType, estimateCost } from '@/lib/api';
import type { DeployRequest, ProviderName } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import {
  ChevronLeft,
  ChevronRight,
  Check,
  AlertCircle,
  Plus,
  X,
  Loader2,
  Server,
  Code,
  Database,
  Globe,
  Sparkles,
} from 'lucide-react';

// Zod Validation Schemas
const step1Schema = z.object({
  name: z.string().min(3, 'Name must be at least 3 characters').max(50, 'Name is too long'),
  type: z.enum(['frontend', 'backend', 'database', 'static', 'container']),
  git_url: z.string().url('Must be a valid URL').optional().or(z.literal('')),
  branch: z.string().optional(),
});

const step2Schema = z.object({
  provider: z.enum(['vercel', 'netlify', 'render', 'railway', 'fly', 'aws', 'gcp', 'azure', 'byteport-host']).or(z.literal('auto')),
  runtime: z.string().optional(),
  framework: z.string().optional(),
  build_command: z.string().optional(),
  start_command: z.string().optional(),
  install_command: z.string().optional(),
});

type Step1Data = z.infer<typeof step1Schema>;
type Step2Data = z.infer<typeof step2Schema>;
type EnvVar = { key: string; value: string };

const APP_TYPE_ICONS = {
  frontend: Globe,
  backend: Server,
  database: Database,
  static: Code,
  container: Server,
};

export default function NewDeploymentPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [detecting, setDetecting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Form data
  const [step1Data, setStep1Data] = useState<Step1Data>({
    name: '',
    type: 'frontend',
    git_url: '',
    branch: 'main',
  });

  const [step2Data, setStep2Data] = useState<Step2Data>({
    provider: 'vercel',
    runtime: '',
    framework: '',
    build_command: '',
    start_command: '',
    install_command: '',
  });

  const [envVars, setEnvVars] = useState<EnvVar[]>([]);
  const [costEstimate, setCostEstimate] = useState<any>(null);

  const totalSteps = 3;

  const validateStep = (step: number): boolean => {
    setErrors({});
    try {
      if (step === 1) {
        step1Schema.parse(step1Data);
      } else if (step === 2) {
        step2Schema.parse(step2Data);
      }
      return true;
    } catch (error) {
      if (error instanceof z.ZodError) {
        const fieldErrors: Record<string, string> = {};
        error.issues.forEach((err) => {
          if (err.path.length > 0) {
            fieldErrors[err.path[0].toString()] = err.message;
          }
        });
        setErrors(fieldErrors);
      }
      return false;
    }
  };

  const handleNext = async () => {
    if (!validateStep(currentStep)) {
      return;
    }

    if (currentStep === 2) {
      // Fetch cost estimate before moving to review step
      try {
        setLoading(true);
        const estimate = await estimateCost({
          name: step1Data.name,
          type: step1Data.type,
          provider: step2Data.provider === 'auto' ? undefined : step2Data.provider as ProviderName
        });
        setCostEstimate(estimate);
      } catch (error) {
        console.error('Failed to fetch cost estimate:', error);
      } finally {
        setLoading(false);
      }
    }

    setCurrentStep(currentStep + 1);
  };

  const handlePrevious = () => {
    setCurrentStep(currentStep - 1);
  };

  const handleAutoDetect = async () => {
    if (!step1Data.git_url) {
      setErrors({ git_url: 'Please enter a Git URL first' });
      return;
    }

    try {
      setDetecting(true);
      const detection = await detectAppType([step1Data.git_url]);

      if (detection.detected && detection.suggested_config) {
        setStep2Data({
          ...step2Data,
          runtime: detection.suggested_config.runtime || '',
          framework: detection.suggested_config.framework || '',
          build_command: detection.suggested_config.build_command || '',
          start_command: detection.suggested_config.start_command || '',
          install_command: detection.suggested_config.install_command || '',
        });

        if (detection.suggested_config.env_vars) {
          const detectedEnvVars = Object.entries(detection.suggested_config.env_vars).map(
            ([key, value]) => ({ key, value: value as string })
          );
          setEnvVars(detectedEnvVars);
        }
      }
    } catch (error) {
      console.error('Auto-detection failed:', error);
    } finally {
      setDetecting(false);
    }
  };

  const handleDeploy = async () => {
    try {
      setLoading(true);

      const envVarsObject = envVars.reduce((acc, { key, value }) => {
        if (key && value) acc[key] = value;
        return acc;
      }, {} as Record<string, string>);

      const deploymentRequest: DeployRequest = {
        name: step1Data.name,
        type: step1Data.type,
        provider: step2Data.provider === 'auto' ? undefined : step2Data.provider as ProviderName,
        git_url: step1Data.git_url || undefined,
        branch: step1Data.branch,
        runtime: step2Data.runtime,
        framework: step2Data.framework,
        build_command: step2Data.build_command,
        start_command: step2Data.start_command,
        install_command: step2Data.install_command,
        env_vars: envVarsObject,
      };

      const response = await deployApp(deploymentRequest);
      router.push(`/deployments/${response.id}`);
    } catch (error: any) {
      setErrors({ deploy: error.message || 'Deployment failed' });
    } finally {
      setLoading(false);
    }
  };

  const addEnvVar = () => {
    setEnvVars([...envVars, { key: '', value: '' }]);
  };

  const removeEnvVar = (index: number) => {
    setEnvVars(envVars.filter((_, i) => i !== index));
  };

  const updateEnvVar = (index: number, field: 'key' | 'value', value: string) => {
    const updated = [...envVars];
    updated[index][field] = value;
    setEnvVars(updated);
  };

  const renderStepIndicator = () => (
    <div className="flex items-center justify-center mb-8">
      {[1, 2, 3].map((step, index) => (
        <div key={step} className="flex items-center">
          <div
            className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
              step < currentStep
                ? 'bg-green-600 text-white'
                : step === currentStep
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-600'
            }`}
          >
            {step < currentStep ? <Check className="w-5 h-5" /> : step}
          </div>
          {index < 2 && (
            <div
              className={`w-24 h-1 mx-2 ${
                step < currentStep ? 'bg-green-600' : 'bg-gray-200'
              }`}
            />
          )}
        </div>
      ))}
    </div>
  );

  const renderStep1 = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">Basic Information</h2>
        <p className="text-gray-600">Tell us about your application</p>
      </div>

      <div className="space-y-4">
        <div>
          <Label htmlFor="name">Application Name</Label>
          <Input
            id="name"
            value={step1Data.name}
            onChange={(e) => setStep1Data({ ...step1Data, name: e.target.value })}
            placeholder="my-awesome-app"
            className={errors.name ? 'border-red-500' : ''}
          />
          {errors.name && (
            <p className="text-red-500 text-sm mt-1 flex items-center gap-1">
              <AlertCircle className="w-4 h-4" />
              {errors.name}
            </p>
          )}
        </div>

        <div>
          <Label>Application Type</Label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-2">
            {(['frontend', 'backend', 'database', 'static', 'container'] as const).map((type) => {
              const Icon = APP_TYPE_ICONS[type];
              return (
                <button
                  key={type}
                  onClick={() => setStep1Data({ ...step1Data, type })}
                  className={`p-4 border-2 rounded-lg flex flex-col items-center gap-2 transition-all ${
                    step1Data.type === type
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <Icon className={`w-8 h-8 ${step1Data.type === type ? 'text-blue-600' : 'text-gray-600'}`} />
                  <span className={`font-medium capitalize ${step1Data.type === type ? 'text-blue-600' : ''}`}>
                    {type}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        <div>
          <Label htmlFor="git_url">Git Repository URL (Optional)</Label>
          <Input
            id="git_url"
            type="url"
            value={step1Data.git_url}
            onChange={(e) => setStep1Data({ ...step1Data, git_url: e.target.value })}
            placeholder="https://github.com/user/repo"
            className={errors.git_url ? 'border-red-500' : ''}
          />
          {errors.git_url && (
            <p className="text-red-500 text-sm mt-1 flex items-center gap-1">
              <AlertCircle className="w-4 h-4" />
              {errors.git_url}
            </p>
          )}
        </div>

        {step1Data.git_url && (
          <div>
            <Label htmlFor="branch">Branch</Label>
            <Input
              id="branch"
              value={step1Data.branch}
              onChange={(e) => setStep1Data({ ...step1Data, branch: e.target.value })}
              placeholder="main"
            />
          </div>
        )}
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold mb-2">Configuration</h2>
          <p className="text-gray-600">Configure your deployment settings</p>
        </div>
        {step1Data.git_url && (
          <Button onClick={handleAutoDetect} disabled={detecting} variant="outline">
            {detecting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Detecting...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Auto-Detect
              </>
            )}
          </Button>
        )}
      </div>

      <div className="space-y-4">
        <div>
          <Label htmlFor="provider">Cloud Provider</Label>
          <select
            id="provider"
            value={step2Data.provider}
            onChange={(e) =>
              setStep2Data({ ...step2Data, provider: e.target.value as Step2Data['provider'] })
            }
            className={`w-full px-4 py-2 border rounded-md ${errors.provider ? 'border-red-500' : ''}`}
          >
            <option value="">Select a provider</option>
            <option value="vercel">Vercel</option>
            <option value="netlify">Netlify</option>
            <option value="render">Render</option>
            <option value="railway">Railway</option>
            <option value="fly">Fly.io</option>
            <option value="aws">AWS</option>
            <option value="gcp">Google Cloud</option>
            <option value="azure">Azure</option>
            <option value="byteport-host">BytePort Host</option>
            <option value="auto">Auto Select</option>
          </select>
          {errors.provider && (
            <p className="text-red-500 text-sm mt-1 flex items-center gap-1">
              <AlertCircle className="w-4 h-4" />
              {errors.provider}
            </p>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="runtime">Runtime</Label>
            <Input
              id="runtime"
              value={step2Data.runtime}
              onChange={(e) => setStep2Data({ ...step2Data, runtime: e.target.value })}
              placeholder="node, python, go, etc."
            />
          </div>

          <div>
            <Label htmlFor="framework">Framework</Label>
            <Input
              id="framework"
              value={step2Data.framework}
              onChange={(e) => setStep2Data({ ...step2Data, framework: e.target.value })}
              placeholder="next, react, express, etc."
            />
          </div>
        </div>

        <div>
          <Label htmlFor="build_command">Build Command</Label>
          <Input
            id="build_command"
            value={step2Data.build_command}
            onChange={(e) => setStep2Data({ ...step2Data, build_command: e.target.value })}
            placeholder="npm run build"
          />
        </div>

        <div>
          <Label htmlFor="start_command">Start Command</Label>
          <Input
            id="start_command"
            value={step2Data.start_command}
            onChange={(e) => setStep2Data({ ...step2Data, start_command: e.target.value })}
            placeholder="npm start"
          />
        </div>

        <div>
          <Label htmlFor="install_command">Install Command</Label>
          <Input
            id="install_command"
            value={step2Data.install_command}
            onChange={(e) => setStep2Data({ ...step2Data, install_command: e.target.value })}
            placeholder="npm install"
          />
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <Label>Environment Variables</Label>
            <Button onClick={addEnvVar} variant="outline" size="sm">
              <Plus className="w-4 h-4 mr-1" />
              Add Variable
            </Button>
          </div>
          <div className="space-y-2">
            {envVars.map((envVar, index) => (
              <div key={index} className="flex gap-2">
                <Input
                  placeholder="KEY"
                  value={envVar.key}
                  onChange={(e) => updateEnvVar(index, 'key', e.target.value)}
                  className="flex-1"
                />
                <Input
                  placeholder="value"
                  value={envVar.value}
                  onChange={(e) => updateEnvVar(index, 'value', e.target.value)}
                  className="flex-1"
                />
                <Button
                  onClick={() => removeEnvVar(index)}
                  variant="outline"
                  size="sm"
                  className="px-3"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">Review & Deploy</h2>
        <p className="text-gray-600">Review your configuration before deploying</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Deployment Summary</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Name</p>
              <p className="font-medium">{step1Data.name}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Type</p>
              <Badge className="capitalize">{step1Data.type}</Badge>
            </div>
            <div>
              <p className="text-sm text-gray-600">Provider</p>
              <p className="font-medium capitalize">{step2Data.provider}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Runtime</p>
              <p className="font-medium">{step2Data.runtime || 'Auto-detect'}</p>
            </div>
          </div>

          {step1Data.git_url && (
            <div>
              <p className="text-sm text-gray-600">Repository</p>
              <p className="font-medium text-blue-600 break-all">{step1Data.git_url}</p>
              <p className="text-sm text-gray-500">Branch: {step1Data.branch}</p>
            </div>
          )}

          {(step2Data.build_command || step2Data.start_command) && (
            <div>
              <p className="text-sm text-gray-600 mb-2">Commands</p>
              <div className="bg-gray-900 text-gray-100 p-4 rounded-md font-mono text-sm space-y-1">
                {step2Data.install_command && (
                  <div>
                    <span className="text-gray-500">$</span> {step2Data.install_command}
                  </div>
                )}
                {step2Data.build_command && (
                  <div>
                    <span className="text-gray-500">$</span> {step2Data.build_command}
                  </div>
                )}
                {step2Data.start_command && (
                  <div>
                    <span className="text-gray-500">$</span> {step2Data.start_command}
                  </div>
                )}
              </div>
            </div>
          )}

          {envVars.length > 0 && (
            <div>
              <p className="text-sm text-gray-600 mb-2">Environment Variables</p>
              <div className="space-y-1">
                {envVars.map((envVar, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm">
                    <code className="bg-gray-100 px-2 py-1 rounded">{envVar.key}</code>
                    <span className="text-gray-400">=</span>
                    <code className="bg-gray-100 px-2 py-1 rounded flex-1 truncate">
                      {envVar.value}
                    </code>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {costEstimate && (
        <Card>
          <CardHeader>
            <CardTitle>Cost Estimate</CardTitle>
            <CardDescription>Estimated monthly cost for this deployment</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">
              ${costEstimate.estimated_monthly_cost || 0}
              <span className="text-lg text-gray-600 font-normal">/month</span>
            </div>
            {costEstimate.notes && costEstimate.notes.length > 0 && (
              <div className="mt-4 space-y-1">
                {costEstimate.notes.map((note: string, index: number) => (
                  <p key={index} className="text-sm text-gray-600">
                    {note}
                  </p>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {errors.deploy && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
              <div>
                <p className="font-medium text-red-900">Deployment Failed</p>
                <p className="text-sm text-red-700 mt-1">{errors.deploy}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );

  return (
    <div className="container mx-auto p-8 max-w-4xl">
      <div className="mb-8">
        <Link href="/deployments" className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center gap-1">
          <ChevronLeft className="w-4 h-4" />
          Back to Deployments
        </Link>
      </div>

      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle className="text-3xl">New Deployment</CardTitle>
          <CardDescription>Deploy your application in just 3 simple steps</CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          {renderStepIndicator()}

          <Progress value={(currentStep / totalSteps) * 100} className="mb-8" />

          <div className="min-h-[500px]">
            {currentStep === 1 && renderStep1()}
            {currentStep === 2 && renderStep2()}
            {currentStep === 3 && renderStep3()}
          </div>

          <div className="flex items-center justify-between mt-8 pt-6 border-t">
            <Button
              onClick={handlePrevious}
              variant="outline"
              disabled={currentStep === 1 || loading}
            >
              <ChevronLeft className="w-4 h-4 mr-2" />
              Previous
            </Button>

            {currentStep < totalSteps ? (
              <Button onClick={handleNext} disabled={loading}>
                Next
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            ) : (
              <Button onClick={handleDeploy} disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Deploying...
                  </>
                ) : (
                  <>
                    <Check className="w-4 h-4 mr-2" />
                    Deploy Now
                  </>
                )}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
