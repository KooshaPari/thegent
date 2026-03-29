'use client';

import { useState } from 'react';
import { DashboardHeader } from '@/components/layout/Header';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Search,
  BookOpen,
  Zap,
  Code,
  Terminal,
  Settings,
  Rocket,
  GitBranch,
  Shield,
  ChevronRight,
  ExternalLink,
  Copy,
  CheckCircle2,
  LucideIcon
} from 'lucide-react';

interface DocSection {
  id: string;
  title: string;
  icon: LucideIcon;
  description: string;
  category: 'getting-started' | 'guides' | 'api' | 'advanced';
  content: string;
  examples?: CodeExample[];
}

interface CodeExample {
  title: string;
  language: string;
  code: string;
}

const DOCUMENTATION: DocSection[] = [
  {
    id: 'quick-start',
    title: 'Quick Start Guide',
    icon: Zap,
    category: 'getting-started',
    description: 'Get up and running with BytePort in minutes',
    content: `# Quick Start Guide

Welcome to BytePort! This guide will help you deploy your first application in just a few minutes.

## Prerequisites

- A Git repository with your application code
- A BytePort account (sign up at byteport.dev)
- Basic knowledge of your application's tech stack

## Step 1: Connect Your Repository

1. Navigate to the Projects page
2. Click "New Project"
3. Select your Git provider (GitHub, GitLab, or Custom)
4. Enter your repository URL
5. Choose your default branch (usually 'main' or 'master')

## Step 2: Configure Your Project

1. Give your project a descriptive name
2. Add a brief description (optional)
3. Select your framework/runtime
4. Upload an NVMS configuration file (optional)
5. Enable or disable automatic deployments

## Step 3: Deploy

1. Click "Create Project" to finalize setup
2. Navigate to your project's detail page
3. Click "Deploy Now" to trigger your first deployment
4. Monitor the deployment progress in real-time

## Next Steps

- Set up environment variables for your application
- Configure custom domains
- Set up monitoring and alerts
- Explore advanced deployment options`,
    examples: [
      {
        title: 'Example NVMS Configuration',
        language: 'yaml',
        code: `name: my-app
version: 1.0.0
runtime: nodejs-18
build:
  command: npm run build
  output: dist
deploy:
  type: static
  provider: aws
  region: us-east-1
environment:
  NODE_ENV: production`
      }
    ]
  },
  {
    id: 'projects',
    title: 'Managing Projects',
    icon: GitBranch,
    category: 'guides',
    description: 'Learn how to create and manage your projects',
    content: `# Managing Projects

Projects in BytePort represent your applications and their deployment configurations.

## Creating a Project

Projects are created through a three-step wizard:

### Step 1: Repository Connection
- Choose your Git provider
- Provide the repository URL
- Select the default branch

### Step 2: Configuration
- Set project name and description
- Choose framework/runtime
- Upload NVMS configuration (optional)
- Configure auto-deployment settings

### Step 3: Review
- Verify all settings
- Create the project

## Project Settings

### Environment Variables
Manage environment variables that will be injected into your deployments:
- Add/remove variables
- Mark variables as secret
- Copy values securely

### Git Integration
- View connection status
- Update repository URL
- Reconnect if needed

### Deployment Settings
- Configure build commands
- Set deployment triggers
- Manage deployment branches

## Archiving and Deleting Projects

### Archive
- Temporarily disable a project
- Keep all data and history
- Can be restored later

### Delete
- Permanently remove a project
- Deletes all associated deployments
- Cannot be undone`,
    examples: [
      {
        title: 'Environment Variables Setup',
        language: 'bash',
        code: `# Set environment variables via CLI
byteport env set DATABASE_URL="postgresql://..."
byteport env set API_KEY="sk-..." --secret

# List all environment variables
byteport env list

# Remove an environment variable
byteport env unset API_KEY`
      }
    ]
  },
  {
    id: 'deployments',
    title: 'Deployments',
    icon: Rocket,
    category: 'guides',
    description: 'Deploy and manage your applications',
    content: `# Deployments

Deployments are instances of your application running on BytePort infrastructure.

## Triggering Deployments

### Manual Deployment
1. Navigate to your project
2. Click "Deploy Now"
3. Select branch and commit (optional)
4. Monitor deployment progress

### Automatic Deployment
Enable automatic deployments to deploy on every push:
- Configure in project settings
- Specify branches to watch
- Set up deployment hooks

## Deployment Lifecycle

1. **Building** - Source code is fetched and built
2. **Deploying** - Application is deployed to infrastructure
3. **Running** - Application is live and serving traffic
4. **Failed** - Deployment encountered an error
5. **Terminated** - Deployment has been stopped

## Monitoring Deployments

### Real-time Logs
- View build and runtime logs
- Filter by severity
- Search log content
- Export logs for analysis

### Metrics
- CPU usage
- Memory consumption
- Network traffic
- Request rates
- Error rates

### Alerts
Set up alerts for:
- Deployment failures
- High resource usage
- Error rate thresholds
- Downtime incidents`,
    examples: [
      {
        title: 'Deploy via CLI',
        language: 'bash',
        code: `# Deploy latest commit from main branch
byteport deploy --project=my-app

# Deploy specific commit
byteport deploy --project=my-app --commit=abc123

# Deploy with environment override
byteport deploy --project=my-app --env=staging

# Watch deployment progress
byteport deploy --project=my-app --follow`
      }
    ]
  },
  {
    id: 'api-reference',
    title: 'API Reference',
    icon: Code,
    category: 'api',
    description: 'Complete API documentation for BytePort',
    content: `# API Reference

The BytePort API provides programmatic access to all platform features.

## Authentication

All API requests require authentication via API key:

\`\`\`
Authorization: Bearer YOUR_API_KEY
\`\`\`

Get your API key from Settings > API Keys.

## Base URL

\`\`\`
https://api.byteport.dev/v1
\`\`\`

## Rate Limits

- 1000 requests per hour for standard plans
- 5000 requests per hour for pro plans
- Rate limit headers included in responses

## Projects API

### List Projects
\`\`\`
GET /projects
\`\`\`

### Create Project
\`\`\`
POST /projects
\`\`\`

### Get Project
\`\`\`
GET /projects/:id
\`\`\`

### Update Project
\`\`\`
PATCH /projects/:id
\`\`\`

### Delete Project
\`\`\`
DELETE /projects/:id
\`\`\`

## Deployments API

### List Deployments
\`\`\`
GET /deployments
\`\`\`

### Create Deployment
\`\`\`
POST /deployments
\`\`\`

### Get Deployment
\`\`\`
GET /deployments/:id
\`\`\`

### Get Deployment Logs
\`\`\`
GET /deployments/:id/logs
\`\`\`

### Get Deployment Metrics
\`\`\`
GET /deployments/:id/metrics
\`\`\``,
    examples: [
      {
        title: 'Create Project via API',
        language: 'javascript',
        code: `const response = await fetch('https://api.byteport.dev/v1/projects', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'My App',
    repository_url: 'https://github.com/user/repo',
    branch: 'main',
    framework: 'nextjs',
    auto_deploy: true
  })
});

const project = await response.json();
console.log('Project created:', project.id);`
      },
      {
        title: 'List Deployments',
        language: 'python',
        code: `import requests

headers = {
    'Authorization': 'Bearer YOUR_API_KEY'
}

response = requests.get(
    'https://api.byteport.dev/v1/deployments',
    headers=headers,
    params={'project_id': 'proj_123', 'limit': 10}
)

deployments = response.json()
for deployment in deployments['data']:
    print(f"{deployment['id']}: {deployment['status']}")`
      }
    ]
  },
  {
    id: 'cli-reference',
    title: 'CLI Reference',
    icon: Terminal,
    category: 'api',
    description: 'Command-line interface documentation',
    content: `# CLI Reference

The BytePort CLI provides a powerful command-line interface for managing your deployments.

## Installation

\`\`\`bash
# Using npm
npm install -g @byteport/cli

# Using yarn
yarn global add @byteport/cli

# Using homebrew (macOS)
brew install byteport
\`\`\`

## Authentication

\`\`\`bash
# Login interactively
byteport login

# Login with API key
byteport login --api-key YOUR_API_KEY
\`\`\`

## Commands

### Projects

\`\`\`bash
# List all projects
byteport projects list

# Create a new project
byteport projects create

# View project details
byteport projects info <project-id>

# Delete a project
byteport projects delete <project-id>
\`\`\`

### Deployments

\`\`\`bash
# Deploy a project
byteport deploy --project=<project-id>

# List deployments
byteport deployments list

# View deployment logs
byteport logs <deployment-id>

# View deployment metrics
byteport metrics <deployment-id>

# Stop a deployment
byteport deployments stop <deployment-id>
\`\`\`

### Environment Variables

\`\`\`bash
# List environment variables
byteport env list --project=<project-id>

# Set an environment variable
byteport env set KEY=value --project=<project-id>

# Set a secret environment variable
byteport env set KEY=value --secret --project=<project-id>

# Delete an environment variable
byteport env unset KEY --project=<project-id>
\`\`\``,
    examples: [
      {
        title: 'Complete Deployment Workflow',
        language: 'bash',
        code: `# Login to BytePort
byteport login

# Create a new project
byteport projects create \\
  --name "My App" \\
  --repo "https://github.com/user/repo" \\
  --branch "main"

# Set environment variables
byteport env set DATABASE_URL="postgresql://..." --secret
byteport env set NODE_ENV="production"

# Deploy the project
byteport deploy --follow

# View logs
byteport logs --tail 100

# Check metrics
byteport metrics --duration 1h`
      }
    ]
  },
  {
    id: 'nvms-config',
    title: 'NVMS Configuration',
    icon: Settings,
    category: 'advanced',
    description: 'Advanced configuration with NVMS files',
    content: `# NVMS Configuration

NVMS (Network Virtual Machine Specification) files provide advanced configuration for your deployments.

## File Format

NVMS files can be written in YAML or JSON format.

## Structure

\`\`\`yaml
name: string          # Project name
version: string       # Configuration version
runtime: string       # Runtime environment
build:
  command: string     # Build command
  output: string      # Build output directory
  env: object        # Build environment variables
deploy:
  type: string       # Deployment type (static, server, container)
  provider: string   # Cloud provider
  region: string     # Deployment region
  instances: number  # Number of instances
  scaling:
    min: number      # Minimum instances
    max: number      # Maximum instances
    target_cpu: number # Target CPU percentage
environment:
  object             # Runtime environment variables
health:
  path: string       # Health check endpoint
  interval: number   # Check interval in seconds
  timeout: number    # Timeout in seconds
\`\`\`

## Examples

### Static Site
\`\`\`yaml
name: my-static-site
version: 1.0.0
runtime: static
build:
  command: npm run build
  output: dist
deploy:
  type: static
  provider: aws
  region: us-east-1
\`\`\`

### Node.js Server
\`\`\`yaml
name: my-api
version: 1.0.0
runtime: nodejs-18
build:
  command: npm run build
  output: dist
deploy:
  type: server
  provider: aws
  region: us-east-1
  instances: 2
  scaling:
    min: 1
    max: 5
    target_cpu: 70
environment:
  NODE_ENV: production
  PORT: 3000
health:
  path: /health
  interval: 30
  timeout: 5
\`\`\``,
    examples: [
      {
        title: 'Full NVMS Configuration Example',
        language: 'yaml',
        code: `name: production-api
version: 2.0.0
runtime: nodejs-18

build:
  command: npm ci && npm run build
  output: dist
  env:
    NODE_ENV: production

deploy:
  type: server
  provider: aws
  region: us-east-1
  instances: 3
  scaling:
    min: 2
    max: 10
    target_cpu: 75
    target_memory: 80

environment:
  NODE_ENV: production
  PORT: 3000
  LOG_LEVEL: info

health:
  path: /api/health
  interval: 30
  timeout: 5
  healthy_threshold: 2
  unhealthy_threshold: 3

networking:
  ports:
    - 3000
  domains:
    - api.example.com
  ssl: true

resources:
  cpu: 2
  memory: 4096
  disk: 20480

monitoring:
  enabled: true
  metrics:
    - cpu
    - memory
    - requests
  alerts:
    - type: error_rate
      threshold: 5
      duration: 300`
      }
    ]
  },
  {
    id: 'security',
    title: 'Security Best Practices',
    icon: Shield,
    category: 'advanced',
    description: 'Secure your deployments and data',
    content: `# Security Best Practices

Follow these guidelines to keep your deployments secure.

## API Keys

- Never commit API keys to source control
- Rotate keys regularly (every 90 days)
- Use separate keys for different environments
- Revoke unused keys immediately
- Use read-only keys when possible

## Environment Variables

- Mark sensitive values as secrets
- Never log secret values
- Use separate variables for each environment
- Rotate secrets regularly
- Audit who has access to secrets

## Network Security

- Enable HTTPS for all deployments
- Use SSL certificates from trusted providers
- Configure CORS policies appropriately
- Implement rate limiting
- Use IP allowlisting when possible

## Access Control

- Follow principle of least privilege
- Use role-based access control
- Enable multi-factor authentication
- Review access logs regularly
- Revoke access for departed team members

## Compliance

- Enable audit logging
- Regular security reviews
- Keep dependencies updated
- Follow industry standards (SOC2, GDPR, etc.)
- Implement data retention policies

## Monitoring

- Set up security alerts
- Monitor for unusual activity
- Review deployment logs
- Track failed authentication attempts
- Monitor resource usage for anomalies`,
    examples: [
      {
        title: 'Secure Environment Setup',
        language: 'bash',
        code: `# Use secret management for sensitive values
byteport env set DB_PASSWORD="..." --secret
byteport env set API_KEY="..." --secret

# Use read-only API keys for CI/CD
byteport api-keys create \\
  --name "CI/CD Key" \\
  --scope "read" \\
  --expires "90d"

# Enable audit logging
byteport settings update \\
  --audit-logging enabled \\
  --log-retention 90d`
      }
    ]
  }
];

