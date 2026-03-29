'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ApiKeyCard, ApiKey } from '@/components/api-key-card';
import { CreateKeyDialog } from '@/components/create-key-dialog';
import { Section } from '@/components/section';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Plus, Key, Info } from 'lucide-react';
import toast from 'react-hot-toast';

export default function ApiKeysPage() {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([
    {
      id: '1',
      name: 'Production Deployment Key',
      key: 'bp_prod_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6',
      scopes: ['deployments:read', 'deployments:write', 'projects:read'],
      created_at: '2024-01-15T10:30:00Z',
      last_used: '2024-03-01T15:45:00Z',
      usage_count: 1234,
    },
    {
      id: '2',
      name: 'Metrics Reader',
      key: 'bp_metrics_x9y8z7w6v5u4t3s2r1q0p9o8n7m6l5k4',
      scopes: ['metrics:read', 'logs:read'],
      created_at: '2024-02-20T14:20:00Z',
      last_used: '2024-03-05T09:15:00Z',
      usage_count: 567,
    },
  ]);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [revokingId, setRevokingId] = useState<string | null>(null);

  const handleRevokeKey = async (id: string) => {
    setRevokingId(id);
    try {
      // TODO: Replace with actual API call
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setApiKeys((keys) => keys.filter((key) => key.id !== id));
      toast.success('API key revoked successfully');
    } catch (_error) {
      toast.error('Failed to revoke API key');
    } finally {
      setRevokingId(null);
    }
  };

  const handleKeyCreated = (newKey: ApiKey) => {
    setApiKeys((keys) => [newKey, ...keys]);
  };

  return (
    <div className="space-y-6">
      <Section>
        <Alert>
          <Info className="h-4 w-4" />
          <AlertTitle>API Key Security</AlertTitle>
          <AlertDescription>
            API keys provide programmatic access to your account. Keep them secure and never share
            them in public repositories or client-side code. You can revoke keys at any time if
            they become compromised.
          </AlertDescription>
        </Alert>
      </Section>

      <Section>
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <CardTitle className="flex items-center gap-2">
                  <Key className="h-5 w-5" />
                  API Keys
                </CardTitle>
                <CardDescription>
                  Manage API keys for programmatic access to your resources
                </CardDescription>
              </div>
              <Button onClick={() => setShowCreateDialog(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Create New Key
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {apiKeys.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <div className="rounded-full bg-muted p-4 mb-4">
                  <Key className="h-8 w-8 text-muted-foreground" />
                </div>
                <h3 className="text-lg font-semibold mb-2">No API Keys</h3>
                <p className="text-sm text-muted-foreground mb-4 max-w-sm">
                  You haven't created any API keys yet. Create one to get started with
                  programmatic access.
                </p>
                <Button onClick={() => setShowCreateDialog(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Your First Key
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {apiKeys.map((apiKey) => (
                  <ApiKeyCard
                    key={apiKey.id}
                    apiKey={apiKey}
                    onRevoke={handleRevokeKey}
                    isRevoking={revokingId === apiKey.id}
                  />
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </Section>

      <Section>
        <Card>
          <CardHeader>
            <CardTitle>Best Practices</CardTitle>
            <CardDescription>Follow these guidelines to keep your API keys secure</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3 text-sm">
              <li className="flex items-start gap-3">
                <div className="rounded-full bg-primary/10 p-1 mt-0.5">
                  <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                </div>
                <div>
                  <strong className="font-medium">Use environment variables</strong> - Store API
                  keys in environment variables, never hardcode them in your source code
                </div>
              </li>
              <li className="flex items-start gap-3">
                <div className="rounded-full bg-primary/10 p-1 mt-0.5">
                  <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                </div>
                <div>
                  <strong className="font-medium">Principle of least privilege</strong> - Only
                  grant the minimum permissions required for each key
                </div>
              </li>
              <li className="flex items-start gap-3">
                <div className="rounded-full bg-primary/10 p-1 mt-0.5">
                  <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                </div>
                <div>
                  <strong className="font-medium">Rotate regularly</strong> - Create new keys and
                  revoke old ones periodically to maintain security
                </div>
              </li>
              <li className="flex items-start gap-3">
                <div className="rounded-full bg-primary/10 p-1 mt-0.5">
                  <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                </div>
                <div>
                  <strong className="font-medium">Monitor usage</strong> - Regularly review key
                  usage and revoke any keys that show suspicious activity
                </div>
              </li>
            </ul>
          </CardContent>
        </Card>
      </Section>

      <CreateKeyDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
        onKeyCreated={handleKeyCreated}
      />
    </div>
  );
}
