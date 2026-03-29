'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Eye, EyeOff, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

interface ProviderField {
  name: string;
  label: string;
  type: 'text' | 'password' | 'textarea';
  placeholder: string;
  required: boolean;
  helpText?: string;
}

export interface ProviderConfiguration {
  provider: string;
  icon: React.ReactNode;
  name: string;
  description: string;
  fields: ProviderField[];
  configured: boolean;
  lastVerified?: string;
}

// Alias for backwards compat
type ProviderCredential = ProviderConfiguration;

interface ProviderCredentialsFormProps {
  credential: ProviderCredential;
  onSave?: (provider: string, values: Record<string, string>) => Promise<void>;
  onTest?: (provider: string, values: Record<string, string>) => Promise<boolean>;
  onRemove?: (provider: string) => Promise<void>;
}

export function ProviderCredentialsForm({
  credential,
  onSave,
  onTest,
  onRemove,
}: ProviderCredentialsFormProps) {
  const [isEditing, setIsEditing] = useState(!credential.configured);
  const [isSaving, setIsSaving] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [isRemoving, setIsRemoving] = useState(false);
  const [showPasswords, setShowPasswords] = useState<Record<string, boolean>>({});
  const [values, setValues] = useState<Record<string, string>>({});
  const [testResult, setTestResult] = useState<'success' | 'error' | null>(null);

  const handleTogglePassword = (fieldName: string) => {
    setShowPasswords((prev) => ({ ...prev, [fieldName]: !prev[fieldName] }));
  };

  const handleValueChange = (fieldName: string, value: string) => {
    setValues((prev) => ({ ...prev, [fieldName]: value }));
    setTestResult(null);
  };

  const handleSave = async () => {
    // Validate required fields
    const missingFields = credential.fields
      .filter((field) => field.required && !values[field.name]?.trim())
      .map((field) => field.label);

    if (missingFields.length > 0) {
      toast.error(`Please fill in: ${missingFields.join(', ')}`);
      return;
    }

    setIsSaving(true);
    try {
      await onSave?.(credential.provider, values);
      toast.success(`${credential.name} credentials saved successfully`);
      setIsEditing(false);
    } catch (_error) {
      toast.error(`Failed to save ${credential.name} credentials`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleTest = async () => {
    setIsTesting(true);
    setTestResult(null);

    try {
      const result = await onTest?.(credential.provider, values);
      setTestResult(result ? 'success' : 'error');

      if (result) {
        toast.success('Credentials verified successfully');
      } else {
        toast.error('Failed to verify credentials');
      }
    } catch (_error) {
      setTestResult('error');
      toast.error('Failed to test credentials');
    } finally {
      setIsTesting(false);
    }
  };

  const handleRemove = async () => {
    setIsRemoving(true);
    try {
      await onRemove?.(credential.provider);
      toast.success(`${credential.name} credentials removed`);
      setValues({});
      setIsEditing(true);
    } catch (_error) {
      toast.error(`Failed to remove ${credential.name} credentials`);
    } finally {
      setIsRemoving(false);
    }
  };

  const handleCancel = () => {
    setValues({});
    setTestResult(null);
    if (credential.configured) {
      setIsEditing(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3">
            <div className="rounded-lg bg-muted p-2">{credential.icon}</div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <CardTitle>{credential.name}</CardTitle>
                {credential.configured && (
                  <Badge variant="secondary" className="gap-1">
                    <CheckCircle2 className="h-3 w-3" />
                    Configured
                  </Badge>
                )}
              </div>
              <CardDescription>{credential.description}</CardDescription>
              {credential.configured && credential.lastVerified && (
                <p className="text-xs text-muted-foreground">
                  Last verified: {new Date(credential.lastVerified).toLocaleDateString()}
                </p>
              )}
            </div>
          </div>
          {!isEditing && (
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={() => setIsEditing(true)}>
                Edit
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleRemove}
                disabled={isRemoving}
                className="text-destructive hover:text-destructive"
              >
                {isRemoving ? 'Removing...' : 'Remove'}
              </Button>
            </div>
          )}
        </div>
      </CardHeader>

      {isEditing && (
        <CardContent>
          <div className="space-y-4">
            {credential.fields.map((field) => (
              <div key={field.name} className="space-y-2">
                <Label htmlFor={field.name}>
                  {field.label}
                  {field.required && <span className="text-destructive ml-1">*</span>}
                </Label>
                <div className="relative">
                  {field.type === 'textarea' ? (
                    <Textarea
                      id={field.name}
                      value={values[field.name] || ''}
                      onChange={(e) => handleValueChange(field.name, e.target.value)}
                      placeholder={field.placeholder}
                      rows={6}
                      className="font-mono text-xs"
                    />
                  ) : (
                    <>
                      <Input
                        id={field.name}
                        type={
                          field.type === 'password' && !showPasswords[field.name]
                            ? 'password'
                            : 'text'
                        }
                        value={values[field.name] || ''}
                        onChange={(e) => handleValueChange(field.name, e.target.value)}
                        placeholder={field.placeholder}
                        className={field.type === 'password' ? 'pr-10' : ''}
                      />
                      {field.type === 'password' && (
                        <button
                          type="button"
                          onClick={() => handleTogglePassword(field.name)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                        >
                          {showPasswords[field.name] ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </button>
                      )}
                    </>
                  )}
                </div>
                {field.helpText && (
                  <p className="text-xs text-muted-foreground">{field.helpText}</p>
                )}
              </div>
            ))}

            {testResult && (
              <Alert variant={testResult === 'success' ? 'default' : 'destructive'}>
                {testResult === 'success' ? (
                  <CheckCircle2 className="h-4 w-4" />
                ) : (
                  <AlertCircle className="h-4 w-4" />
                )}
                <AlertDescription>
                  {testResult === 'success'
                    ? 'Credentials verified successfully'
                    : 'Failed to verify credentials. Please check your credentials and try again.'}
                </AlertDescription>
              </Alert>
            )}

            <div className="flex items-center gap-2 pt-2">
              <Button onClick={handleSave} disabled={isSaving || isTesting}>
                {isSaving ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Save Credentials'
                )}
              </Button>
              <Button
                variant="outline"
                onClick={handleTest}
                disabled={isSaving || isTesting}
              >
                {isTesting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Testing...
                  </>
                ) : (
                  'Test Connection'
                )}
              </Button>
              {credential.configured && (
                <Button variant="ghost" onClick={handleCancel} disabled={isSaving || isTesting}>
                  Cancel
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  );
}