export default function DocsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedDoc, setSelectedDoc] = useState<DocSection | null>(DOCUMENTATION[0]);
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const filteredDocs = DOCUMENTATION.filter((doc) => {
    const matchesSearch =
      doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.content.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesCategory =
      selectedCategory === 'all' || doc.category === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  const categories = [
    { id: 'all', label: 'All Docs' },
    { id: 'getting-started', label: 'Getting Started' },
    { id: 'guides', label: 'Guides' },
    { id: 'api', label: 'API Reference' },
    { id: 'advanced', label: 'Advanced' },
  ];

  const handleCopyCode = (code: string, id: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <DashboardHeader
        title="Documentation"
        subtitle="Learn how to build and deploy with BytePort"
        action={
          <Button
            variant="outline"
            onClick={() => window.open('https://byteport.dev/docs', '_blank')}
          >
            <ExternalLink className="h-4 w-4 mr-2" />
            Full Documentation
          </Button>
        }
      />

      <section className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div className="w-80 border-r border-border bg-muted/30">
          <div className="p-4 space-y-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search documentation..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Category Filter */}
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <Badge
                  key={category.id}
                  variant={selectedCategory === category.id ? 'default' : 'outline'}
                  className="cursor-pointer"
                  onClick={() => setSelectedCategory(category.id)}
                >
                  {category.label}
                </Badge>
              ))}
            </div>
          </div>

          {/* Doc List */}
          <ScrollArea className="h-[calc(100vh-250px)]">
            <div className="p-4 space-y-1">
              {filteredDocs.map((doc) => (
                <button
                  key={doc.id}
                  onClick={() => setSelectedDoc(doc)}
                  className={`w-full text-left rounded-lg p-3 transition-colors ${
                    selectedDoc?.id === doc.id
                      ? 'bg-primary text-primary-foreground'
                      : 'hover:bg-muted'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <doc.icon className="h-5 w-5 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">{doc.title}</div>
                      <div className={`text-xs mt-1 line-clamp-2 ${
                        selectedDoc?.id === doc.id
                          ? 'text-primary-foreground/80'
                          : 'text-muted-foreground'
                      }`}>
                        {doc.description}
                      </div>
                    </div>
                    <ChevronRight className="h-4 w-4 flex-shrink-0" />
                  </div>
                </button>
              ))}

              {filteredDocs.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <BookOpen className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  <p className="text-sm">No documentation found</p>
                  <p className="text-xs mt-1">Try adjusting your search</p>
                </div>
              )}
            </div>
          </ScrollArea>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto">
          {selectedDoc ? (
            <div className="p-8 max-w-4xl mx-auto">
              <div className="mb-6">
                <div className="flex items-center gap-3 mb-2">
                  <selectedDoc.icon className="h-8 w-8 text-primary" />
                  <h1 className="text-3xl font-bold">{selectedDoc.title}</h1>
                </div>
                <p className="text-muted-foreground">{selectedDoc.description}</p>
              </div>

              {/* Main Content */}
              <Card className="p-6 mb-6">
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  {selectedDoc.content.split('\n').map((line, idx) => {
                    if (line.startsWith('# ')) {
                      return (
                        <h1 key={idx} className="text-2xl font-bold mt-6 mb-4">
                          {line.substring(2)}
                        </h1>
                      );
                    }
                    if (line.startsWith('## ')) {
                      return (
                        <h2 key={idx} className="text-xl font-semibold mt-5 mb-3">
                          {line.substring(3)}
                        </h2>
                      );
                    }
                    if (line.startsWith('### ')) {
                      return (
                        <h3 key={idx} className="text-lg font-medium mt-4 mb-2">
                          {line.substring(4)}
                        </h3>
                      );
                    }
                    if (line.startsWith('```')) {
                      return null; // Skip code fence markers
                    }
                    if (line.trim() === '') {
                      return <br key={idx} />;
                    }
                    if (line.startsWith('- ')) {
                      return (
                        <li key={idx} className="ml-4">
                          {line.substring(2)}
                        </li>
                      );
                    }
                    return (
                      <p key={idx} className="mb-2">
                        {line}
                      </p>
                    );
                  })}
                </div>
              </Card>

              {/* Code Examples */}
              {selectedDoc.examples && selectedDoc.examples.length > 0 && (
                <div className="space-y-4">
                  <h2 className="text-2xl font-bold">Examples</h2>
                  {selectedDoc.examples.map((example, idx) => (
                    <Card key={idx} className="overflow-hidden">
                      <div className="flex items-center justify-between bg-muted px-4 py-3 border-b">
                        <div className="flex items-center gap-2">
                          <Code className="h-4 w-4" />
                          <span className="font-medium">{example.title}</span>
                          <Badge variant="outline" className="text-xs">
                            {example.language}
                          </Badge>
                        </div>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleCopyCode(example.code, `${selectedDoc.id}-${idx}`)}
                        >
                          {copiedCode === `${selectedDoc.id}-${idx}` ? (
                            <>
                              <CheckCircle2 className="h-4 w-4 mr-2 text-green-500" />
                              Copied
                            </>
                          ) : (
                            <>
                              <Copy className="h-4 w-4 mr-2" />
                              Copy
                            </>
                          )}
                        </Button>
                      </div>
                      <div className="p-4 bg-slate-950 text-slate-50">
                        <pre className="text-sm overflow-x-auto">
                          <code>{example.code}</code>
                        </pre>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <BookOpen className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                <h2 className="text-2xl font-semibold mb-2">Select a documentation topic</h2>
                <p className="text-muted-foreground">
                  Choose a topic from the sidebar to get started
                </p>
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
