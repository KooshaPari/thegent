"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Plus, X, Eye, EyeOff, Upload, Download } from "lucide-react"
import { cn } from "@/lib/utils"

export interface EnvVariable {
  key: string
  value: string
  isSecret?: boolean
}

export interface EnvVarEditorProps {
  variables?: Record<string, string>
  onChange?: (variables: Record<string, string>) => void
  className?: string
  showImportExport?: boolean
  allowSecrets?: boolean
}

export function EnvVarEditor({
  variables = {},
  onChange,
  className,
  showImportExport = false,
  allowSecrets = true,
}: EnvVarEditorProps) {
  const [envVars, setEnvVars] = React.useState<EnvVariable[]>(() => {
    const entries = Object.entries(variables)
    if (entries.length === 0) {
      return [{ key: "", value: "", isSecret: false }]
    }
    return entries.map(([key, value]) => ({
      key,
      value,
      isSecret: false,
    }))
  })

  const [visibleValues, setVisibleValues] = React.useState<Set<number>>(new Set())

  React.useEffect(() => {
    const validVars = envVars.filter((v) => v.key.trim() !== "")
    const varsObject = validVars.reduce((acc, { key, value }) => {
      if (key.trim()) {
        acc[key] = value
      }
      return acc
    }, {} as Record<string, string>)

    onChange?.(varsObject)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [envVars])

  const handleAdd = () => {
    setEnvVars([...envVars, { key: "", value: "", isSecret: false }])
  }

  const handleRemove = (index: number) => {
    const newVars = envVars.filter((_, i) => i !== index)
    setEnvVars(newVars.length === 0 ? [{ key: "", value: "", isSecret: false }] : newVars)

    // Update visible values set
    const newVisible = new Set<number>()
    visibleValues.forEach((i) => {
      if (i < index) newVisible.add(i)
      else if (i > index) newVisible.add(i - 1)
    })
    setVisibleValues(newVisible)
  }

  const handleKeyChange = (index: number, key: string) => {
    const newVars = [...envVars]
    newVars[index].key = key
    setEnvVars(newVars)
  }

  const handleValueChange = (index: number, value: string) => {
    const newVars = [...envVars]
    newVars[index].value = value
    setEnvVars(newVars)
  }

  const toggleVisibility = (index: number) => {
    const newVisible = new Set(visibleValues)
    if (newVisible.has(index)) {
      newVisible.delete(index)
    } else {
      newVisible.add(index)
    }
    setVisibleValues(newVisible)
  }

  const handleImport = () => {
    const input = document.createElement("input")
    input.type = "file"
    input.accept = ".env,.txt"
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (!file) return

      const reader = new FileReader()
      reader.onload = (event) => {
        const content = event.target?.result as string
        const lines = content.split("\n")
        const imported: EnvVariable[] = []

        lines.forEach((line) => {
          const trimmed = line.trim()
          if (trimmed && !trimmed.startsWith("#")) {
            const [key, ...valueParts] = trimmed.split("=")
            if (key) {
              const value = valueParts.join("=").replace(/^["']|["']$/g, "")
              imported.push({ key: key.trim(), value, isSecret: false })
            }
          }
        })

        if (imported.length > 0) {
          setEnvVars(imported)
        }
      }
      reader.readAsText(file)
    }
    input.click()
  }

  const handleExport = () => {
    const content = envVars
      .filter((v) => v.key.trim() !== "")
      .map((v) => `${v.key}=${v.value}`)
      .join("\n")

    const blob = new Blob([content], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = ".env"
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Environment Variables</CardTitle>
            <CardDescription>
              Configure environment variables for your deployment
            </CardDescription>
          </div>
          {showImportExport && (
            <div className="flex gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleImport}
              >
                <Upload className="h-4 w-4 mr-2" />
                Import
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleExport}
                disabled={envVars.filter((v) => v.key.trim()).length === 0}
              >
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3">
          {envVars.map((envVar, index) => (
            <div key={index} className="flex gap-2 items-start">
              <div className="flex-1 grid grid-cols-2 gap-2">
                <div className="space-y-1">
                  {index === 0 && (
                    <Label className="text-xs text-muted-foreground">Key</Label>
                  )}
                  <Input
                    placeholder="VARIABLE_NAME"
                    value={envVar.key}
                    onChange={(e) => handleKeyChange(index, e.target.value)}
                    className="font-mono text-sm"
                  />
                </div>
                <div className="space-y-1">
                  {index === 0 && (
                    <Label className="text-xs text-muted-foreground">Value</Label>
                  )}
                  <div className="relative">
                    <Input
                      type={
                        allowSecrets && !visibleValues.has(index)
                          ? "password"
                          : "text"
                      }
                      placeholder="value"
                      value={envVar.value}
                      onChange={(e) => handleValueChange(index, e.target.value)}
                      className="font-mono text-sm pr-10"
                    />
                    {allowSecrets && envVar.value && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                        onClick={() => toggleVisibility(index)}
                      >
                        {visibleValues.has(index) ? (
                          <EyeOff className="h-4 w-4 text-muted-foreground" />
                        ) : (
                          <Eye className="h-4 w-4 text-muted-foreground" />
                        )}
                      </Button>
                    )}
                  </div>
                </div>
              </div>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={() => handleRemove(index)}
                disabled={envVars.length === 1}
                className="mt-0 h-10 w-10"
              >
                <X className="h-4 w-4" />
                <span className="sr-only">Remove variable</span>
              </Button>
            </div>
          ))}
        </div>

        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleAdd}
          className="w-full"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Variable
        </Button>

        {envVars.filter((v) => v.key.trim()).length > 0 && (
          <div className="text-sm text-muted-foreground">
            {envVars.filter((v) => v.key.trim()).length} variable(s) configured
          </div>
        )}
      </CardContent>
    </Card>
  )
}
