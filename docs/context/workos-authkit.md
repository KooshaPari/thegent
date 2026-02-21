# WorkOS AuthKit Context

> Definitive reference for WorkOS AuthKit — hosted and embedded authentication UI plus the WorkOS Python SDK for user management.
> Sources: workos.com/docs/authkit, workos.com/docs/user-management/vanilla/python, workos.com/docs/sdks/python, github.com/workos/authkit-nextjs, github.com/workos/python-authkit-example (fetched 2026-02-20).

---

## What is AuthKit

**AuthKit** is WorkOS's authentication layer built on top of the WorkOS User Management API. It provides:

1. **Hosted AuthKit** — Redirect users to a WorkOS-hosted sign-in page (zero frontend UI work)
2. **Embedded Components** — React components for rendering sign-in/sign-up forms in your own UI
3. **Python SDK** — Server-side session management, user lookup, org membership, SSO, MFA

AuthKit sits on top of **WorkOS User Management**, which is the REST API and SDK layer for managing users, organizations, SSO connections, and directory sync. AuthKit specifically refers to the auth UI and session flow; User Management refers to the underlying CRUD/admin API.

**Distinction: AuthKit vs WorkOS User Management**

| Layer | Purpose | SDK Entry Point |
|-------|---------|-----------------|
| AuthKit | Sign-in/sign-up UI flows, session cookies | `workos.user_management.get_authorization_url()` |
| User Management | CRUD: users, orgs, memberships, invitations | `workos.user_management.*` |
| SSO | SAML/OIDC enterprise connections | `workos.sso.*` |
| Directory Sync | SCIM provisioning | `workos.directory_sync.*` |

**thegent Use Case:** AuthKit authenticates thegent dashboard users and CLI operators; the Python SDK validates sessions on protected routes; WorkOS manages org-level isolation for multi-tenant agent workspaces.

---

## Key Concepts

| Term | Definition |
|------|-----------|
| **Sealed session** | Encrypted JWT stored in HTTP-only cookie; encrypted with `WORKOS_COOKIE_PASSWORD` |
| **Authorization URL** | WorkOS-hosted sign-in page URL; generated server-side, user redirected here |
| **Code exchange** | OAuth callback: exchange `code` param for access/refresh tokens and user info |
| **Organization** | A WorkOS entity grouping users; maps to a customer/tenant |
| **SSO Connection** | SAML/OIDC identity provider (IdP) linked to an organization |
| **MFA enrollment** | Per-user MFA devices; enforced via AuthKit automatically when enabled |
| **Cookie password** | 32+ character string used as HMAC key to encrypt session cookies |
| **Admin Portal** | WorkOS-hosted UI for org admins to manage SSO, Directory Sync, Audit Log |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `WORKOS_API_KEY` | Yes | Server-side API key (`sk_live_...` or `sk_test_...`) |
| `WORKOS_CLIENT_ID` | Yes | Application client ID (`default_org_...`) |
| `WORKOS_COOKIE_PASSWORD` | Yes | 32+ char string for cookie encryption |
| `WORKOS_REDIRECT_URI` | Yes | OAuth callback URL registered in WorkOS dashboard |

**Generate cookie password:**
```bash
openssl rand -hex 16   # Returns 32-char hex string
python3 -c "import secrets; print(secrets.token_hex(16))"
```

---

## Installation

### Python SDK

```bash
pip install workos
# Current stable: workos >= 5.40.0
```

### Node.js / Next.js SDK

```bash
npm install @workos-inc/authkit-nextjs
bun add @workos-inc/authkit-nextjs
```

### React Components (Embedded)

```bash
npm install @workos-inc/authkit-react
bun add @workos-inc/authkit-react
```

---

## Python SDK: WorkOSClient

### Initialization

```python
import os
from workos import WorkOSClient

workos = WorkOSClient(
    api_key=os.getenv("WORKOS_API_KEY"),
    client_id=os.getenv("WORKOS_CLIENT_ID"),
)
```

### Authentication Flow (Authorization Code)

**Step 1: Generate authorization URL**

```python
# Generate the WorkOS-hosted sign-in page URL
authorization_url = workos.user_management.get_authorization_url(
    provider="authkit",           # Use AuthKit hosted UI
    redirect_uri="http://localhost:3000/callback",
    # Optional: pre-select organization for SSO
    organization_id="org_01ARZ...",
    # Optional: pass state for CSRF protection
    state="random_csrf_token",
)
# Redirect user to this URL
```

**Step 2: Handle callback — exchange code for session**

