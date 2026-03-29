import { getApiBaseUrl, getDeploymentApiBaseUrl } from './config';
import type { ProviderName, DeploymentStatus } from './types';

// ============================================================================
// API Configuration
// ============================================================================


export const API_CONFIG = {
  BASE_URL: getApiBaseUrl(),
  DEPLOYMENT_URL: getDeploymentApiBaseUrl(),
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
} as const;

// ============================================================================
// Refresh Intervals (in milliseconds)
// ============================================================================

export const REFRESH_INTERVALS = {
  DEPLOYMENTS: 5000, // 5 seconds
  METRICS: 10000, // 10 seconds
  LOGS: 2000, // 2 seconds
  STATS: 30000, // 30 seconds
  PROVIDERS: 60000, // 1 minute
  HOSTS: 15000, // 15 seconds
  COST: 300000, // 5 minutes
} as const;

// ============================================================================
// Provider Information
// ============================================================================

interface ProviderInfo {
  name: ProviderName;
  displayName: string;
  description: string;
  logo: string;
  color: string;
  backgroundColor: string;
  website: string;
  features: string[];
  pricing: {
    free: boolean;
    startingPrice?: string;
  };
}

export const PROVIDER_INFO: Record<ProviderName, ProviderInfo> = {
  vercel: {
    name: 'vercel',
    displayName: 'Vercel',
    description: 'Deploy web applications with zero configuration',
    logo: '/providers/vercel.svg',
    color: '#000000',
    backgroundColor: '#F5F5F5',
    website: 'https://vercel.com',
    features: ['Serverless', 'Edge Functions', 'CDN', 'Analytics'],
    pricing: {
      free: true,
      startingPrice: '$20/month',
    },
  },
  netlify: {
    name: 'netlify',
    displayName: 'Netlify',
    description: 'Build, deploy, and scale modern web projects',
    logo: '/providers/netlify.svg',
    color: '#00C7B7',
    backgroundColor: '#E6FAF8',
    website: 'https://netlify.com',
    features: ['JAMstack', 'Forms', 'Identity', 'Functions'],
    pricing: {
      free: true,
      startingPrice: '$19/month',
    },
  },
  render: {
    name: 'render',
    displayName: 'Render',
    description: 'Cloud application hosting for developers',
    logo: '/providers/render.svg',
    color: '#46E3B7',
    backgroundColor: '#E6FAF5',
    website: 'https://render.com',
    features: ['Docker', 'PostgreSQL', 'Redis', 'Background Jobs'],
    pricing: {
      free: true,
      startingPrice: '$7/month',
    },
  },
  railway: {
    name: 'railway',
    displayName: 'Railway',
    description: 'Infrastructure, instantly',
    logo: '/providers/railway.svg',
    color: '#0B0D0E',
    backgroundColor: '#F0F0F0',
    website: 'https://railway.app',
    features: ['Databases', 'Docker', 'Templates', 'Observability'],
    pricing: {
      free: true,
      startingPrice: '$5/month',
    },
  },
  fly: {
    name: 'fly',
    displayName: 'Fly.io',
    description: 'Deploy app servers close to your users',
    logo: '/providers/fly.svg',
    color: '#7B3FF2',
    backgroundColor: '#F3EBFF',
    website: 'https://fly.io',
    features: ['Global Edge', 'Containers', 'Machines', 'PostgreSQL'],
    pricing: {
      free: true,
      startingPrice: '$1.94/month',
    },
  },
  aws: {
    name: 'aws',
    displayName: 'AWS',
    description: 'Amazon Web Services - Comprehensive cloud platform',
    logo: '/providers/aws.svg',
    color: '#FF9900',
    backgroundColor: '#FFF5E6',
    website: 'https://aws.amazon.com',
    features: ['EC2', 'Lambda', 'S3', 'RDS', 'ECS'],
    pricing: {
      free: true,
      startingPrice: 'Pay as you go',
    },
  },
  gcp: {
    name: 'gcp',
    displayName: 'Google Cloud',
    description: 'Google Cloud Platform - Build with Google infrastructure',
    logo: '/providers/gcp.svg',
    color: '#4285F4',
    backgroundColor: '#E8F0FE',
    website: 'https://cloud.google.com',
    features: ['Compute Engine', 'Cloud Run', 'Cloud Functions', 'Cloud SQL'],
    pricing: {
      free: true,
      startingPrice: 'Pay as you go',
    },
  },
  azure: {
    name: 'azure',
    displayName: 'Microsoft Azure',
    description: 'Microsoft Azure - Cloud computing platform',
    logo: '/providers/azure.svg',
    color: '#0078D4',
    backgroundColor: '#E6F2FA',
    website: 'https://azure.microsoft.com',
    features: ['App Service', 'Functions', 'Container Instances', 'SQL Database'],
    pricing: {
      free: true,
      startingPrice: 'Pay as you go',
    },
  },
  supabase: {
    name: 'supabase',
    displayName: 'Supabase',
    description: 'The open source Firebase alternative',
    logo: '/providers/supabase.svg',
    color: '#3ECF8E',
    backgroundColor: '#E6FAF2',
    website: 'https://supabase.com',
    features: ['PostgreSQL', 'Auth', 'Storage', 'Edge Functions', 'Realtime'],
    pricing: {
      free: true,
      startingPrice: '$25/month',
    },
  },
};

