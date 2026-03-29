"use client"

import * as React from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { cn } from "@/lib/utils"
import { AppType, DeployRequest, ProviderName } from "@/lib/types"
import { ProviderSelector } from "@/components/provider-selector"
import { EnvVarEditor } from "@/components/env-var-editor"

const deploymentSchema = z.object({
  name: z.string().min(1, "Name is required").max(50),
  type: z.enum(["frontend", "backend", "database", "static", "container"]),
  provider: z.string().min(1, "Provider is required"),
  git_url: z.string().url().optional().or(z.literal("")),
  branch: z.string().optional(),
  runtime: z.string().optional(),
  framework: z.string().optional(),
  build_command: z.string().optional(),
  start_command: z.string().optional(),
  install_command: z.string().optional(),
  env_vars: z.record(z.string(), z.string()).optional(),
})

type DeploymentFormValues = z.input<typeof deploymentSchema>

export interface DeploymentWizardProps {
  onSubmit: (data: DeployRequest) => void | Promise<void>
  onCancel?: () => void
  initialData?: Partial<DeployRequest>
  className?: string
}

export function DeploymentWizard({
  onSubmit,
  onCancel,
  initialData,
  className,
}: DeploymentWizardProps) {
  const [currentStep, setCurrentStep] = React.useState(0)
  const [isSubmitting, setIsSubmitting] = React.useState(false)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<DeploymentFormValues>({
    resolver: zodResolver(deploymentSchema),
    defaultValues: {
      name: initialData?.name || "",
      type: initialData?.type || "frontend",
      provider: (initialData?.provider as ProviderName | undefined) || "",
      git_url: initialData?.git_url || "",
      branch: initialData?.branch || "main",
      runtime: initialData?.runtime || "",
      framework: initialData?.framework || "",
      build_command: initialData?.build_command || "",
      start_command: initialData?.start_command || "",
      install_command: initialData?.install_command || "",
      env_vars: initialData?.env_vars || {},
    },
  })

  const appType = watch("type")
  const provider = watch("provider")
  const envVars = (watch("env_vars") ?? {}) as Record<string, string>

  const steps = [
    { id: "basics", title: "Basic Info", description: "Name and type" },
    { id: "provider", title: "Provider", description: "Select deployment provider" },
    { id: "source", title: "Source", description: "Repository and runtime" },
    { id: "config", title: "Configuration", description: "Build and environment" },
  ]

  const progress = ((currentStep + 1) / steps.length) * 100

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleFormSubmit = async (data: DeploymentFormValues) => {
    setIsSubmitting(true)
    try {
      const payload: DeployRequest = {
        ...data,
        provider: data.provider as ProviderName,
      }
      await onSubmit(payload)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Card className={cn("w-full max-w-3xl", className)}>
      <CardHeader>
        <div className="space-y-2">
          <CardTitle>New Deployment</CardTitle>
          <CardDescription>
            {steps[currentStep].title}: {steps[currentStep].description}
          </CardDescription>
          <Progress value={progress} className="h-2" />
        </div>
      </CardHeader>

      <form onSubmit={handleSubmit(handleFormSubmit)}>
        <CardContent className="space-y-6">
          {/* Step 1: Basic Info */}
          {currentStep === 0 && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Deployment Name</Label>
                <Input
                  id="name"
                  placeholder="my-awesome-app"
                  {...register("name")}
                  aria-invalid={errors.name ? "true" : "false"}
                />
                {errors.name && (
                  <p className="text-sm text-destructive">{errors.name.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label>Application Type</Label>
                <Tabs
                  value={appType}
                  onValueChange={(value) => setValue("type", value as AppType)}
                >
                  <TabsList className="grid w-full grid-cols-5">
                    <TabsTrigger value="frontend">Frontend</TabsTrigger>
                    <TabsTrigger value="backend">Backend</TabsTrigger>
                    <TabsTrigger value="static">Static</TabsTrigger>
                    <TabsTrigger value="database">Database</TabsTrigger>
                    <TabsTrigger value="container">Container</TabsTrigger>
                  </TabsList>
                </Tabs>
              </div>
            </div>
          )}

          {/* Step 2: Provider */}
          {currentStep === 1 && (
            <div className="space-y-4">
              <ProviderSelector
                value={provider as ProviderName}
                onChange={(value) => setValue("provider", value)}
                appType={appType}
              />
              {errors.provider && (
                <p className="text-sm text-destructive">{errors.provider.message}</p>
              )}
            </div>
          )}

          {/* Step 3: Source */}
          {currentStep === 2 && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="git_url">Git Repository URL</Label>
                <Input
                  id="git_url"
                  type="url"
                  placeholder="https://github.com/username/repo"
                  {...register("git_url")}
                />
                {errors.git_url && (
                  <p className="text-sm text-destructive">{errors.git_url.message}</p>
                )}
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="branch">Branch</Label>
                  <Input id="branch" placeholder="main" {...register("branch")} />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="runtime">Runtime</Label>
                  <Input
                    id="runtime"
                    placeholder="node@20, python@3.11"
                    {...register("runtime")}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="framework">Framework (optional)</Label>
                <Input
                  id="framework"
                  placeholder="next, react, vue, django, fastapi"
                  {...register("framework")}
                />
              </div>
            </div>
          )}

          {/* Step 4: Configuration */}
          {currentStep === 3 && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="install_command">Install Command (optional)</Label>
                <Input
                  id="install_command"
                  placeholder="npm install"
                  {...register("install_command")}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="build_command">Build Command (optional)</Label>
                <Input
                  id="build_command"
                  placeholder="npm run build"
                  {...register("build_command")}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="start_command">Start Command (optional)</Label>
                <Input
                  id="start_command"
                  placeholder="npm start"
                  {...register("start_command")}
                />
              </div>

              <div className="space-y-2">
                <Label>Environment Variables</Label>
                <EnvVarEditor
                  variables={envVars}
                  onChange={(vars) => setValue("env_vars", vars)}
                />
              </div>
            </div>
          )}
        </CardContent>

        <CardFooter className="flex justify-between">
          <Button
            type="button"
            variant="outline"
            onClick={currentStep === 0 ? onCancel : handleBack}
          >
            <ChevronLeft className="mr-2 h-4 w-4" />
            {currentStep === 0 ? "Cancel" : "Back"}
          </Button>

          {currentStep < steps.length - 1 ? (
            <Button type="button" onClick={handleNext}>
              Next
              <ChevronRight className="ml-2 h-4 w-4" />
            </Button>
          ) : (
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Deploying..." : "Deploy"}
            </Button>
          )}
        </CardFooter>
      </form>
    </Card>
  )
}
