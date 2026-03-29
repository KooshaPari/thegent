'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Copy, AlertTriangle, Key } from 'lucide-react';
import toast from 'react-hot-toast';

interface CreatedKeyPayload {
  id: string;
  name: string;
  key: string;
  scopes: string[];
  created_at: string;
}

interface CreateKeyDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onKeyCreated?: (key: CreatedKeyPayload) => void;
}

const availableScopes = [
  { id: 'deployments:read', label: 'Read Deployments', description: 'View deployment information' },
  { id: 'deployments:write', label: 'Write Deployments', description: 'Create and manage deployments' },
  { id: 'projects:read', label: 'Read Projects', description: 'View project information' },
  { id: 'projects:write', label: 'Write Projects', description: 'Create and manage projects' },
  { id: 'metrics:read', label: 'Read Metrics', description: 'Access monitoring and metrics data' },
  { id: 'logs:read', label: 'Read Logs', description: 'Access application logs' },
  { id: 'costs:read', label: 'Read Costs', description: 'View cost information' },
  { id: 'admin', label: 'Admin Access', description: 'Full access to all resources' },
];

export function CreateKeyDialog({ open, onOpenChange, onKeyCreated }: CreateKeyDialogProps) {
  const [step, setStep] = useState<'create' | 'display'>('create');
  const [isCreating, setIsCreating] = useState(false);
  const [keyName, setKeyName] = useState('');
  const [selectedScopes, setSelectedScopes] = useState<string[]>([]);
  const [createdKey, setCreatedKey] = useState('');

  const handleClose = () => {
    setStep('create');
    setKeyName('');
    setSelectedScopes([]);
    setCreatedKey('');
    onOpenChange(false);
  };

  const handleScopeToggle = (scopeId: string) => {
    setSelectedScopes((prev) =>
      prev.includes(scopeId) ? prev.filter((s) => s !== scopeId) : [...prev, scopeId]
    );
  };

  const handleCreate = async () => {
    if (!keyName.trim()) {
      toast.error('Please enter a key name');
      return;
    }

    if (selectedScopes.length === 0) {
      toast.error('Please select at least one scope');
      return;
    }

    setIsCreating(true);

    try {
      // TODO: Replace with actual API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Generate a mock API key
      const mockKey = `bp_${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`;

      const newKey = {
        id: Math.random().toString(36).substring(7),
        name: keyName,
        key: mockKey,
        scopes: selectedScopes,
        created_at: new Date().toISOString(),
      };

      setCreatedKey(mockKey);
      setStep('display');
      onKeyCreated?.(newKey);
      toast.success('API key created successfully');
    } catch (_error) {
      toast.error('Failed to create API key');
    } finally {
      setIsCreating(false);
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(createdKey);
      toast.success('API key copied to clipboard');
    } catch (_error) {
      toast.error('Failed to copy API key');
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        {step === 'create' ? (
          <>
            <DialogHeader>
              <DialogTitle>Create API Key</DialogTitle>
              <DialogDescription>
                Create a new API key with specific permissions for accessing your resources
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-6 py-4">
              <div className="space-y-2">
                <Label htmlFor="key-name">Key Name</Label>
                <Input
                  id="key-name"
                  placeholder="e.g., Production Deployment Key"
                  value={keyName}
                  onChange={(e) => setKeyName(e.target.value)}
                />
                <p className="text-xs text-muted-foreground">
                  A descriptive name to help you identify this key later
                </p>
              </div>

              <div className="space-y-3">
                <Label>Permissions</Label>
                <div className="space-y-3 rounded-lg border p-4 max-h-[300px] overflow-y-auto">
                  {availableScopes.map((scope) => (
                    <div key={scope.id} className="flex items-start space-x-3">
                      <Checkbox
                        id={scope.id}
                        checked={selectedScopes.includes(scope.id)}
                        onCheckedChange={() => handleScopeToggle(scope.id)}
                      />
                      <div className="grid gap-1 leading-none">
                        <label
                          htmlFor={scope.id}
                          className="text-sm font-medium cursor-pointer"
                        >
                          {scope.label}
                        </label>
                        <p className="text-xs text-muted-foreground">{scope.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={handleClose}>
                Cancel
              </Button>
              <Button onClick={handleCreate} disabled={isCreating}>
                {isCreating ? 'Creating...' : 'Create Key'}
              </Button>
            </DialogFooter>
          </>
        ) : (
          <>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Key className="h-5 w-5 text-primary" />
                API Key Created
              </DialogTitle>
              <DialogDescription>
                Copy and save this key now. You won't be able to see it again!
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <Alert variant="destructive">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  Make sure to copy your API key now. You will not be able to see it again!
                </AlertDescription>
              </Alert>

              <div className="space-y-2">
                <Label>Your API Key</Label>
                <div className="flex items-center gap-2">
                  <code className="flex-1 rounded-md bg-muted px-4 py-3 text-sm font-mono">
                    {createdKey}
                  </code>
                  <Button variant="outline" size="icon" onClick={handleCopy}>
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Key Name</Label>
                <p className="text-sm text-muted-foreground">{keyName}</p>
              </div>

              <div className="space-y-2">
                <Label>Permissions</Label>
                <div className="flex flex-wrap gap-1">
                  {selectedScopes.map((scopeId) => {
                    const scope = availableScopes.find((s) => s.id === scopeId);
                    return (
                      <span
                        key={scopeId}
                        className="rounded-md bg-secondary px-2 py-1 text-xs font-medium"
                      >
                        {scope?.label}
                      </span>
                    );
                  })}
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button onClick={handleClose}>Done</Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
