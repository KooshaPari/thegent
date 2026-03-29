import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { formatDistance, formatDistanceToNow, format, isValid, parseISO } from 'date-fns';
import { DeploymentStatus, ProviderStatus, HostStatus } from './types';
import { STATUS_COLORS, STATUS_ICONS } from './constants';

// ============================================================================
// Tailwind CSS Class Utilities
// ============================================================================

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// ============================================================================
// Date Formatting
// ============================================================================

export function formatDate(date: string | Date, formatStr: string = 'PPpp'): string {
  try {
    const d = typeof date === 'string' ? parseISO(date) : date;
    if (!isValid(d)) return 'Invalid date';
    return format(d, formatStr);
  } catch {
    return 'Invalid date';
  }
}

export function formatDateShort(date: string | Date): string {
  return formatDate(date, 'MMM d, yyyy');
}

export function formatDateTime(date: string | Date): string {
  return formatDate(date, 'MMM d, yyyy h:mm a');
}

export function formatTimeAgo(date: string | Date): string {
  try {
    const d = typeof date === 'string' ? parseISO(date) : date;
    if (!isValid(d)) return 'Invalid date';
    return formatDistanceToNow(d, { addSuffix: true });
  } catch {
    return 'Invalid date';
  }
}

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  if (ms < 3600000) return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`;
  const hours = Math.floor(ms / 3600000);
  const minutes = Math.floor((ms % 3600000) / 60000);
  return `${hours}h ${minutes}m`;
}

export function formatRelativeTime(from: string | Date, to: string | Date): string {
  try {
    const fromDate = typeof from === 'string' ? parseISO(from) : from;
    const toDate = typeof to === 'string' ? parseISO(to) : to;
    if (!isValid(fromDate) || !isValid(toDate)) return 'Invalid date';
    return formatDistance(fromDate, toDate);
  } catch {
    return 'Invalid date';
  }
}

// ============================================================================
// Number Formatting
// ============================================================================

export function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-US').format(num);
}

export function formatCompactNumber(num: number): string {
  return new Intl.NumberFormat('en-US', {
    notation: 'compact',
    compactDisplay: 'short',
  }).format(num);
}

export function formatPercentage(value: number, decimals: number = 1): string {
  return `${value.toFixed(decimals)}%`;
}

// ============================================================================
// Currency Formatting
// ============================================================================

export function formatCurrency(amount: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatCost(amount: number): string {
  if (amount === 0) return '$0.00';
  if (amount < 0.01) return '<$0.01';
  if (amount < 1) return `$${amount.toFixed(3)}`;
  return formatCurrency(amount);
}

// ============================================================================
// Byte Formatting
// ============================================================================

export function formatBytes(bytes: number, decimals: number = 2): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

export function formatBytesPerSecond(bytesPerSec: number): string {
  return `${formatBytes(bytesPerSec)}/s`;
}

export function parseBytesString(str: string): number {
  const match = str.match(/^(\d+(?:\.\d+)?)\s*([KMGT]?B)$/i);
  if (!match) return 0;

  const value = parseFloat(match[1]);
  const unit = match[2].toUpperCase();
  const units: Record<string, number> = {
    B: 1,
    KB: 1024,
    MB: 1024 ** 2,
    GB: 1024 ** 3,
    TB: 1024 ** 4,
  };

  return value * (units[unit] || 1);
}

// ============================================================================
// String Utilities
// ============================================================================

export function truncate(str: string, maxLength: number, suffix: string = '...'): string {
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength - suffix.length) + suffix;
}

export function slugify(str: string): string {
  return str
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export function capitalizeWords(str: string): string {
  return str
    .split(' ')
    .map((word) => capitalize(word))
    .join(' ');
}

export function camelToTitle(str: string): string {
  return str
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, (s) => s.toUpperCase())
    .trim();
}

// ============================================================================
// Clipboard Utilities
// ============================================================================

export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      const result = document.execCommand('copy');
      textArea.remove();
      return result;
    }
  } catch (error) {
    console.error('Failed to copy to clipboard:', error);
    return false;
  }
}

export async function readFromClipboard(): Promise<string | null> {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      return await navigator.clipboard.readText();
    }
    return null;
  } catch (error) {
    console.error('Failed to read from clipboard:', error);
    return null;
  }
}

// ============================================================================
// Validation Utilities
// ============================================================================

export function isValidUrl(str: string): boolean {
  try {
    new URL(str);
    return true;
  } catch {
    return false;
  }
}

export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function isValidGitUrl(url: string): boolean {
  const gitUrlRegex =
    /^(https?:\/\/)?([\w.-]+@)?[\w.-]+[:/][\w.-]+\/[\w.-]+(\.git)?$/;
  return gitUrlRegex.test(url);
}

// ============================================================================
// Array Utilities
// ============================================================================

export function unique<T>(arr: T[]): T[] {
  return Array.from(new Set(arr));
}

export function groupBy<T>(arr: T[], key: keyof T): Record<string, T[]> {
  return arr.reduce(
    (groups, item) => {
      const groupKey = String(item[key]);
      if (!groups[groupKey]) {
        groups[groupKey] = [];
      }
      groups[groupKey].push(item);
      return groups;
    },
    {} as Record<string, T[]>
  );
}

export function sortBy<T>(arr: T[], key: keyof T, order: 'asc' | 'desc' = 'asc'): T[] {
  return [...arr].sort((a, b) => {
    const aVal = a[key];
    const bVal = b[key];
    if (aVal < bVal) return order === 'asc' ? -1 : 1;
    if (aVal > bVal) return order === 'asc' ? 1 : -1;
    return 0;
  });
}

// ============================================================================
// Object Utilities
// ============================================================================

export function pick<T extends object, K extends keyof T>(
  obj: T,
  keys: K[]
): Pick<T, K> {
  const result = {} as Pick<T, K>;
  keys.forEach((key) => {
    if (key in obj) {
      result[key] = obj[key];
    }
  });
  return result;
}

export function omit<T extends object, K extends keyof T>(
  obj: T,
  keys: K[]
): Omit<T, K> {
  const result = { ...obj };
  keys.forEach((key) => {
    delete result[key];
  });
  return result;
}

export function deepMerge<T extends object>(target: T, source: Partial<T>): T {
  const output = { ...target };
  if (isObject(target) && isObject(source)) {
    Object.keys(source).forEach((key) => {
      const sourceValue = source[key as keyof T];
      const targetValue = target[key as keyof T];
      if (isObject(sourceValue) && isObject(targetValue)) {
        (output as any)[key] = deepMerge(targetValue as any, sourceValue as any);
      } else {
        (output as any)[key] = sourceValue;
      }
    });
  }
  return output;
}

function isObject(item: any): item is object {
  return item && typeof item === 'object' && !Array.isArray(item);
}

// ============================================================================
// Color Utilities
// ============================================================================

export function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
}

export function getContrastColor(hex: string): 'light' | 'dark' {
  const rgb = hexToRgb(hex);
  if (!rgb) return 'dark';

  // Calculate relative luminance
  const luminance = (0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b) / 255;
  return luminance > 0.5 ? 'dark' : 'light';
}

// ============================================================================
// Debounce & Throttle
// ============================================================================

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

// ============================================================================
// Random Utilities
// ============================================================================

export function generateId(length: number = 8): string {
  return Math.random()
    .toString(36)
    .substring(2, 2 + length);
}

export function randomFromArray<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

// ============================================================================
// Storage Utilities
// ============================================================================

export function safeLocalStorage() {
  const isAvailable = (() => {
    try {
      const test = '__storage_test__';
      localStorage.setItem(test, test);
      localStorage.removeItem(test);
      return true;
    } catch {
      return false;
    }
  })();

  return {
    getItem: (key: string): string | null => {
      if (!isAvailable) return null;
      try {
        return localStorage.getItem(key);
      } catch {
        return null;
      }
    },
    setItem: (key: string, value: string): void => {
      if (!isAvailable) return;
      try {
        localStorage.setItem(key, value);
      } catch {}
    },
    removeItem: (key: string): void => {
      if (!isAvailable) return;
      try {
        localStorage.removeItem(key);
      } catch {}
    },
    clear: (): void => {
      if (!isAvailable) return;
      try {
        localStorage.clear();
      } catch {}
    },
  };
}

// ============================================================================
// Status Utilities
// ============================================================================

export function getStatusColor(status: DeploymentStatus): { text: string; bg: string; border: string } {
  return STATUS_COLORS[status] || STATUS_COLORS.pending;
}

export function getStatusIcon(status: DeploymentStatus): string {
  return STATUS_ICONS[status] || STATUS_ICONS.pending;
}

export function getProviderStatusColor(status: ProviderStatus): string {
  const colors: Record<ProviderStatus, string> = {
    connected: 'text-green-600',
    disconnected: 'text-gray-600',
    error: 'text-red-600',
    pending: 'text-yellow-600',
  };
  return colors[status] || colors.disconnected;
}

export function getHostStatusColor(status: HostStatus): string {
  const colors: Record<HostStatus, string> = {
    online: 'text-green-600',
    offline: 'text-gray-600',
    degraded: 'text-yellow-600',
    maintenance: 'text-blue-600',
  };
  return colors[status] || colors.offline;
}

export function getHostStatusBadge(status: HostStatus): { text: string; bg: string; border: string } {
  const badges: Record<HostStatus, { text: string; bg: string; border: string }> = {
    online: {
      text: 'text-green-700',
      bg: 'bg-green-50',
      border: 'border-green-200',
    },
    offline: {
      text: 'text-gray-700',
      bg: 'bg-gray-50',
      border: 'border-gray-200',
    },
    degraded: {
      text: 'text-yellow-700',
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
    },
    maintenance: {
      text: 'text-blue-700',
      bg: 'bg-blue-50',
      border: 'border-blue-200',
    },
  };
  return badges[status] || badges.offline;
}

export function getProviderStatusBadge(status: ProviderStatus): { text: string; bg: string; border: string } {
  const badges: Record<ProviderStatus, { text: string; bg: string; border: string }> = {
    connected: {
      text: 'text-green-700',
      bg: 'bg-green-50',
      border: 'border-green-200',
    },
    disconnected: {
      text: 'text-gray-700',
      bg: 'bg-gray-50',
      border: 'border-gray-200',
    },
    error: {
      text: 'text-red-700',
      bg: 'bg-red-50',
      border: 'border-red-200',
    },
    pending: {
      text: 'text-yellow-700',
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
    },
  };
  return badges[status] || badges.disconnected;
}