```python
from flask import request, redirect, make_response

cookie_password = os.getenv("WORKOS_COOKIE_PASSWORD")

@app.route("/callback")
def callback():
    code = request.args.get("code")

    # Exchange code for sealed session (encrypted cookie value)
    auth_response = workos.user_management.authenticate_with_code(
        code=code,
        session={
            "seal_session": True,
            "cookie_password": cookie_password,
        },
    )

    # auth_response.sealed_session  → encrypted string to store in cookie
    # auth_response.user            → User object
    # auth_response.access_token    → raw access token (if needed)
    # auth_response.refresh_token   → raw refresh token

    response = make_response(redirect("/dashboard"))
    response.set_cookie(
        "wos-session",
        auth_response.sealed_session,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=60 * 60 * 24 * 7,  # 7 days
    )
    return response
```

**Step 3: Validate session on protected routes**

```python
from workos.user_management import AuthenticationResponse, SessionStatus

@app.route("/dashboard")
def dashboard():
    sealed_session = request.cookies.get("wos-session")
    if not sealed_session:
        return redirect("/login")

    # Load and authenticate sealed session
    session = workos.user_management.load_sealed_session(
        sealed_session=sealed_session,
        cookie_password=cookie_password,
    )

    auth_result = session.authenticate()
    # auth_result.authenticated: bool
    # auth_result.reason: str (why failed, if not authenticated)
    # auth_result.user: User | None
    # auth_result.session_id: str

    if not auth_result.authenticated:
        return redirect("/login")

    user = auth_result.user
    return f"Hello, {user.email}"
```

**Step 4: Refresh session**

```python
# Call when session is approaching expiry or after role changes
result = session.refresh()
# Returns new sealed_session; update cookie with new value

new_response = make_response(redirect("/dashboard"))
new_response.set_cookie("wos-session", result.sealed_session, ...)
```

**Step 5: Sign out**

```python
@app.route("/logout")
def logout():
    sealed_session = request.cookies.get("wos-session")
    session = workos.user_management.load_sealed_session(
        sealed_session=sealed_session,
        cookie_password=cookie_password,
    )

    # Get WorkOS logout URL (invalidates server-side session)
    logout_url = session.get_logout_url()

    response = make_response(redirect(logout_url))
    response.delete_cookie("wos-session")
    return response
```

---

## Python SDK: Key Methods Reference

### `workos.user_management`

| Method | Description | Returns |
|--------|-------------|---------|
| `get_authorization_url(provider, redirect_uri, ...)` | Generate hosted sign-in URL | `str` |
| `authenticate_with_code(code, session=...)` | Exchange OAuth code for tokens/session | `AuthenticationResponse` |
| `load_sealed_session(sealed_session, cookie_password)` | Deserialize sealed cookie | `Session` |
| `get_user(user_id)` | Fetch user by ID | `User` |
| `list_users(email=None, organization_id=None, limit=10)` | List users with filters | `ListUsersResponse` |
| `create_user(email, password=None, first_name=None, ...)` | Programmatically create user | `User` |
| `update_user(user_id, first_name=None, ...)` | Update user attributes | `User` |
| `delete_user(user_id)` | Delete user | `None` |
| `list_organization_memberships(user_id=None, organization_id=None)` | List org memberships | `ListMembershipsResponse` |
| `create_organization_membership(user_id, organization_id, role_slug=None)` | Add user to org | `OrganizationMembership` |
| `send_invitation(email, organization_id=None)` | Invite user by email | `Invitation` |
| `authenticate_with_magic_auth(code, email)` | Magic link code exchange | `AuthenticationResponse` |
| `send_magic_auth_code(email)` | Send magic link | `None` |
| `enroll_auth_factor(user_id, type="totp")` | Enroll MFA factor | `EnrollAuthFactorResponse` |
| `verify_auth_factor(auth_factor_id, code)` | Verify MFA code | `VerifyAuthFactorResponse` |

### `Session` object methods

| Method | Description | Returns |
|--------|-------------|---------|
| `session.authenticate()` | Validate and return auth info | `SessionAuthentication` |
| `session.refresh()` | Refresh tokens, return new sealed session | `RefreshSessionResponse` |
| `session.get_logout_url()` | Get WorkOS logout URL | `str` |

### `AuthenticationResponse` fields

```python
auth_response.user              # User object
auth_response.organization_id   # str | None
auth_response.access_token      # str (raw JWT)
auth_response.refresh_token     # str (raw refresh)
auth_response.sealed_session    # str (encrypted; store as cookie)
```

### `User` object fields