// ============================================================================
// Status Colors
// ============================================================================

export const STATUS_COLORS: Record<DeploymentStatus, { text: string; bg: string; border: string }> = {
  pending: {
    text: 'text-yellow-700',
    bg: 'bg-yellow-50',
    border: 'border-yellow-200',
  },
  building: {
    text: 'text-blue-700',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
  },
  deploying: {
    text: 'text-indigo-700',
    bg: 'bg-indigo-50',
    border: 'border-indigo-200',
  },
  running: {
    text: 'text-green-700',
    bg: 'bg-green-50',
    border: 'border-green-200',
  },
  failed: {
    text: 'text-red-700',
    bg: 'bg-red-50',
    border: 'border-red-200',
  },
  terminated: {
    text: 'text-gray-700',
    bg: 'bg-gray-50',
    border: 'border-gray-200',
  },
};

export const STATUS_ICONS: Record<DeploymentStatus, string> = {
  pending: '⏳',
  building: '🔨',
  deploying: '🚀',
  running: '✅',
  failed: '❌',
  terminated: '⏹️',
};

// ============================================================================
// Log Level Colors
// ============================================================================

export const LOG_LEVEL_COLORS = {
  debug: {
    text: 'text-gray-600',
    bg: 'bg-gray-50',
  },
  info: {
    text: 'text-blue-600',
    bg: 'bg-blue-50',
  },
  warn: {
    text: 'text-yellow-600',
    bg: 'bg-yellow-50',
  },
  error: {
    text: 'text-red-600',
    bg: 'bg-red-50',
  },
  fatal: {
    text: 'text-red-900',
    bg: 'bg-red-100',
  },
} as const;

// ============================================================================
// Framework Detection Patterns
// ============================================================================

export const FRAMEWORK_PATTERNS = {
  nextjs: {
    files: ['next.config.js', 'next.config.mjs', 'next.config.ts'],
    packageJsonDeps: ['next'],
  },
  react: {
    files: ['src/App.jsx', 'src/App.tsx'],
    packageJsonDeps: ['react', 'react-dom'],
  },
  vue: {
    files: ['vue.config.js', 'src/App.vue'],
    packageJsonDeps: ['vue'],
  },
  svelte: {
    files: ['svelte.config.js', 'src/App.svelte'],
    packageJsonDeps: ['svelte'],
  },
  angular: {
    files: ['angular.json'],
    packageJsonDeps: ['@angular/core'],
  },
  nuxt: {
    files: ['nuxt.config.js', 'nuxt.config.ts'],
    packageJsonDeps: ['nuxt'],
  },
  gatsby: {
    files: ['gatsby-config.js'],
    packageJsonDeps: ['gatsby'],
  },
  astro: {
    files: ['astro.config.mjs', 'astro.config.js'],
    packageJsonDeps: ['astro'],
  },
} as const;

// ============================================================================
// Runtime Information
// ============================================================================

