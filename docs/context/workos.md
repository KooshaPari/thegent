# WorkOS API Context

> Definitive reference for implementing WorkOS enterprise auth and directory features for thegent multi-tenant deployments.
> Sources: workos.com/docs (fetched 2026-02-20).

---

## What is WorkOS

WorkOS is an enterprise-focused authentication and identity management platform providing single sign-on (SSO), directory sync, admin portals, audit logs, and user management—enabling applications to become enterprise-ready without building custom enterprise IAM.

**Key capabilities:**
- **Single Sign-On (SSO):** SAML and OIDC support for any organization's identity provider
- **Directory Sync:** Provision users/groups from Google Workspace, Microsoft Entra ID, and other SCIM providers
- **Admin Portal:** Hosted UI for IT admins to configure SSO/Directory Sync without vendor support
- **User Management:** AuthKit for password and magic link authentication
- **Audit Logs:** Track identity and access events for compliance
- **Organizations:** Multi-tenant organization management with domain verification

**Pricing (2026):** $125/month per SSO connection; $125/month per Directory Sync connection.

---

## Core Concepts

### Organizations

An **organization** represents a customer/tenant in your application. WorkOS associates connections, users, and domains with organizations.

```
Organization
├── Domains (verified)
├── Connections
│   ├── SSO (SAML/OIDC)
│   ├── Directory Sync (SCIM)
│   └── OAuth (User Management)
└── Users & Groups
```

### Connections

A **connection** links an organization to an identity provider:
- **SSO Connection:** Maps to a customer's SAML IdP or OIDC provider
- **Directory Sync Connection:** Syncs users/groups from a SCIM provider (Google Workspace, Entra ID)
- **OAuth Connection:** Enables password and magic link login via AuthKit

### Authentication Flows

| Type | Protocol | Use Case |
|------|----------|----------|
| **SSO** | SAML 2.0, OIDC | Enterprise users authenticate via corporate IdP |
| **Directory Sync** | SCIM | Automated user/group provisioning from HR/directory |
| **AuthKit** | OAuth 2.0 | App-native password/magic link auth for smaller orgs |

### Authentication Credentials

Two credentials identify your application to WorkOS:

| Credential | Purpose | Example |
|----------|---------|---------|
| **client_id** | Public application identifier | `default_organization_01ARZ3NDEKTSV4RRFFQ6WQ4` |
| **client_secret** / **API Key** | Secret authentication token | `sk_live_...` (API key) |

Obtain from WorkOS dashboard: `https://dashboard.workos.com/api-keys`

---

## Authentication & API Keys

### API Key Header

All WorkOS API requests require the `Authorization` header with API key:

```
Authorization: Bearer <API_KEY>
```

**Example:**
```bash
curl -H "Authorization: Bearer sk_live_..." \
  https://api.workos.com/organizations
```

### Environment Variables

Recommended setup for thegent integrations:

```bash
# Required
WORKOS_API_KEY=sk_live_...           # API key for server-side requests
WORKOS_CLIENT_ID=default_organization_...

# Optional (for AuthKit)
WORKOS_CLIENT_SECRET=...             # For OAuth code exchange
WORKOS_REDIRECT_URI=https://app.example.com/auth/callback
```

### API Key Introspection

Check API key status and rate limits:

```
GET https://api.workos.com/keys/{key_id}
Authorization: Bearer <API_KEY>

Response:
{
  "id": "api_key_01ARZ...",
  "name": "Production API Key",
  "created_at": "2024-01-15T10:00:00Z",
  "active": true,
  "rate_limit": {
    "requests_per_minute": 600,
    "requests_per_second": 10
  }
}
```

---

## Base URL

```
https://api.workos.com
```

All endpoints are relative to this base.

---

## Organizations Endpoint

### GET /organizations

List all organizations.

