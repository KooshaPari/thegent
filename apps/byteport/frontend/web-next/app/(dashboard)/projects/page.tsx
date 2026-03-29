'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardHeader } from '@/components/layout/Header';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  GitBranch,
  ExternalLink,
  Rocket,
  Grid3x3,
  List,
  Plus,
  Clock,
  Activity,
  Search,
  Filter
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

type ViewMode = 'grid' | 'list';
type StatusFilter = 'all' | 'active' | 'inactive' | 'deploying';

interface Project {
  id: string;
  name: string;
  description: string;
  repositoryUrl: string;
  branch: string;
  deploymentCount: number;
  lastDeployedAt: string | null;
  status: 'active' | 'inactive' | 'deploying';
  framework?: string;
}

// Mock data - replace with actual API call
const MOCK_PROJECTS: Project[] = [
  {
    id: '1',
    name: 'BytePort Landing',
    description: 'Marketing website and documentation',
    repositoryUrl: 'https://github.com/byteport/landing',
    branch: 'main',
    deploymentCount: 42,
    lastDeployedAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    status: 'active',
    framework: 'Next.js'
  },
  {
    id: '2',
    name: 'API Gateway',
    description: 'Core API and authentication service',
    repositoryUrl: 'https://github.com/byteport/api-gateway',
    branch: 'main',
    deploymentCount: 128,
    lastDeployedAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    status: 'active',
    framework: 'FastAPI'
  },
  {
    id: '3',
    name: 'Analytics Dashboard',
    description: 'Real-time metrics and monitoring',
    repositoryUrl: 'https://github.com/byteport/analytics',
    branch: 'develop',
    deploymentCount: 67,
    lastDeployedAt: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    status: 'inactive',
    framework: 'React'
  },
  {
    id: '4',
    name: 'CLI Tool',
    description: 'Command-line interface for deployments',
    repositoryUrl: 'https://github.com/byteport/cli',
    branch: 'main',
    deploymentCount: 15,
    lastDeployedAt: null,
    status: 'inactive',
    framework: 'Go'
  }
];

