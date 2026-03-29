'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardHeader } from '@/components/layout/Header';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import {
  GitBranch,
  ExternalLink,
  Rocket,
  Trash2,
  Archive,
  Plus,
  Eye,
  EyeOff,
  Copy,
  CheckCircle2,
  Clock,
  GitCommit
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface Deployment {
  id: string;
  commit: string;
  branch: string;
  status: 'success' | 'failed' | 'building' | 'cancelled';
  createdAt: string;
  duration?: number;
}

interface EnvironmentVariable {
  id: string;
  key: string;
  value: string;
  isSecret: boolean;
}

export default function ProjectDetailPage({ params }: any) {
  const router = useRouter();
  const [showSecrets, setShowSecrets] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [envVars, setEnvVars] = useState<EnvironmentVariable[]>([
    { id: '1', key: 'DATABASE_URL', value: 'postgresql://...', isSecret: true },
    { id: '2', key: 'API_KEY', value: 'sk-...', isSecret: true },
    { id: '3', key: 'NODE_ENV', value: 'production', isSecret: false },
  ]);
  const [newEnvKey, setNewEnvKey] = useState('');
  const [newEnvValue, setNewEnvValue] = useState('');
  const [newEnvIsSecret, setNewEnvIsSecret] = useState(true);

  // Mock data - replace with actual API call using params.id
  const project = {
    id: params.id,
    name: 'BytePort Landing',
    description: 'Marketing website and documentation',
    repositoryUrl: 'https://github.com/byteport/landing',
    branch: 'main',
    deploymentCount: 42,
    lastDeployedAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    status: 'active' as const,
    framework: 'Next.js',
    gitConnected: true,
  };

  const deployments: Deployment[] = [
    {
      id: '1',
      commit: 'abc1234',
      branch: 'main',
      status: 'success',
      createdAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
      duration: 125,
    },
    {
      id: '2',
      commit: 'def5678',
      branch: 'main',
      status: 'success',
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
      duration: 110,
    },
    {
      id: '3',
      commit: '9gh0123',
      branch: 'develop',
      status: 'failed',
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
      duration: 45,
    },
  ];

  const getStatusColor = (status: Deployment['status']) => {
    switch (status) {
      case 'success':
        return 'bg-green-500/10 text-green-500';
      case 'failed':
        return 'bg-red-500/10 text-red-500';
      case 'building':
        return 'bg-blue-500/10 text-blue-500';
      case 'cancelled':
        return 'bg-gray-500/10 text-gray-500';
      default:
        return 'bg-gray-500/10 text-gray-500';
    }
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleAddEnvVar = () => {
    if (!newEnvKey || !newEnvValue) return;

    const newVar: EnvironmentVariable = {
      id: Date.now().toString(),
      key: newEnvKey,
      value: newEnvValue,
      isSecret: newEnvIsSecret,
    };

    setEnvVars([...envVars, newVar]);
    setNewEnvKey('');
    setNewEnvValue('');
    setNewEnvIsSecret(true);
  };

  const handleDeleteEnvVar = (id: string) => {
    setEnvVars(envVars.filter(v => v.id !== id));
  };

  const handleArchiveProject = () => {
    // TODO: Implement archive logic
    console.log('Archiving project:', params.id);
    router.push('/projects');
  };

  const handleDeleteProject = () => {
    // TODO: Implement delete logic
    console.log('Deleting project:', params.id);
    router.push('/projects');
  };

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <DashboardHeader
        title={project.name}
        subtitle={project.description}
        action={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={() => window.open(project.repositoryUrl, '_blank')}
            >
              <GitBranch className="h-4 w-4 mr-2" />
              Repository
            </Button>
            <Button onClick={() => router.push(`/deploy?project=${params.id}`)}>
              <Rocket className="h-4 w-4 mr-2" />
              Deploy Now
            </Button>
          </div>
        }
      />

      <section className="flex-1 overflow-y-auto px-6 py-8">
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="deployments">Deployments</TabsTrigger>
            <TabsTrigger value="environment">Environment</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2">
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Project Information</h3>
                <dl className="space-y-3">
                  <div>
                    <dt className="text-sm text-muted-foreground">Framework</dt>
                    <dd className="text-sm font-medium">{project.framework}</dd>
                  </div>
                  <div>
                    <dt className="text-sm text-muted-foreground">Default Branch</dt>
                    <dd className="text-sm font-medium flex items-center gap-2">
                      <GitBranch className="h-4 w-4" />
                      {project.branch}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm text-muted-foreground">Total Deployments</dt>
                    <dd className="text-sm font-medium">{project.deploymentCount}</dd>
                  </div>
                  <div>
                    <dt className="text-sm text-muted-foreground">Last Deployed</dt>
                    <dd className="text-sm font-medium">
                      {project.lastDeployedAt
                        ? formatDistanceToNow(new Date(project.lastDeployedAt), { addSuffix: true })
                        : 'Never'}
                    </dd>
                  </div>
                </dl>
              </Card>

              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Git Integration</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Status</span>
                    <Badge className={project.gitConnected ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}>
                      {project.gitConnected ? 'Connected' : 'Disconnected'}
                    </Badge>
                  </div>
                  <div>
                    <Label className="text-sm text-muted-foreground">Repository URL</Label>
                    <div className="mt-1 flex items-center gap-2">
                      <Input
                        value={project.repositoryUrl}
                        readOnly
                        className="flex-1"
                      />
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => window.open(project.repositoryUrl, '_blank')}
                      >
                        <ExternalLink className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  {!project.gitConnected && (
                    <Button className="w-full">
                      <GitBranch className="h-4 w-4 mr-2" />
                      Reconnect Repository
                    </Button>
                  )}
                </div>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="deployments" className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Deployment History</h3>
              <Button onClick={() => router.push(`/deploy?project=${params.id}`)}>
                <Plus className="h-4 w-4 mr-2" />
                New Deployment
              </Button>
            </div>

            <div className="space-y-3">
              {deployments.map((deployment) => (
                <Card
                  key={deployment.id}
                  className="p-4 cursor-pointer hover:border-primary transition-colors"
                  onClick={() => router.push(`/deployments/${deployment.id}`)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <Badge className={getStatusColor(deployment.status)}>
                        {deployment.status}
                      </Badge>
                      <div>
                        <div className="flex items-center gap-2">
                          <GitCommit className="h-4 w-4 text-muted-foreground" />
                          <span className="font-mono text-sm">{deployment.commit}</span>
                          <span className="text-sm text-muted-foreground">on {deployment.branch}</span>
                        </div>
                        <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          {formatDistanceToNow(new Date(deployment.createdAt), { addSuffix: true })}
                          {deployment.duration && (
                            <span>• {deployment.duration}s</span>
                          )}
                        </div>
                      </div>
                    </div>
                    <Button variant="ghost" size="sm">
                      View Details
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="environment" className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold">Environment Variables</h3>
                <p className="text-sm text-muted-foreground">
                  Manage environment variables for your deployments
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowSecrets(!showSecrets)}
              >
                {showSecrets ? (
                  <>
                    <EyeOff className="h-4 w-4 mr-2" />
                    Hide Values
                  </>
                ) : (
                  <>
                    <Eye className="h-4 w-4 mr-2" />
                    Show Values
                  </>
                )}
              </Button>
            </div>

            <Card className="p-6">
              <div className="space-y-4">
                {envVars.map((envVar) => (
                  <div key={envVar.id} className="flex items-center gap-4 p-3 border rounded-lg">
                    <div className="flex-1 grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-xs text-muted-foreground">Key</Label>
                        <p className="font-mono text-sm">{envVar.key}</p>
                      </div>
                      <div>
                        <Label className="text-xs text-muted-foreground">Value</Label>
                        <p className="font-mono text-sm">
                          {envVar.isSecret && !showSecrets
                            ? '••••••••••••••••'
                            : envVar.value}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleCopy(envVar.id, envVar.value)}
                      >
                        {copiedId === envVar.id ? (
                          <CheckCircle2 className="h-4 w-4 text-green-500" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                      </Button>
                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button size="sm" variant="ghost">
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>Delete environment variable?</AlertDialogTitle>
                            <AlertDialogDescription>
                              This will remove {envVar.key} from all future deployments.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                            <AlertDialogAction onClick={() => handleDeleteEnvVar(envVar.id)}>
                              Delete
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </div>
                  </div>
                ))}

                <div className="border-t pt-4 mt-4">
                  <h4 className="text-sm font-semibold mb-3">Add New Variable</h4>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <Label htmlFor="env-key">Key</Label>
                      <Input
                        id="env-key"
                        placeholder="API_KEY"
                        value={newEnvKey}
                        onChange={(e) => setNewEnvKey(e.target.value)}
                      />
                    </div>
                    <div>
                      <Label htmlFor="env-value">Value</Label>
                      <Input
                        id="env-value"
                        type={newEnvIsSecret ? 'password' : 'text'}
                        placeholder="Enter value"
                        value={newEnvValue}
                        onChange={(e) => setNewEnvValue(e.target.value)}
                      />
                    </div>
                  </div>
                  <div className="flex items-center justify-between mt-4">
                    <label className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={newEnvIsSecret}
                        onChange={(e) => setNewEnvIsSecret(e.target.checked)}
                        className="rounded"
                      />
                      Mark as secret
                    </label>
                    <Button onClick={handleAddEnvVar} disabled={!newEnvKey || !newEnvValue}>
                      <Plus className="h-4 w-4 mr-2" />
                      Add Variable
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="settings" className="space-y-6">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Project Settings</h3>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="project-name">Project Name</Label>
                  <Input id="project-name" defaultValue={project.name} />
                </div>
                <div>
                  <Label htmlFor="project-description">Description</Label>
                  <Input id="project-description" defaultValue={project.description} />
                </div>
                <div>
                  <Label htmlFor="project-branch">Default Branch</Label>
                  <Input id="project-branch" defaultValue={project.branch} />
                </div>
                <Button>Save Changes</Button>
              </div>
            </Card>

            <Card className="p-6 border-destructive/50">
              <h3 className="text-lg font-semibold mb-4 text-destructive">Danger Zone</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border border-destructive/20 rounded-lg">
                  <div>
                    <h4 className="font-medium">Archive Project</h4>
                    <p className="text-sm text-muted-foreground">
                      Mark this project as archived. You can restore it later.
                    </p>
                  </div>
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="outline">
                        <Archive className="h-4 w-4 mr-2" />
                        Archive
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Archive this project?</AlertDialogTitle>
                        <AlertDialogDescription>
                          The project will be hidden but can be restored later.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction onClick={handleArchiveProject}>
                          Archive Project
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </div>

                <div className="flex items-center justify-between p-4 border border-destructive/20 rounded-lg">
                  <div>
                    <h4 className="font-medium text-destructive">Delete Project</h4>
                    <p className="text-sm text-muted-foreground">
                      Permanently delete this project and all its deployments. This cannot be undone.
                    </p>
                  </div>
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="destructive">
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                        <AlertDialogDescription>
                          This will permanently delete the project &quot;{project.name}&quot; and all its deployments.
                          This action cannot be undone.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                          onClick={handleDeleteProject}
                          className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        >
                          Delete Project
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </div>
              </div>
            </Card>
          </TabsContent>
        </Tabs>
      </section>
    </div>
  );
}