```
GET https://api.workos.com/organizations
Authorization: Bearer <API_KEY>
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Max results (default 10, max 100) |
| `before` / `after` | string | Cursor for pagination |

**Response:**

```json
{
  "object": "list",
  "data": [
    {
      "id": "org_01ARZ3NDEKTSV4RRFFQ6WQ4",
      "object": "organization",
      "name": "Acme Corp",
      "domains": [
        {
          "id": "org_domain_01ARZ...",
          "object": "organization_domain",
          "domain": "acme.com",
          "verified_at": "2024-01-15T10:00:00Z"
        }
      ],
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "list_metadata": {
    "before": null,
    "after": "org_01ARZ3ND..."
  }
}
```

### POST /organizations

Create a new organization.

```
POST https://api.workos.com/organizations
Authorization: Bearer <API_KEY>
Content-Type: application/json

{
  "name": "Acme Corp",
  "domain_data": {
    "domain": "acme.com"
  }
}
```

**Response:** Same structure as GET single organization.

### GET /organizations/{id}

Get organization details.

```
GET https://api.workos.com/organizations/org_01ARZ3NDEKTSV4RRFFQ6WQ4
Authorization: Bearer <API_KEY>
```

---

## Single Sign-On (SSO)

### SSO Authorization Endpoints

#### 1. Create Authorization URL

Direct users to WorkOS SSO:

```
GET https://api.workos.com/sso/authorize
  ?client_id=<client_id>
  &organization_id=<org_id>  [or domain=<domain>]
  &redirect_uri=<callback_url>
  &response_type=code
  &state=<random_state>
```

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `client_id` | Yes | Your WorkOS client_id |
| `organization_id` | One of | Organization ID |
| `domain` | One of | Organization domain (alternative) |
| `redirect_uri` | Yes | Callback URL (must match registered) |
| `response_type` | Yes | Always `code` |
| `state` | Recommended | CSRF protection token |

**Redirect Flow:**
```
User → Your App → /authorize
       Your App → WorkOS SSO
       WorkOS → User authenticates with IdP
       WorkOS → Redirect to your callback with code + state
       Your App → Exchange code for session
```

#### 2. Authorization Code Exchange

Exchange code for session:

```
POST https://api.workos.com/sso/code
Authorization: Bearer <API_KEY>
Content-Type: application/json

{
  "client_id": "<client_id>",
  "code": "<authorization_code>"
}
```

**Response:**

```json
{
  "id": "ses_01ARZ3NDEKTSV4RRFFQ6WQ4",
  "object": "sso_session",
  "user": {
    "id": "user_01ARZ3NDEKTSV4RRFFQ6WQ4",
    "object": "user",
    "email": "john@acme.com",
    "first_name": "John",
    "last_name": "Doe",
    "email_verified": true
  },
  "organization_id": "org_01ARZ3NDEKTSV4RRFFQ6WQ4",
  "authentication_method": "SAML"
}
```

### SSO Connections

#### GET /sso_connections

List SSO connections for an organization.

```
GET https://api.workos.com/sso_connections
  ?organization_id=org_01ARZ3NDEKTSV4RRFFQ6WQ4
Authorization: Bearer <API_KEY>
```

**Response:**

```json
{
  "object": "list",
  "data": [
    {
      "id": "conn_01ARZ3NDEKTSV4RRFFQ6WQ4",
      "object": "sso_connection",
      "organization_id": "org_01ARZ3NDEKTSV4RRFFQ6WQ4",
      "connection_type": "SAML",
      "name": "Acme SAML",
      "created_at": "2024-01-15T10:00:00Z",
      "status": "established"
    }
  ]
}
```

---

## Directory Sync

### Directory Sync Connections

#### GET /directory_sync_connections

List Directory Sync connections.

```
GET https://api.workos.com/directory_sync_connections
  ?organization_id=org_01ARZ3NDEKTSV4RRFFQ6WQ4
Authorization: Bearer <API_KEY>
```

**Response:**

```json
{
  "object": "list",
  "data": [
    {
      "id": "dir_conn_01ARZ...",
      "object": "directory_sync_connection",
      "organization_id": "org_01ARZ...",
      "name": "Google Workspace",
      "directory_provider": "google_workspace",
      "status": "linked",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

### Directory Sync Users

#### GET /directory_users

List provisioned users from Directory Sync.

```
GET https://api.workos.com/directory_users
  ?directory_id=dir_conn_01ARZ...
Authorization: Bearer <API_KEY>
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `directory_id` | string | Directory connection ID |
| `limit` | integer | Pagination (default 10, max 100) |
| `before` / `after` | string | Cursor |

**Response:**

```json
{
  "object": "list",
  "data": [
    {
      "id": "dir_usr_01ARZ...",
      "object": "directory_user",
      "directory_id": "dir_conn_01ARZ...",
      "external_id": "goog_01ARZ...",
      "emails": [
        { "address": "john@acme.com", "primary": true }
      ],
      "first_name": "John",
      "last_name": "Doe",
      "idp_metadata": {
        "title": "Engineer",
        "department": "Engineering"
      },
      "state": "active",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

### Directory Sync Groups

#### GET /directory_groups

List provisioned groups.

```
GET https://api.workos.com/directory_groups
  ?directory_id=dir_conn_01ARZ...
Authorization: Bearer <API_KEY>
```

**Response:**

```json
{
  "object": "list",
  "data": [
    {
      "id": "dir_grp_01ARZ...",
      "object": "directory_group",
      "directory_id": "dir_conn_01ARZ...",
      "external_id": "goog_grp_01ARZ...",
      "name": "Engineering",
      "display_name": "Engineering Team",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

### Directory Sync Webhooks

WorkOS sends webhook events for user/group changes:

```json
{
  "id": "evt_01ARZ...",
  "type": "dsync.user.created",
  "created_at": "2024-01-15T10:00:00Z",
  "data": {
    "object": "directory_user",
    "id": "dir_usr_01ARZ...",
    "directory_id": "dir_conn_01ARZ...",
    "emails": [{ "address": "new@acme.com", "primary": true }],
    "first_name": "New",
    "last_name": "User",
    "state": "active"
  }
}
```

**Event Types:**
- `dsync.user.created`
- `dsync.user.updated`
- `dsync.user.deleted`
- `dsync.group.created`
- `dsync.group.updated`
- `dsync.group.deleted`

---

## Admin Portal

### Admin Portal Links

The Admin Portal provides a hosted UI for IT admins to configure SSO/Directory Sync without vendor support.

#### POST /admin_portal_authorizations

Create an authorization link for the Admin Portal (5-minute expiration).

```
POST https://api.workos.com/admin_portal_authorizations
Authorization: Bearer <API_KEY>
Content-Type: application/json

{
  "organization_id": "org_01ARZ3NDEKTSV4RRFFQ6WQ4",
  "environment_id": "env_..."  [optional]
}
```

**Response:**

```json
{
  "object": "admin_portal_authorization",
  "id": "auth_01ARZ...",
  "organization_id": "org_01ARZ...",
  "authorization_url": "https://admin.workos.com/authorize?code=auth_01ARZ...",
  "created_at": "2024-01-15T10:00:00Z",
  "expires_at": "2024-01-15T10:05:00Z"
}
```

**Use Cases:**
- Embed in customer dashboard: `<a href="{authorization_url}">Configure SSO</a>`
- Expires in 5 minutes; generate fresh link per request

### Admin Portal Features

From within the portal, IT admins can:

| Feature | Capability |
|---------|-----------|
| **Domain Verification** | Add DNS records proving organizational domain ownership |
| **SSO Management** | Test connections, view session details, edit configuration, reset connections |
| **Directory Sync** | Monitor sync status, manage attribute mappings, select groups, review synced users |
| **User Management** | Manage users, set roles, configure email domains |

---

## Audit Logs

### GET /audit_logs

Retrieve audit log events for compliance tracking.

```
GET https://api.workos.com/audit_logs
  ?organization_id=org_01ARZ3NDEKTSV4RRFFQ6WQ4
  &limit=10
  &after=audit_log_01ARZ...
Authorization: Bearer <API_KEY>
```

**Response:**

```json
{
  "object": "list",
  "data": [
    {
      "object": "audit_log",
      "id": "audit_log_01ARZ...",
      "organization_id": "org_01ARZ...",
      "action": "sso.user.authenticated",
      "actor": {
        "type": "user",
        "id": "user_01ARZ..."
      },
      "targets": [
        {
          "type": "organization",
          "id": "org_01ARZ..."
        }
      ],
      "result": "success",
      "occurred_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

---

## User Management (AuthKit)

WorkOS provides user creation, password management, and magic link authentication.

### POST /users

Create a user.

```
POST https://api.workos.com/users
Authorization: Bearer <API_KEY>
Content-Type: application/json

{
  "organization_id": "org_01ARZ3NDEKTSV4RRFFQ6WQ4",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password_hash": "bcrypt_hash_...",  [optional]
  "email_verified": false
}
```

### GET /users

List users in an organization.

```
GET https://api.workos.com/users
  ?organization_id=org_01ARZ3NDEKTSV4RRFFQ6WQ4
Authorization: Bearer <API_KEY>
```

---

## SDK Support

WorkOS provides official SDKs:

| Language | Package | Installation |
|----------|---------|--------------|
| **Python** | `workos` | `pip install workos` |
| **Node.js** | `@workos-inc/node` | `npm install @workos-inc/node` |
| **Go** | `github.com/workos/workos-go` | Import from Go modules |
| **Java** | `com.workos:workos` | Maven/Gradle dependency |
| **.NET** | `WorkOS.Net` | NuGet package |

### Python Example

```python
from workos import WorkOS

workos = WorkOS(api_key="sk_live_...")

# Create organization
org = workos.organizations.create(
    name="Acme Corp",
    domain_data={"domain": "acme.com"}
)

# Create SSO authorization URL
auth_url = workos.sso.authorization_url(
    client_id="default_organization_...",
    organization_id=org.id,
    redirect_uri="https://app.example.com/auth/callback"
)

# Exchange code for session
session = workos.sso.get_profile(code=auth_code)
print(f"User: {session.user.email}")

# List Directory Sync connections
connections = workos.directory_sync.list_connections(
    organization_id=org.id
)

# List provisioned users
users = workos.directory_sync.list_users(
    directory_id=connections[0].id
)
```

### Node.js Example

```typescript
import { WorkOS } from '@workos-inc/node';

const client = new WorkOS(process.env.WORKOS_API_KEY);

// Get organization
const org = await client.organizations.getOrganization('org_...');

// Create SSO authorization URL
const authUrl = client.sso.getAuthorizationUrl({
  clientId: process.env.WORKOS_CLIENT_ID,
  organizationId: org.id,
  redirectUri: 'https://app.example.com/auth/callback'
});

// Exchange code
const session = await client.sso.getProfile({ code: authCode });

// List Directory Sync users
const users = await client.dirSync.listUsers({
  directoryId: 'dir_conn_...'
});
```

---

## Error Codes

WorkOS API errors return standard HTTP codes with structured error responses:

| Code | Meaning | Details |
|------|---------|---------|
| 200 | Success | Request succeeded |
| 201 | Created | Resource created |
| 204 | No Content | Successful but no response body |
| 400 | Bad Request | Invalid parameters or validation error |
| 401 | Unauthorized | Invalid or missing API key |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Resource already exists or state conflict |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Internal WorkOS error |
| 503 | Service Unavailable | Service temporarily down |

**Error Response Format:**

```json
{
  "object": "error",
  "code": "invalid_request",
  "message": "Invalid organization_id",
  "request_id": "req_..."
}
```

---

## Rate Limits

Default rate limits per API key:

| Limit | Value |
|-------|-------|
| **Requests per minute** | 600 |
| **Requests per second** | 10 |
| **Concurrent requests** | 100 |

Check rate limit status in response headers:

```
X-RateLimit-Limit: 600
X-RateLimit-Remaining: 599
X-RateLimit-Reset: 1705329600
```

---

## Relevance to thegent

WorkOS enables thegent deployments to support enterprise customers requiring:

1. **Multi-tenant SSO:** Each customer organization authenticates via their corporate IdP (Okta, Azure AD, etc.)
2. **Directory Sync:** Automated user provisioning from SCIM providers; eliminates manual user management
3. **Admin Portal:** Customers self-configure SSO/Directory Sync without vendor support
4. **Audit Logs:** Track authentication and authorization events for compliance
5. **User Management:** Fallback password/magic link auth for non-enterprise tiers

**Integration Points:**
- Web dashboard: Use WorkOS AuthKit (covered in `workos-authkit.md`)
- CLI server: Validate organization from JWT; route requests per organization
- Webhook handlers: Sync Directory Sync users to thegent user database
- Multi-org routing: Use organization_id to isolate data

---

## Sources

- [WorkOS API Reference](https://workos.com/docs/reference)
- [Single Sign-On Documentation](https://workos.com/docs/sso)
- [Directory Sync Documentation](https://workos.com/docs/directory-sync)
- [Admin Portal Documentation](https://workos.com/docs/admin-portal)
- [User Management (AuthKit)](https://workos.com/docs/user-management)
- [Audit Logs](https://workos.com/docs/audit-logs)
- [GitHub: workos-python](https://github.com/workos/python-sdk)
- [GitHub: workos-node](https://github.com/workos/workos-node)
