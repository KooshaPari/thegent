const USE_LOCAL = process.env.NEXT_PUBLIC_USE_LOCAL === 'true';

const LOCAL_API_PORT = process.env.NEXT_PUBLIC_LOCAL_API_PORT ?? '8080';
const LOCAL_FRONTEND_PORT = process.env.NEXT_PUBLIC_LOCAL_FRONTEND_PORT ?? '3000';

const DEFAULT_API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'https://byte.kooshapari.com/api/v1';

function buildLocalApiUrl() {
  return `http://localhost:${LOCAL_API_PORT}/api/v1`;
}

export function getApiBaseUrl(windowOverride?: Window): string {
  if (USE_LOCAL) {
    return buildLocalApiUrl();
  }

  if (typeof window === 'undefined') {
    return DEFAULT_API_URL;
  }

  const target = windowOverride ?? window;

  const hasTauriInternals = (target as any).__TAURI_INTERNALS__;
  if (hasTauriInternals) {
    const platform = (target as any).__TAURI_INTERNALS__?.platform ?? 'desktop';
    switch (platform) {
      case 'android':
        return 'http://10.0.2.2:8080/api/v1';
      case 'windows':
        return buildLocalApiUrl();
      default:
        return buildLocalApiUrl();
    }
  }

  try {
    const url = new URL(target.location.href);
    if (url.hostname === 'localhost' || url.hostname === '127.0.0.1') {
      return buildLocalApiUrl();
    }
  } catch {
    // ignore and fall back to production URL
  }

  return DEFAULT_API_URL;
}

export function getDeploymentApiBaseUrl(): string {
  return getApiBaseUrl();
}

export function getRedirectUri(): string {
  if (USE_LOCAL) {
    return `http://localhost:${LOCAL_FRONTEND_PORT}/auth/callback`;
  }
  return process.env.NEXT_PUBLIC_WORKOS_REDIRECT_URI ?? 'https://byte.kooshapari.com/auth/callback';
}
