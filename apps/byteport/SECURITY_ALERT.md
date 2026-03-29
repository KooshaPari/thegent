# 🚨 CRITICAL SECURITY ALERT - IMMEDIATE ACTION REQUIRED

**Date:** 2025-10-12  
**Severity:** HIGH  
**Issue:** Exposed credentials in git history

## Executive Summary

Multiple `.env` files containing production secrets were tracked in git and exposed in commit history. These files have now been removed from tracking, but **all exposed credentials must be rotated immediately**.

---

## Exposed Credentials

### 1. WorkOS API Credentials
**Location:** Root `.env`, `backend/.env`, `frontend/web-next/.env.local`

```
WORKOS_API_KEY: sk_test_a2V5XzAxSzRLWVpRSkFNUURWS0tWR0JZQVFGUkZWLGNsYmZHcTZmTVc0bFlicHA3bXNjMEpIVTE
WORKOS_CLIENT_ID: client_01K4KYZR40RK7R9X3PPB5SEJ66
WORKOS_CLIENT_SECRET: f52b84bfa0bfba6c1554a8db1b14bc1fcec27fb59970a1204f6d23927749e9b9
WORKOS_COOKIE_PASSWORD: eSwJsxDHCWsLFJVOzjYFoE6+g3gnIWYP
```

**Action Required:**
1. Log in to [WorkOS Dashboard](https://dashboard.workos.com/)
2. Navigate to API Keys section
3. Revoke the exposed API key immediately
4. Generate a new API key
5. Rotate the client secret
6. Generate a new random cookie password: `openssl rand -base64 24`
7. Update all `.env` files with new credentials

**Priority:** 🔴 IMMEDIATE

---

### 2. JWT Secret
**Location:** `backend/.env`

```
JWT_SECRET: byteport-dev-secret-key-change-in-production
```

**Action Required:**
1. Generate a new secure secret: `openssl rand -hex 64`
2. Update `JWT_SECRET` in backend `.env`
3. **WARNING:** All existing JWT tokens will be invalidated
4. Users will need to re-authenticate

**Priority:** 🔴 HIGH

---

### 3. Encryption Key
**Location:** `backend/.env`

```
ENCRYPTION_KEY: byteport-dev-encryption-key-32b
```

**Action Required:**
1. Generate a new 32-byte key: `openssl rand -base64 32`
2. Update `ENCRYPTION_KEY` in backend `.env`
3. **WARNING:** Previously encrypted data may become inaccessible
4. If you have encrypted production data, plan a migration strategy first

**Priority:** 🟠 MEDIUM (if no encrypted production data yet)

---

### 4. Database Credentials
**Location:** `backend/.env`

```
DATABASE_URL: host=localhost user=zen password=zen dbname=zen_mcp
```

**Action Required:**
1. Change the `zen` database user password
2. Update `DATABASE_URL` in backend `.env`
3. Restart database connections

**Priority:** 🟡 LOW (if only local development database)

---

### 5. Host Agent API Key
**Location:** `backend/.env`

```
HOST_AGENT_API_KEY: byteport-host-agent-dev-key
```

**Action Required:**
1. Generate a new secure key: `openssl rand -hex 32`
2. Update `HOST_AGENT_API_KEY` in backend `.env`
3. Update any deployed host agents with new key

**Priority:** 🟡 LOW (if no host agents deployed yet)

---

### 6. NVMS Token Secret
**Location:** `backend/.env`

```
NVMS_TOKEN_SECRET: nvms-dev-token-secret
```

**Action Required:**
1. Generate a new secure secret: `openssl rand -hex 32`
2. Update `NVMS_TOKEN_SECRET` in backend `.env`

**Priority:** 🟡 LOW (if internal service only)

---

## Remediation Steps Completed

✅ **Step 1:** Removed `.env` files from git tracking
```bash
git rm --cached .env backend/.env frontend/web-next/.env frontend/web-next/.env.local
```

✅ **Step 2:** Updated `.gitignore` to prevent future commits
```gitignore
# Environment files (SECURITY: Never commit secrets!)
.env
.env.*
!.env.example
!.env*.example
```

✅ **Step 3:** Created sanitized `.env.example` templates

---

## Next Steps for Developer

### Immediate (Do Now)

1. **Rotate WorkOS credentials** (see section 1)
2. **Rotate JWT secret** (see section 2)
3. **Generate new encryption key** (see section 3)

### Before Committing

4. Verify no secrets in git:
```bash
git status
git diff --cached
```

5. Commit the security fixes:
```bash
git add .gitignore .env.example backend/.env.example frontend/web-next/.env.example
git commit -m "security: Remove .env files from tracking and update .gitignore

BREAKING CHANGE: All authentication secrets have been rotated.
Developers must copy .env.example files and fill in new credentials."
```

### After Rotating Credentials

6. Update your local `.env` files with new credentials
7. Test that the application still works
8. Document the new credential locations (password manager, secret manager)
9. Update deployment pipelines with new secrets

---

## Git History Cleanup (Optional but Recommended)

The exposed secrets are still in git history. To completely remove them:

### Option 1: BFG Repo-Cleaner (Recommended)
```bash
# Install BFG
brew install bfg  # macOS

# Backup your repo
cd /Users/kooshapari/temp-PRODVERCEL/485
cp -r BytePort BytePort-backup

# Clean history
cd BytePort
bfg --delete-files '.env' --delete-files '.env.local'
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### Option 2: git-filter-repo
```bash
# Install git-filter-repo
pip install git-filter-repo

# Clean history
git filter-repo --path .env --path backend/.env --path frontend/web-next/.env --path frontend/web-next/.env.local --invert-paths
```

### Option 3: Start Fresh (Nuclear Option)
If this is a private repo with no collaborators, consider:
1. Create a new empty repo
2. Copy current working tree (without .git/)
3. Initialize fresh git history
4. Push to new remote

---

## Prevention Checklist

Future commits must follow these rules:

- [ ] Use `.env.example` templates only (no actual secrets)
- [ ] Never hardcode API keys, tokens, or passwords
- [ ] Use environment variables or secret managers
- [ ] Review `git diff --cached` before every commit
- [ ] Enable pre-commit hooks to block `.env` files
- [ ] Use GitHub secret scanning (if using GitHub)
- [ ] Rotate credentials immediately if accidentally committed

---

## Pre-Commit Hook (Optional)

Add this to `.git/hooks/pre-commit`:

```bash
#!/bin/bash

if git diff --cached --name-only | grep -qE '^\.env$|\.env\..*$' ; then
    echo "❌ ERROR: Attempting to commit .env files!"
    echo "Please remove them from staging:"
    echo "  git reset HEAD .env"
    exit 1
fi

# Check for common secret patterns
if git diff --cached | grep -qE 'sk_test_|sk_live_|WORKOS|JWT_SECRET|ENCRYPTION_KEY'; then
    echo "⚠️  WARNING: Potential secret detected in commit!"
    echo "Please review your changes carefully."
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Contact

If you have questions or need assistance:
- **Security Issues:** Create a private security advisory on GitHub
- **Internal Team:** Contact DevOps team immediately

---

## Verification

After completing all steps, verify:

- [ ] No `.env` files are tracked: `git ls-files | grep .env`
- [ ] WorkOS credentials rotated and tested
- [ ] JWT secret rotated (users logged out)
- [ ] Application works with new credentials
- [ ] `.gitignore` updated
- [ ] Commit created with security fixes

---

**Last Updated:** 2025-10-12  
**Status:** 🔴 PENDING CREDENTIAL ROTATION