```python
user.id                   # "user_01ARZ..."
user.email                # "alice@example.com"
user.email_verified       # bool
user.first_name           # str | None
user.last_name            # str | None
user.profile_picture_url  # str | None
user.created_at           # datetime
user.updated_at           # datetime
user.external_id          # str | None (SCIM or external mapping)
```

---

## SSO (SAML / OIDC) Integration

### SSO Authorization URL

```python
# For org-specific SSO (SAML/OIDC IdP)
authorization_url = workos.user_management.get_authorization_url(
    provider="authkit",
    redirect_uri="http://localhost:3000/callback",
    organization_id="org_01ARZ...",  # Required for SSO
)
```

WorkOS automatically routes to the correct IdP (SAML/OIDC) based on the organization's SSO connection. After SAML assertion, WorkOS creates/updates the WorkOS user and issues tokens.

### SSO Connection Management

```python
# List SSO connections for an org
connections = workos.sso.list_connections(
    organization_id="org_01ARZ...",
    limit=20,
)
for conn in connections.data:
    print(conn.id, conn.provider, conn.status)  # "active" | "inactive" | "draft"
```

---

## Webhook Events

WorkOS sends webhooks for auth events. Register webhook endpoint in the WorkOS dashboard.

### Webhook Verification

```python
from workos import WorkOSClient

workos = WorkOSClient(api_key=os.getenv("WORKOS_API_KEY"))

@app.route("/webhooks/workos", methods=["POST"])
def handle_webhook():
    payload = request.data.decode("utf-8")
    signature = request.headers.get("WorkOS-Signature")
    webhook_secret = os.getenv("WORKOS_WEBHOOK_SECRET")

    try:
        event = workos.webhooks.construct_event(
            payload=payload,
            sig_header=signature,
            secret=webhook_secret,
            tolerance=180,  # seconds
        )
    except Exception as e:
        return {"error": str(e)}, 400

    # event.event: str (event type)
    # event.data: dict (payload)
    handle_event(event)
    return {"received": True}, 200
```

### Key Webhook Events

| Event | Trigger |
|-------|---------|
| `user.created` | New user registered |
| `user.updated` | User profile changed |
| `user.deleted` | User removed |
| `session.created` | New session started |
| `connection.activated` | SSO connection enabled |
| `dsync.user.created` | SCIM-provisioned user |
| `dsync.user.updated` | SCIM user attribute change |
| `invitation.accepted` | User accepted org invite |

---

## Admin Portal

The Admin Portal is a WorkOS-hosted UI for end customers (org admins) to configure their own SSO, Directory Sync, and Audit Log settings without code.

```python
# Generate Admin Portal link for an organization
portal_link = workos.portal.generate_link(
    organization="org_01ARZ...",
    intent="sso",           # "sso" | "dsync" | "audit_logs" | "log_streams"
    return_url="https://app.example.com/settings",
    success_url="https://app.example.com/settings/success",
)
# portal_link.link → URL to redirect org admin to
```

---

## Node.js / Next.js SDK (authkit-nextjs)

### Setup

```typescript
// lib/auth.ts
import { authkit } from '@workos-inc/authkit-nextjs';

export const { getSession, withAuth } = authkit({
    clientId: process.env.WORKOS_CLIENT_ID!,
    clientSecret: process.env.WORKOS_CLIENT_SECRET!,
    apiKeySecret: process.env.WORKOS_API_KEY!,
    redirectUri: process.env.WORKOS_REDIRECT_URI!,
    cookiePassword: process.env.WORKOS_COOKIE_PASSWORD!,
    cookieMaxAge: 60 * 60 * 24 * 7,  // 7 days (default)
});
```

### Middleware Protection

```typescript
// middleware.ts
import { authkitMiddleware } from '@workos-inc/authkit-nextjs';

export default authkitMiddleware({
    publicRoutes: ['/', '/login', '/signup', '/api/public/*'],
});

export const config = {
    matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
```

### Server Components

```typescript
// app/dashboard/page.tsx
import { getSession } from '@/lib/auth';
import { redirect } from 'next/navigation';

export default async function Dashboard() {
    const session = await getSession();
    if (!session) redirect('/login');

    return <h1>Hello {session.user.email}</h1>;
}
```

### React Embedded Components

```tsx
// Embedded sign-in form (no redirect to WorkOS UI)
import { SignIn } from '@workos-inc/authkit-react';

export function LoginPage() {
    return <SignIn />;
}
```

---

## Authentication

WorkOS API uses Bearer token authentication on all server-side calls:

```
Authorization: Bearer sk_live_...
```

