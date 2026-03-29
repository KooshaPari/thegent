'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Copy, Eye, EyeOff, Trash2 } from 'lucide-react';
import { formatDate } from '@/lib/utils';
import toast from 'react-hot-toast';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger
} from '@/components/ui/alert-dialog';

export interface ApiKey {
  id: string;
  name: string;
  key: string;
  scopes: string[];
  created_at: string;
  last_used?: string;
  usage_count?: number;
}

interface ApiKeyCardProps {
  apiKey: ApiKey;
  onRevoke?: (id: string) => void;
  isRevoking?: boolean;
}

export function ApiKeyCard({ apiKey, onRevoke, isRevoking = false }: ApiKeyCardProps) {
  const [showKey, setShowKey] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(apiKey.key);
      toast.success('API key copied to clipboard');
    } catch (_error) {
      toast.error('Failed to copy API key');
    }
  };

  const maskedKey = apiKey.key.slice(0, 8) + '...' + apiKey.key.slice(-4);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="text-base">{apiKey.name}</CardTitle>
            <CardDescription className="text-xs">
              Created {formatDate(apiKey.created_at)}
            </CardDescription>
          </div>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-destructive"
                disabled={isRevoking}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Revoke API Key</AlertDialogTitle>
                <AlertDialogDescription>
                  Are you sure you want to revoke this API key? This action cannot be undone and
                  any applications using this key will immediately lose access.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction
                  onClick={() => onRevoke?.(apiKey.id)}
                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                >
                  Revoke
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <code className="flex-1 rounded bg-muted px-3 py-2 text-sm font-mono">
              {showKey ? apiKey.key : maskedKey}
            </code>
            <Button variant="ghost" size="icon" onClick={() => setShowKey(!showKey)}>
              {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </Button>
            <Button variant="ghost" size="icon" onClick={handleCopy}>
              <Copy className="h-4 w-4" />
            </Button>
          </div>

          <div className="flex flex-wrap gap-1">
            {apiKey.scopes.map((scope) => (
              <Badge key={scope} variant="secondary" className="text-xs">
                {scope}
              </Badge>
            ))}
          </div>

          {(apiKey.last_used || apiKey.usage_count !== undefined) && (
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              {apiKey.last_used && (
                <span>Last used: {formatDate(apiKey.last_used)}</span>
              )}
              {apiKey.usage_count !== undefined && (
                <span>{apiKey.usage_count} requests</span>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