export default function ProjectsPage() {
  const router = useRouter();
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [projects] = useState<Project[]>(MOCK_PROJECTS);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [frameworkFilter, setFrameworkFilter] = useState<string>('all');

  const filteredProjects = projects.filter((project) => {
    const matchesSearch =
      project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      project.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      project.repositoryUrl.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus = statusFilter === 'all' || project.status === statusFilter;

    const matchesFramework =
      frameworkFilter === 'all' || project.framework === frameworkFilter;

    return matchesSearch && matchesStatus && matchesFramework;
  });

  const frameworks = Array.from(new Set(projects.map((p) => p.framework).filter(Boolean)));

  const getStatusColor = (status: Project['status']) => {
    switch (status) {
      case 'active':
        return 'bg-green-500/10 text-green-500';
      case 'deploying':
        return 'bg-blue-500/10 text-blue-500';
      case 'inactive':
        return 'bg-gray-500/10 text-gray-500';
      default:
        return 'bg-gray-500/10 text-gray-500';
    }
  };

  const ProjectCard = ({ project }: { project: Project }) => (
    <Card className="group cursor-pointer transition-all hover:border-primary hover:shadow-lg">
      <div
        className="p-6"
        onClick={() => router.push(`/projects/${project.id}`)}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-semibold text-foreground group-hover:text-primary transition-colors">
                {project.name}
              </h3>
              <Badge className={getStatusColor(project.status)}>
                {project.status}
              </Badge>
            </div>
            <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
              {project.description}
            </p>
          </div>
        </div>

        <div className="mt-4 flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <GitBranch className="h-4 w-4" />
            <span>{project.branch}</span>
          </div>
          {project.framework && (
            <Badge variant="outline" className="text-xs">
              {project.framework}
            </Badge>
          )}
        </div>

        <div className="mt-4 flex items-center justify-between border-t pt-4">
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-1 text-muted-foreground">
              <Activity className="h-4 w-4" />
              <span>{project.deploymentCount} deployments</span>
            </div>
            {project.lastDeployedAt && (
              <div className="flex items-center gap-1 text-muted-foreground">
                <Clock className="h-4 w-4" />
                <span>{formatDistanceToNow(new Date(project.lastDeployedAt), { addSuffix: true })}</span>
              </div>
            )}
          </div>

          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={(e) => {
                e.stopPropagation();
                window.open(project.repositoryUrl, '_blank');
              }}
            >
              <ExternalLink className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                router.push(`/deploy?project=${project.id}`);
              }}
              disabled={project.status === 'deploying'}
            >
              <Rocket className="h-4 w-4 mr-1" />
              Deploy
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );

  const ProjectListItem = ({ project }: { project: Project }) => (
    <Card className="group cursor-pointer transition-all hover:border-primary">
      <div
        className="p-4"
        onClick={() => router.push(`/projects/${project.id}`)}
      >
        <div className="flex items-center justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="text-base font-semibold text-foreground group-hover:text-primary transition-colors truncate">
                {project.name}
              </h3>
              <Badge className={getStatusColor(project.status)} >
                {project.status}
              </Badge>
              {project.framework && (
                <Badge variant="outline" className="text-xs">
                  {project.framework}
                </Badge>
              )}
            </div>
            <p className="mt-1 text-sm text-muted-foreground truncate">
              {project.description}
            </p>
          </div>

          <div className="flex items-center gap-6 text-sm text-muted-foreground">
            <div className="flex items-center gap-1">
              <GitBranch className="h-4 w-4" />
              <span className="hidden md:inline">{project.branch}</span>
            </div>

            <div className="flex items-center gap-1">
              <Activity className="h-4 w-4" />
              <span className="hidden sm:inline">{project.deploymentCount}</span>
            </div>

            {project.lastDeployedAt && (
              <div className="flex items-center gap-1 min-w-[120px]">
                <Clock className="h-4 w-4" />
                <span className="hidden lg:inline">
                  {formatDistanceToNow(new Date(project.lastDeployedAt), { addSuffix: true })}
                </span>
              </div>
            )}
          </div>

          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={(e) => {
                e.stopPropagation();
                window.open(project.repositoryUrl, '_blank');
              }}
            >
              <ExternalLink className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                router.push(`/deploy?project=${project.id}`);
              }}
              disabled={project.status === 'deploying'}
            >
              <Rocket className="h-4 w-4 mr-1" />
              <span className="hidden sm:inline">Deploy</span>
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <DashboardHeader
        title="Projects"
        subtitle={`${filteredProjects.length} of ${projects.length} ${projects.length === 1 ? 'project' : 'projects'}`}
        action={
          <div className="flex items-center gap-2">
            <div className="hidden md:flex items-center gap-1 border rounded-lg p-1">
              <Button
                size="sm"
                variant={viewMode === 'grid' ? 'secondary' : 'ghost'}
                onClick={() => setViewMode('grid')}
              >
                <Grid3x3 className="h-4 w-4" />
              </Button>
              <Button
                size="sm"
                variant={viewMode === 'list' ? 'secondary' : 'ghost'}
                onClick={() => setViewMode('list')}
              >
                <List className="h-4 w-4" />
              </Button>
            </div>
            <Button onClick={() => router.push('/projects/new')}>
              <Plus className="h-4 w-4 mr-2" />
              New Project
            </Button>
          </div>
        }
      />

      <section className="flex-1 overflow-y-auto px-6 py-8">
        {/* Search and Filters */}
        <div className="mb-6 space-y-4">
          <div className="flex flex-col gap-4 md:flex-row md:items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search projects by name, description, or repository..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
                className="h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="deploying">Deploying</option>
              </select>

              <select
                value={frameworkFilter}
                onChange={(e) => setFrameworkFilter(e.target.value)}
                className="h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              >
                <option value="all">All Frameworks</option>
                {frameworks.map((framework) => (
                  <option key={framework} value={framework}>
                    {framework}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {(searchQuery || statusFilter !== 'all' || frameworkFilter !== 'all') && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span>Active filters:</span>
              {searchQuery && (
                <Badge variant="secondary">
                  Search: {searchQuery}
                </Badge>
              )}
              {statusFilter !== 'all' && (
                <Badge variant="secondary">
                  Status: {statusFilter}
                </Badge>
              )}
              {frameworkFilter !== 'all' && (
                <Badge variant="secondary">
                  Framework: {frameworkFilter}
                </Badge>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSearchQuery('');
                  setStatusFilter('all');
                  setFrameworkFilter('all');
                }}
                className="h-auto p-1 text-xs"
              >
                Clear all
              </Button>
            </div>
          )}
        </div>

        {filteredProjects.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="rounded-full bg-muted p-6 mb-4">
              <GitBranch className="h-12 w-12 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-semibold mb-2">
              {projects.length === 0 ? 'No projects yet' : 'No projects found'}
            </h3>
            <p className="text-muted-foreground mb-6 text-center max-w-md">
              {projects.length === 0
                ? 'Get started by creating your first project and connecting it to a Git repository.'
                : 'Try adjusting your search or filter criteria.'}
            </p>
            {projects.length === 0 && (
              <Button onClick={() => router.push('/projects/new')}>
                <Plus className="h-4 w-4 mr-2" />
                Create Project
              </Button>
            )}
          </div>
        ) : (
          <div className={
            viewMode === 'grid'
              ? 'grid gap-6 md:grid-cols-2 lg:grid-cols-3'
              : 'flex flex-col gap-4'
          }>
            {filteredProjects.map((project) =>
              viewMode === 'grid' ? (
                <ProjectCard key={project.id} project={project} />
              ) : (
                <ProjectListItem key={project.id} project={project} />
              )
            )}
          </div>
        )}
      </section>
    </div>
  );
}