export const RUNTIME_INFO = {
  nodejs: {
    name: 'Node.js',
    versions: ['18.x', '20.x', '22.x'],
    defaultVersion: '20.x',
    icon: '⬢',
  },
  python: {
    name: 'Python',
    versions: ['3.9', '3.10', '3.11', '3.12'],
    defaultVersion: '3.11',
    icon: '🐍',
  },
  go: {
    name: 'Go',
    versions: ['1.20', '1.21', '1.22'],
    defaultVersion: '1.22',
    icon: '🐹',
  },
  rust: {
    name: 'Rust',
    versions: ['1.75', '1.76', '1.77'],
    defaultVersion: '1.77',
    icon: '🦀',
  },
  ruby: {
    name: 'Ruby',
    versions: ['3.0', '3.1', '3.2', '3.3'],
    defaultVersion: '3.3',
    icon: '💎',
  },
  php: {
    name: 'PHP',
    versions: ['8.1', '8.2', '8.3'],
    defaultVersion: '8.3',
    icon: '🐘',
  },
  docker: {
    name: 'Docker',
    versions: ['latest'],
    defaultVersion: 'latest',
    icon: '🐳',
  },
} as const;

// ============================================================================
// Default Values
// ============================================================================

export const DEFAULTS = {
  DEPLOYMENT_TIMEOUT: 600000, // 10 minutes
  LOG_TAIL_LINES: 100,
  METRICS_RETENTION_DAYS: 7,
  PAGE_SIZE: 20,
  MAX_RETRY_ATTEMPTS: 3,
  DEBOUNCE_DELAY: 300, // milliseconds
  TOAST_DURATION: 3000, // milliseconds
} as const;

// ============================================================================
// UI Constants
// ============================================================================

export const UI = {
  SIDEBAR_WIDTH: 280,
  HEADER_HEIGHT: 64,
  MOBILE_BREAKPOINT: 768,
  TABLET_BREAKPOINT: 1024,
  DESKTOP_BREAKPOINT: 1280,
} as const;

// ============================================================================
// Storage Keys
// ============================================================================

export const STORAGE_KEYS = {
  THEME: 'byteport_theme',
  SIDEBAR_STATE: 'byteport_sidebar',
  RECENT_DEPLOYMENTS: 'byteport_recent_deployments',
  USER_PREFERENCES: 'byteport_preferences',
  API_CACHE: 'byteport_api_cache',
} as const;

// ============================================================================
// Error Messages
// ============================================================================

export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  AUTH_ERROR: 'Authentication failed. Please log in again.',
  NOT_FOUND: 'Resource not found.',
  SERVER_ERROR: 'Server error. Please try again later.',
  VALIDATION_ERROR: 'Invalid input. Please check your data.',
  TIMEOUT: 'Request timed out. Please try again.',
  UNKNOWN: 'An unknown error occurred.',
} as const;

// ============================================================================
// Success Messages
// ============================================================================

export const SUCCESS_MESSAGES = {
  DEPLOYMENT_CREATED: 'Deployment created successfully',
  DEPLOYMENT_TERMINATED: 'Deployment terminated',
  DEPLOYMENT_RESTARTED: 'Deployment restarted',
  PROVIDER_CONNECTED: 'Provider connected successfully',
  PROVIDER_DISCONNECTED: 'Provider disconnected',
  HOST_REGISTERED: 'Host registered successfully',
  HOST_DELETED: 'Host deleted',
  SETTINGS_SAVED: 'Settings saved',
} as const;

// ============================================================================
// Metric Units
// ============================================================================

export const METRIC_UNITS = {
  CPU: '%',
  MEMORY: 'MB',
  NETWORK: 'MB/s',
  REQUESTS: 'req/s',
  RESPONSE_TIME: 'ms',
  ERROR_RATE: '%',
  UPTIME: '%',
} as const;

// ============================================================================
// Chart Colors
// ============================================================================

export const CHART_COLORS = {
  primary: '#3b82f6',
  secondary: '#8b5cf6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  info: '#06b6d4',
  cpu: '#3b82f6',
  memory: '#8b5cf6',
  network: '#10b981',
  requests: '#f59e0b',
} as const;
