"use client"

import * as React from "react"
import { Check, Circle, Loader2, XCircle } from "lucide-react"
import { cn } from "@/lib/utils"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"

export interface DeploymentStep {
  id: string
  label: string
  description?: string
  status: "pending" | "active" | "completed" | "failed"
  error?: string
}

export interface DeploymentProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  steps: DeploymentStep[]
  currentStep?: number
  progress?: number
  showProgress?: boolean
}

export function DeploymentProgress({
  steps,
  currentStep = 0,
  progress = 0,
  showProgress = true,
  className,
  ...props
}: DeploymentProgressProps) {
  const getStepIcon = (step: DeploymentStep, index: number) => {
    switch (step.status) {
      case "completed":
        return <Check className="h-5 w-5 text-green-500" />
      case "active":
        return <Loader2 className="h-5 w-5 animate-spin text-primary" />
      case "failed":
        return <XCircle className="h-5 w-5 text-destructive" />
      default:
        return (
          <Circle
            className={cn(
              "h-5 w-5",
              index < currentStep ? "text-muted-foreground" : "text-muted-foreground/40"
            )}
          />
        )
    }
  }

  return (
    <Card className={cn("", className)} {...props}>
      <CardHeader>
        <CardTitle className="text-base">Deployment Progress</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {showProgress && (
          <div className="space-y-2">
            <Progress value={progress} className="h-2" />
            <p className="text-right text-xs text-muted-foreground">{Math.round(progress)}%</p>
          </div>
        )}

        <div className="space-y-4">
          {steps.map((step, index) => (
            <div key={step.id} className="flex gap-3">
              <div className="relative flex flex-col items-center">
                {getStepIcon(step, index)}
                {index < steps.length - 1 && (
                  <div
                    className={cn(
                      "mt-1 h-full w-px",
                      step.status === "completed"
                        ? "bg-green-500/20"
                        : "bg-muted-foreground/20"
                    )}
                    style={{ minHeight: "2rem" }}
                  />
                )}
              </div>

              <div className="flex-1 space-y-1 pb-4">
                <div className="flex items-center justify-between">
                  <p
                    className={cn(
                      "font-medium",
                      step.status === "active" && "text-primary",
                      step.status === "completed" && "text-green-600 dark:text-green-500",
                      step.status === "failed" && "text-destructive",
                      step.status === "pending" && "text-muted-foreground"
                    )}
                  >
                    {step.label}
                  </p>
                  {step.status === "active" && (
                    <span className="text-xs text-muted-foreground">In progress...</span>
                  )}
                </div>

                {step.description && (
                  <p className="text-sm text-muted-foreground">{step.description}</p>
                )}

                {step.error && (
                  <div className="mt-2 rounded-md bg-destructive/10 p-2 text-xs text-destructive">
                    {step.error}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
