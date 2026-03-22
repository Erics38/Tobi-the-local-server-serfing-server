# Security Audit Report

**Date:** 2026-03-21
**Project:** Restaurant AI Chatbot
**Status:** ✅ **SAFE FOR PUBLIC REPOSITORY**

---

## Executive Summary

✅ **No critical security issues found**
⚠️ **2 warnings requiring attention before production deployment**
📋 **5 recommendations for hardening**

---

## Findings

### ✅ GOOD: No Hardcoded Secrets

**What we checked:**
- No API keys in code
- No passwords committed
- No private keys
- No authentication tokens
- No AWS credentials

**Evidence:**
```bash
# Searched entire codebase for sensitive patterns
grep -r "SECRET_KEY.*=.*sk-" .  # No matches
grep -r "API_KEY.*=.*[a-zA-Z0-9]{32}" .  # No matches
grep -r "password.*=.*['\"][^'\"]{8,}" .  # No matches
```

**Protection mechanisms:**
- `.gitignore` excludes `.env` files ✅
- `.gitignore` excludes SSH keys (`*.pem`) ✅
- `pre-upload-check.sh` scans for secrets before commits ✅

---

### ⚠️ WARNING 1: Default SECRET_KEY in Production

**Issue:**
[app/config.py:28](app/config.py#L28)
```python
secret_key: str = "dev-secret-key-change-in-production"
```

**Risk:** Medium
If someone deploys to production without setting `SECRET_KEY` environment variable, they'll use this default value. This could allow session hijacking or token forgery.

**Impact:**
- Session cookies could be forged
- CSRF protection could be bypassed
- JWT tokens (if added later) could be signed with known key

**Fix Required Before Production:**
```bash
# Generate a strong secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set it in environment
export SECRET_KEY="<generated-key>"

# Or in docker-compose.yml
services:
  app:
    environment:
      - SECRET_KEY=${SECRET_KEY}  # Reads from .env or environment
```

**Current Protection:**
- ✅ Default has warning text: "change-in-production"
- ✅ Docker Compose uses env var: `SECRET_KEY=${SECRET_KEY:-change-me-in-production}`
- ✅ Documentation warns about this in [SECURITY.md](SECURITY.md#L167)

**Status:** ⚠️ Acceptable for development, **MUST FIX** for production

---

### ⚠️ WARNING 2: CORS Set to Allow All Origins

**Issue:**
[app/config.py:31](app/config.py#L31)
```python
allowed_origins: str = "*"  # Comma-separated list
```

[docker-compose.yml:34](docker-compose.yml#L34)
```yaml
- ALLOWED_ORIGINS=*
```

**Risk:** Low-Medium
Allows any website to make requests to your API. Could enable CSRF attacks or data exfiltration if users are authenticated.

**Impact:**
- Any website can call your API
- Potential for CSRF attacks (if you add authentication later)
- Can't rely on browser's same-origin protection

**Fix Required Before Production:**
```bash
# Set specific allowed origins
export ALLOWED_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
```

Or in `docker-compose.yml`:
```yaml
- ALLOWED_ORIGINS=https://restaurant.example.com
```

**Current Protection:**
- ✅ `.env.example` has comments warning about this
- ✅ Documentation mentions restricting CORS

**Status:** ⚠️ Acceptable for development, **MUST FIX** for production

---

### ✅ GOOD: No Hardcoded IPs or Hostnames

**What we checked:**
- No hardcoded EC2 IPs
- No hardcoded private IPs
- No hardcoded domain names

**Evidence:**
```python
# app/config.py uses configurable values
host: str = "0.0.0.0"  # Binds to all interfaces (correct for Docker)
llama_server_url: Optional[str] = None  # User must configure

# static/restaurant_chat.html uses dynamic origin
const API_URL = window.location.origin;  # Not hardcoded!
```

**Status:** ✅ Safe

---

### ✅ GOOD: No SSH Keys Committed

**What we checked:**
- No `.pem` files in Git
- No `id_rsa` files
- No AWS credentials

**Evidence:**
```bash
# .gitignore properly excludes keys
*.pem
*.key
id_rsa*
.env
```

**Verification:**
```bash
git ls-files | grep -E "\.(pem|key)$"
# No matches ✅
```

**Status:** ✅ Safe

---

### ✅ GOOD: Environment Variables Used Correctly

**Pattern:**
```python
# All sensitive config loaded from environment
class Settings(BaseSettings):
    secret_key: str = "dev-secret-key-change-in-production"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
```

**Files that load environment variables:**
- `app/config.py` - Main configuration ✅
- `docker-compose.yml` - Uses `${VAR:-default}` syntax ✅
- `.env.example` - Template with safe defaults ✅

**Status:** ✅ Safe

---

### ✅ GOOD: No Database Credentials Hardcoded

**Current setup:**
```python
# Uses SQLite with local file (no credentials needed)
DATABASE_URL=sqlite:///./data/orders.db
```

**Future PostgreSQL (from docs):**
```bash
# Documented to use environment variable
DATABASE_URL=postgresql://user:password@localhost/dbname
```

**Status:** ✅ Safe (and ready for future PostgreSQL migration)

---

## Recommendations

### 1. Add SECRET_KEY Validation on Startup

**Suggestion:** Add a check to prevent running in production with default secret

Add to [app/main.py](app/main.py):
```python
@app.on_event("startup")
async def validate_security():
    """Validate security settings on startup."""
    if settings.is_production:
        if "dev-secret-key" in settings.secret_key or "change-me" in settings.secret_key:
            raise ValueError(
                "CRITICAL: Running in production with default SECRET_KEY! "
                "Generate a secure key with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )

        if settings.allowed_origins == "*":
            logger.warning(
                "SECURITY WARNING: CORS allows all origins (*) in production. "
                "Set ALLOWED_ORIGINS to your domain."
            )
```

**Priority:** High
**Effort:** 5 minutes

---

### 2. Add Rate Limiting for Production

**Current state:** No rate limiting

**Suggestion:** Add rate limiting to prevent DoS attacks

Use `slowapi` library:
```bash
pip install slowapi
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/chat")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def chat_endpoint():
    ...
```

**Priority:** Medium (for production)
**Effort:** 15 minutes

---

### 3. Add Security Headers

**Current state:** Basic FastAPI defaults

**Suggestion:** Add security headers to all responses

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

**Priority:** Medium (for production)
**Effort:** 10 minutes

---

### 4. Scan Dependencies for Vulnerabilities

**Suggestion:** Add automated dependency scanning

Add to `.github/workflows/ci.yml`:
```yaml
- name: Check for security vulnerabilities
  run: |
    pip install safety
    safety check --json
```

Or use Dependabot (already enabled in GitHub):
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

**Priority:** Low (nice to have)
**Effort:** 5 minutes

---

### 5. Add Logging of Security Events

**Current state:** Basic logging

**Suggestion:** Log security-relevant events

```python
# Log failed authentication attempts (if you add auth)
# Log unusual request patterns
# Log configuration changes

import logging
security_logger = logging.getLogger("security")

# Example
if suspicious_request:
    security_logger.warning(
        f"Suspicious request from {request.client.host}: {details}"
    )
```

**Priority:** Low (for production)
**Effort:** Ongoing

---

## Hardcoded Values Audit

### Acceptable Hardcoded Values

These are configuration defaults, not security issues:

| File | Line | Value | Risk | Notes |
|------|------|-------|------|-------|
| `app/config.py` | 15 | `host = "0.0.0.0"` | ✅ Safe | Correct for Docker |
| `app/config.py` | 16 | `port = 8000` | ✅ Safe | Standard app port |
| `app/config.py` | 21 | `restaurant_name = "The Common House"` | ✅ Safe | Business logic |
| `docker-compose.yml` | 53 | `ports: - "8000:8000"` | ✅ Safe | Standard mapping |
| `docker-compose.yml` | 60 | `--ctx-size 4096` | ✅ Safe | AI model config |

### Values That Should Be Environment Variables

All sensitive values already use environment variables:

| Setting | Environment Variable | Default | Status |
|---------|---------------------|---------|--------|
| Secret Key | `SECRET_KEY` | ⚠️ "dev-secret..." | Must change for prod |
| CORS Origins | `ALLOWED_ORIGINS` | ⚠️ "*" | Must change for prod |
| AI Server URL | `LLAMA_SERVER_URL` | "http://llama-server:8080" | ✅ Safe |
| Database URL | `DATABASE_URL` | "sqlite:///./data/orders.db" | ✅ Safe |
| Log Level | `LOG_LEVEL` | "INFO" | ✅ Safe |

---

## Pre-Production Checklist

Before deploying to production, ensure:

- [ ] `SECRET_KEY` is set to a strong random value (not default)
- [ ] `ALLOWED_ORIGINS` is set to your specific domain (not "*")
- [ ] `ENVIRONMENT=production` is set
- [ ] `DEBUG=False` is set
- [ ] HTTPS is enabled (use reverse proxy like nginx)
- [ ] Security headers are added
- [ ] Rate limiting is enabled
- [ ] Monitoring/logging is configured
- [ ] Regular security updates are scheduled

---

## GitHub Actions Security

**Current state:** ✅ Secure

```yaml
# Uses GitHub's built-in secrets
- name: Login to GitHub Container Registry
  uses: docker/login-action@v2
  with:
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}  # Auto-provided by GitHub
```

**No manual tokens required** ✅

---

## Conclusion

**Overall Security Posture:** ✅ **GOOD**

Your codebase is safe for public GitHub repository. The defaults are secure for development use. Before production deployment, you must:

1. Set a strong `SECRET_KEY`
2. Restrict `ALLOWED_ORIGINS` to your domain
3. Consider adding rate limiting and security headers

**No immediate action required** for development/testing.

---

## Questions or Concerns?

If you find any security issues not covered in this audit, please:
1. **Do NOT** create a public GitHub issue
2. Email security concerns privately (add to README if deploying publicly)
3. Review [SECURITY.md](SECURITY.md) for reporting process
