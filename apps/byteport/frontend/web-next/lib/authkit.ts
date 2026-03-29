const AUTHKIT_DOMAIN = process.env.NEXT_PUBLIC_AUTHKIT_DOMAIN;
const AUTHKIT_CLIENT_ID = process.env.NEXT_PUBLIC_AUTHKIT_CLIENT_ID;
const AUTHKIT_REDIRECT_URI = process.env.NEXT_PUBLIC_AUTHKIT_REDIRECT_URI;
const AUTHKIT_REQUIRED_SCOPES = process.env.NEXT_PUBLIC_AUTHKIT_SCOPES ?? 'openid profile email';
const AUTHKIT_AUDIENCE = process.env.NEXT_PUBLIC_AUTHKIT_AUDIENCE;

function ensureConfig() {
  if (!AUTHKIT_DOMAIN) {
    throw new Error('NEXT_PUBLIC_AUTHKIT_DOMAIN is not configured');
  }
  if (!AUTHKIT_CLIENT_ID) {
    throw new Error('NEXT_PUBLIC_AUTHKIT_CLIENT_ID is not configured');
  }
}

export function resolveRedirectUri(windowOverride?: Window): string {
  if (AUTHKIT_REDIRECT_URI) {
    return AUTHKIT_REDIRECT_URI;
  }
  if (typeof window === 'undefined') {
    return 'http://localhost:3000/auth/callback';
  }
  const target = windowOverride ?? window;
  return `${target.location.origin}/auth/callback`;
}

export function buildAuthkitAuthorizeUrl(state?: string) {
  ensureConfig();
  const redirectUri = resolveRedirectUri();
  const url = new URL('/oauth/authorize', AUTHKIT_DOMAIN);
  url.searchParams.set('client_id', AUTHKIT_CLIENT_ID as string);
  url.searchParams.set('response_type', 'code');
  url.searchParams.set('redirect_uri', redirectUri);
  url.searchParams.set('scope', AUTHKIT_REQUIRED_SCOPES);
  if (AUTHKIT_AUDIENCE) {
    url.searchParams.set('audience', AUTHKIT_AUDIENCE);
  }
  if (state) {
    url.searchParams.set('state', state);
  }
  return url.toString();
}

export interface WorkOSCallbackPayload {
  code: string;
  state?: string | null;
}