Rate limits: Not publicly documented; contact WorkOS for enterprise limits. Use exponential backoff on 429 responses.

---

## 2026 Beta / Recent Features (as of 2026-02-20)

- **Python AuthKit example app** — Official sample at `github.com/workos/python-authkit-example` using Flask + sealed sessions
- **Composable Middleware (Node)** — `authkitMiddleware` supports custom proxy helpers for auth composition
- **TokenRefreshError Enhancement** — Now includes `userId` and `sessionId` fields for debugging
- **Next.js 15 parity** — Full App Router, Server Actions, and React 19 support
- **Python SDK v5.40+** — Latest stable; `workos >= 5.40.0` in trace project

---

## thegent / trace Integration

- **trace project**: `workos>=5.40.0` in `pyproject.toml`; `@workos-inc/authkit-react@^0.16.0` in web app frontend
- **thegent**: WorkOS manages dashboard user auth and org-level access isolation
- **Pattern**: Python backend uses `WorkOSClient` + sealed sessions; Next.js frontend uses `authkit-nextjs` with middleware

---

## Known Issues / Gotchas

1. **Cookie password length**: Must be exactly 32+ characters; shorter values cause silent decryption failures at runtime.
2. **Sealed session expiry**: `session.authenticate()` returns `authenticated=False` with reason `"session_expired"` when the session has expired; always check `auth_result.reason`.
3. **SSO requires organization_id**: `get_authorization_url()` without `organization_id` shows generic AuthKit UI; SSO routing only activates when org is specified.
4. **Webhook tolerance**: Default tolerance is 180 seconds; clock skew > 3 minutes causes webhook rejections.
5. **Multiple org memberships**: A user can belong to multiple organizations; `session.authenticate()` returns the active session's org only — use `list_organization_memberships()` to get all.
6. **Python SDK vs Node SDK parity**: Python SDK `authenticate_with_code()` is the equivalent of Node's `handleAuth()`; both produce sealed sessions.

---

## Sources & References

- **WorkOS AuthKit (Python)**: https://workos.com/docs/authkit/vanilla/python (fetched 2026-02-20)
- **WorkOS User Management (Python)**: https://workos.com/docs/user-management/vanilla/python (fetched 2026-02-20)
- **WorkOS Python SDK Docs**: https://workos.com/docs/sdks/python (fetched 2026-02-20)
- **WorkOS API Reference**: https://workos.com/docs/reference (fetched 2026-02-20)
- **authkit-nextjs GitHub**: https://github.com/workos/authkit-nextjs (fetched 2026-02-20)
- **python-authkit-example**: https://github.com/workos/python-authkit-example (fetched 2026-02-20)
- **authkit-react npm**: `@workos-inc/authkit-react@^0.16.0`
- **Last Verified**: 2026-02-20

See also: `docs/context/workos.md` (enterprise SSO/SCIM reference)

---

## Quick Reference

| Item | Value |
|------|-------|
| Python package | `workos >= 5.40.0` |
| Node package | `@workos-inc/authkit-nextjs` |
| React package | `@workos-inc/authkit-react` |
| Auth pattern | Authorization Code + Sealed Session Cookie |
| Cookie encryption | HMAC-SHA256 with 32+ char `WORKOS_COOKIE_PASSWORD` |
| Session TTL | 7 days default (configurable) |
| Base API URL | `https://api.workos.com` |
| Auth header | `Authorization: Bearer $WORKOS_API_KEY` |
| Webhook header | `WorkOS-Signature` |

### Quick Python Session Flow

```python
# 1. Redirect to AuthKit
url = workos.user_management.get_authorization_url(
    provider="authkit", redirect_uri=REDIRECT_URI)
redirect(url)

# 2. Exchange code (in /callback)
auth = workos.user_management.authenticate_with_code(
    code=code, session={"seal_session": True, "cookie_password": COOKIE_PWD})
set_cookie("wos-session", auth.sealed_session)

# 3. Validate on each request
session = workos.user_management.load_sealed_session(
    sealed_session=cookie, cookie_password=COOKIE_PWD)
result = session.authenticate()
if not result.authenticated:
    redirect("/login")
user = result.user
```

### Common Patterns

- **SSO**: Pass `organization_id` to `get_authorization_url()`; WorkOS routes to correct IdP
- **Refresh**: Call `session.refresh()` when `auth_result.reason == "session_expired"`
- **Logout**: `session.get_logout_url()` → redirect → delete cookie
- **Webhooks**: Verify with `workos.webhooks.construct_event(payload, sig, secret, tolerance=180)`
