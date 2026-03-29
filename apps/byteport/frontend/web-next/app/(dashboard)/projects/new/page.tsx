'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardHeader } from '@/components/layout/Header';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import {
  GitBranch,
  Upload,
  Github,
  Gitlab,
  FileCode,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  Loader2
} from 'lucide-react';

type Step = 'repository' | 'configuration' | 'review';
type GitProvider = 'github' | 'gitlab' | 'custom';

interface ProjectFormData {
  name: string;
  description: string;
  gitProvider: GitProvider;
  repositoryUrl: string;
  branch: string;
  nvmsConfig?: File;
  autoDeployEnabled: boolean;
  framework?: string;
}

export default function NewProjectPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<Step>('repository');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<ProjectFormData>({
    name: '',
    description: '',
    gitProvider: 'github',
    repositoryUrl: '',
    branch: 'main',
    autoDeployEnabled: true,
  });

  const updateFormData = (updates: Partial<ProjectFormData>) => {
    setFormData({ ...formData, ...updates });
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setError(null);

    try {
      // TODO: Replace with actual API call
      await new Promise((resolve) => setTimeout(resolve, 1500));

      console.log('Creating project:', formData);

      // Redirect to project details
      router.push('/projects');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project');
      setSubmitting(false);
    }
  };

  const canProceed = () => {
    if (currentStep === 'repository') {
      return formData.repositoryUrl && formData.branch;
    }
    if (currentStep === 'configuration') {
      return formData.name;
    }
    return true;
  };

  const steps = [
    { id: 'repository', label: 'Repository', icon: GitBranch },
    { id: 'configuration', label: 'Configuration', icon: FileCode },
    { id: 'review', label: 'Review', icon: CheckCircle2 },
  ];

  const currentStepIndex = steps.findIndex((s) => s.id === currentStep);

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <DashboardHeader
        title="New Project"
        subtitle="Connect your Git repository and configure deployment settings"
        action={
          <Button variant="outline" onClick={() => router.push('/projects')}>
            Cancel
          </Button>
        }
      />

      <section className="flex-1 overflow-y-auto px-6 py-8">
        <div className="mx-auto max-w-4xl">
          {/* Progress Steps */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              {steps.map((step, index) => (
                <div key={step.id} className="flex items-center">
                  <div className="flex flex-col items-center">
                    <div
                      className={`flex h-12 w-12 items-center justify-center rounded-full border-2 transition-colors ${
                        index <= currentStepIndex
                          ? 'border-primary bg-primary text-primary-foreground'
                          : 'border-muted bg-muted text-muted-foreground'
                      }`}
                    >
                      <step.icon className="h-5 w-5" />
                    </div>
                    <span
                      className={`mt-2 text-sm font-medium ${
                        index <= currentStepIndex ? 'text-foreground' : 'text-muted-foreground'
                      }`}
                    >
                      {step.label}
                    </span>
                  </div>
                  {index < steps.length - 1 && (
                    <div
                      className={`mx-4 h-0.5 w-24 transition-colors ${
                        index < currentStepIndex ? 'bg-primary' : 'bg-muted'
                      }`}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Step Content */}
          <Card className="p-8">
            {error && (
              <div className="mb-6 flex items-center gap-2 rounded-lg bg-destructive/10 p-4 text-destructive">
                <AlertCircle className="h-5 w-5" />
                <p className="text-sm">{error}</p>
              </div>
            )}

            {currentStep === 'repository' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold mb-4">Connect Git Repository</h3>
                  <p className="text-sm text-muted-foreground mb-6">
                    Connect your Git repository to enable continuous deployment
                  </p>
                </div>

                <div className="space-y-4">
                  <div>
                    <Label htmlFor="git-provider">Git Provider</Label>
                    <RadioGroup
                      value={formData.gitProvider}
                      onValueChange={(value) => updateFormData({ gitProvider: value as GitProvider })}
                      className="mt-2 grid grid-cols-3 gap-4"
                    >
                      <label
                        htmlFor="github"
                        className={`flex cursor-pointer items-center gap-3 rounded-lg border p-4 transition-colors ${
                          formData.gitProvider === 'github'
                            ? 'border-primary bg-primary/5'
                            : 'border-border hover:border-primary/50'
                        }`}
                      >
                        <RadioGroupItem value="github" id="github" />
                        <Github className="h-5 w-5" />
                        <span className="font-medium">GitHub</span>
                      </label>

                      <label
                        htmlFor="gitlab"
                        className={`flex cursor-pointer items-center gap-3 rounded-lg border p-4 transition-colors ${
                          formData.gitProvider === 'gitlab'
                            ? 'border-primary bg-primary/5'
                            : 'border-border hover:border-primary/50'
                        }`}
                      >
                        <RadioGroupItem value="gitlab" id="gitlab" />
                        <Gitlab className="h-5 w-5" />
                        <span className="font-medium">GitLab</span>
                      </label>

                      <label
                        htmlFor="custom"
                        className={`flex cursor-pointer items-center gap-3 rounded-lg border p-4 transition-colors ${
                          formData.gitProvider === 'custom'
                            ? 'border-primary bg-primary/5'
                            : 'border-border hover:border-primary/50'
                        }`}
                      >
                        <RadioGroupItem value="custom" id="custom" />
                        <GitBranch className="h-5 w-5" />
                        <span className="font-medium">Custom</span>
                      </label>
                    </RadioGroup>
                  </div>

                  <div>
                    <Label htmlFor="repository-url">Repository URL</Label>
                    <Input
                      id="repository-url"
                      placeholder="https://github.com/username/repository"
                      value={formData.repositoryUrl}
                      onChange={(e) => updateFormData({ repositoryUrl: e.target.value })}
                      className="mt-2"
                    />
                    <p className="mt-1 text-xs text-muted-foreground">
                      The HTTPS URL of your Git repository
                    </p>
                  </div>

                  <div>
                    <Label htmlFor="branch">Default Branch</Label>
                    <Input
                      id="branch"
                      placeholder="main"
                      value={formData.branch}
                      onChange={(e) => updateFormData({ branch: e.target.value })}
                      className="mt-2"
                    />
                    <p className="mt-1 text-xs text-muted-foreground">
                      The branch to deploy from by default
                    </p>
                  </div>
                </div>
              </div>
            )}

            {currentStep === 'configuration' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold mb-4">Project Configuration</h3>
                  <p className="text-sm text-muted-foreground mb-6">
                    Configure your project settings and deployment options
                  </p>
                </div>

                <div className="space-y-4">
                  <div>
                    <Label htmlFor="name">Project Name</Label>
                    <Input
                      id="name"
                      placeholder="My Awesome Project"
                      value={formData.name}
                      onChange={(e) => updateFormData({ name: e.target.value })}
                      className="mt-2"
                    />
                    <p className="mt-1 text-xs text-muted-foreground">
                      A friendly name for your project
                    </p>
                  </div>

                  <div>
                    <Label htmlFor="description">Description (Optional)</Label>
                    <Textarea
                      id="description"
                      placeholder="A brief description of your project"
                      value={formData.description}
                      onChange={(e) => updateFormData({ description: e.target.value })}
                      className="mt-2"
                      rows={3}
                    />
                  </div>

                  <div>
                    <Label htmlFor="framework">Framework (Optional)</Label>
                    <Input
                      id="framework"
                      placeholder="e.g., Next.js, React, Node.js"
                      value={formData.framework || ''}
                      onChange={(e) => updateFormData({ framework: e.target.value })}
                      className="mt-2"
                    />
                    <p className="mt-1 text-xs text-muted-foreground">
                      The framework or runtime used by your project
                    </p>
                  </div>

                  <div>
                    <Label htmlFor="nvms-config">NVMS Configuration (Optional)</Label>
                    <div className="mt-2 flex items-center gap-4">
                      <Input
                        id="nvms-config"
                        type="file"
                        accept=".json,.yaml,.yml"
                        onChange={(e) => {
                          const file = e.target.files?.[0];
                          if (file) updateFormData({ nvmsConfig: file });
                        }}
                        className="flex-1"
                      />
                      <Button variant="outline" size="sm">
                        <Upload className="h-4 w-4 mr-2" />
                        Upload
                      </Button>
                    </div>
                    <p className="mt-1 text-xs text-muted-foreground">
                      Upload an NVMS configuration file for advanced deployment settings
                    </p>
                  </div>

                  <div className="flex items-center gap-2 pt-4">
                    <input
                      type="checkbox"
                      id="auto-deploy"
                      checked={formData.autoDeployEnabled}
                      onChange={(e) => updateFormData({ autoDeployEnabled: e.target.checked })}
                      className="rounded"
                    />
                    <Label htmlFor="auto-deploy" className="cursor-pointer">
                      Enable automatic deployments on push
                    </Label>
                  </div>
                </div>
              </div>
            )}

            {currentStep === 'review' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold mb-4">Review Project Settings</h3>
                  <p className="text-sm text-muted-foreground mb-6">
                    Verify your project configuration before creating
                  </p>
                </div>

                <div className="space-y-4">
                  <Card className="p-4 bg-muted/50">
                    <h4 className="font-semibold mb-3">Repository</h4>
                    <dl className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <dt className="text-muted-foreground">Provider:</dt>
                        <dd className="font-medium capitalize">{formData.gitProvider}</dd>
                      </div>
                      <div className="flex justify-between">
                        <dt className="text-muted-foreground">URL:</dt>
                        <dd className="font-mono text-xs">{formData.repositoryUrl}</dd>
                      </div>
                      <div className="flex justify-between">
                        <dt className="text-muted-foreground">Branch:</dt>
                        <dd className="font-medium">{formData.branch}</dd>
                      </div>
                    </dl>
                  </Card>

                  <Card className="p-4 bg-muted/50">
                    <h4 className="font-semibold mb-3">Configuration</h4>
                    <dl className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <dt className="text-muted-foreground">Name:</dt>
                        <dd className="font-medium">{formData.name}</dd>
                      </div>
                      {formData.description && (
                        <div className="flex justify-between">
                          <dt className="text-muted-foreground">Description:</dt>
                          <dd className="font-medium">{formData.description}</dd>
                        </div>
                      )}
                      {formData.framework && (
                        <div className="flex justify-between">
                          <dt className="text-muted-foreground">Framework:</dt>
                          <dd className="font-medium">{formData.framework}</dd>
                        </div>
                      )}
                      <div className="flex justify-between">
                        <dt className="text-muted-foreground">Auto Deploy:</dt>
                        <dd className="font-medium">
                          {formData.autoDeployEnabled ? 'Enabled' : 'Disabled'}
                        </dd>
                      </div>
                      {formData.nvmsConfig && (
                        <div className="flex justify-between">
                          <dt className="text-muted-foreground">NVMS Config:</dt>
                          <dd className="font-medium">{formData.nvmsConfig.name}</dd>
                        </div>
                      )}
                    </dl>
                  </Card>
                </div>
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="mt-8 flex justify-between">
              <Button
                variant="outline"
                onClick={() => {
                  if (currentStepIndex > 0) {
                    setCurrentStep(steps[currentStepIndex - 1].id as Step);
                  } else {
                    router.push('/projects');
                  }
                }}
                disabled={submitting}
              >
                {currentStepIndex === 0 ? 'Cancel' : 'Back'}
              </Button>

              {currentStep === 'review' ? (
                <Button onClick={handleSubmit} disabled={submitting}>
                  {submitting ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    <>
                      Create Project
                      <CheckCircle2 className="h-4 w-4 ml-2" />
                    </>
                  )}
                </Button>
              ) : (
                <Button
                  onClick={() => setCurrentStep(steps[currentStepIndex + 1].id as Step)}
                  disabled={!canProceed()}
                >
                  Next
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              )}
            </div>
          </Card>
        </div>
      </section>
    </div>
  );
}
