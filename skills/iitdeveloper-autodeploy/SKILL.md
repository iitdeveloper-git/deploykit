---
name: iitdeveloper-autodeploy
description: Automatically turn any repository into a secure, production-ready CI/CD project using iitdeveloper-git/shared-workflows@v1. Detects language/framework, reuses shared workflows, enforces least-privilege, and configures environments and Telegram notifications.
---

# IITDEVELOPER AutoDeploy

Configure repositories using reusable workflows & actions from:
```yaml
# Reusable Workflows:
uses: iitdeveloper-git/shared-workflows/.github/workflows/<workflow>.yml@v1

# Composite Actions:
uses: iitdeveloper-git/shared-workflows/actions/<action>@v1
```

## Goal

Turn any repository into a secure, production-ready CI/CD project with minimal custom workflow code.

**Primary Principle:** Always prefer reusable workflows from `iitdeveloper-git/shared-workflows@v1` over duplicating CI/CD logic inside the application repository. Treat `shared-workflows@v1` as the single source of truth.

---

## Execution Workflow

### 1. Inspect the Project
Automatically detect the project stack without making assumptions:
- **Language / Framework:** Node.js, Next.js, Python, FastAPI, Django, Go, Java, Docker, etc.
- **Package Manager:** `npm`, `yarn`, `pnpm`, `bun`, `pip`, `poetry`, `uv`.
- **Scripts & Commands:** Test, lint, format, type-check, and build commands (e.g. from `package.json`, `pyproject.toml`, `Makefile`, `Dockerfile`).
- **Existing CI/CD:** Inspect `.github/workflows/` for existing pipelines, deployment targets, and custom steps.
- **Environments:** Detect target environments (e.g. UAT, Staging, Production).
- **Deployment Mechanism:** SSH, Docker container registry, PM2, Kubernetes, Cloud (AWS/GCP/Vercel/Render), static host.
- **Notifications:** Telegram or Slack alerts.

---

### 2. Inspect Shared Workflows Interface (`@v1`)
Verify available reusable workflows and composite actions from `iitdeveloper-git/shared-workflows@v1`:

| Component | Target Ref | Purpose |
|---|---|---|
| `actions/telegram-notify` | `@v1` | Composite action for rich Telegram deployment & CI alerts |
| `.github/workflows/telegram-notify.yml` | `@v1` | Reusable standalone job for Telegram alerts |
| `.github/workflows/node-ci.yml` | `@v1` | Reusable Node.js matrix test, lint, and build pipeline |
| `.github/workflows/python-ci.yml` | `@v1` | Reusable Python pytest, ruff lint, and caching pipeline |
| `.github/workflows/docker-build.yml` | `@v1` | Reusable multi-arch Docker build & push with Buildx |
| `.github/workflows/security-scan.yml` | `@v1` | Reusable Trivy filesystem and container vulnerability scan |

> [!IMPORTANT]
> Use **only** workflows, actions, inputs, and secrets that actually exist in `@v1`. Do not invent non-existent workflow names or parameters. Never use `@main` or `@master`.

---

### 3. Reuse Before Creating
- Prefer:
  ```yaml
  uses: iitdeveloper-git/shared-workflows/.github/workflows/<workflow>.yml@v1
  ```
  or:
  ```yaml
  uses: iitdeveloper-git/shared-workflows/actions/<action>@v1
  ```
- Keep custom workflow code inside the caller repository strictly limited to application-specific build scripts or unique deployment targets.

---

### 4. Configure Appropriate Pipeline
Build only what the project actually needs. Avoid unnecessary stages.

**Standard Production Lifecycle:**
```
Pull Request / Commit
         ↓
  CI (Lint & Test)
         ↓
   Security Scan
         ↓
  Build / Package
         ↓
  UAT Deployment (Optional/Branch-based)
         ↓
Production Deployment (Tagged / Main / Protected Env)
         ↓
Telegram Status Notification
```

---

### 5. Deployment Safety & Least Privilege
- **GitHub Environments:** Use GitHub Environments (`Production`, `UAT`, `Staging`) with protection rules.
- **Secret Isolation:** Pass secrets exclusively via GitHub Secrets / Environment Secrets. Never hardcode credentials.
- **Least Privilege:** Declare explicit minimal permissions (e.g. `permissions: contents: read`).
- **No Secret Leakage:** Ensure secrets never appear in logs or process args.
- **Immutability & Rollback:** Deploy immutable artifacts (Docker tags, SemVer git tags).
- **Post-Deploy Health Check:** Verify endpoint status after deployment before marking success.
- **No Arbitrary Remote Execution:** Never construct unescaped remote shell commands from untrusted inputs.

---

### 6. Managing Existing CI/CD
If `.github/workflows/` already exist:
1. Audit existing jobs for custom build steps, environment variables, and deployment secrets.
2. Preserve existing application-specific behavior.
3. Replace duplicated boilerplate (linting, testing, Docker builds, notifications) with `shared-workflows@v1`.
4. Delete old duplicated workflow files only after verifying compatibility.
5. Purge any legacy references to `iitdeveloper-git-shared-workflows` and update to `shared-workflows@v1`.

---

### 7. Required Secrets Configuration
Never invent fake production secrets in files. Use clean secret references:
- `${{ secrets.TELEGRAM_BOT_TOKEN }}`
- `${{ secrets.TELEGRAM_CHAT_ID }}`
- `${{ secrets.DEPLOY_HOST }}`
- `${{ secrets.DEPLOY_USER }}`
- `${{ secrets.DEPLOY_SSH_KEY }}`

Detail every required secret clearly in the final summary.

---

### 8. Validation Before Finishing
Before completing the deployment setup:
1. Validate YAML syntax on all created/modified `.github/workflows/*.yml` files.
2. Validate reusable workflow input names, types, and defaults against `@v1`.
3. Validate secret bindings and environment variables.
4. Verify explicit permissions blocks (`permissions: contents: read`).
5. Ensure zero `@main` / `@master` references exist in workflow calls.

---

### 9. What NOT to Do
- ❌ Do NOT hardcode credentials or server passwords in workflow files.
- ❌ Do NOT duplicate shared workflow logic in the caller repo.
- ❌ Do NOT reference non-existent workflows or inputs.
- ❌ Do NOT use `@main` or `@master` refs.
- ❌ Do NOT trigger automatic production deployment on unmerged feature branches.
- ❌ Do NOT remove existing safety/rollback mechanisms without replacement.

---

## Final Report Format

When completing the auto-deploy setup for a project, always output the report structured as follows:

```markdown
### 🚀 AutoDeploy Summary

**AUTODEPLOY STATUS:** READY | PARTIAL | BLOCKED

* **Stack Detected:** <Language / Framework / Package Manager>
* **Environments Configured:** <UAT, Production, etc.>
* **Shared Workflows Used (@v1):**
  - `iitdeveloper-git/shared-workflows/.github/workflows/...@v1`
  - `iitdeveloper-git/shared-workflows/actions/telegram-notify@v1`
* **Files Created / Changed:**
  - `.github/workflows/...`
* **Required GitHub Secrets:**
  - `TELEGRAM_BOT_TOKEN`: Bot token from @BotFather
  - `TELEGRAM_CHAT_ID`: Group or channel chat ID
  - `<OTHER_SECRETS>`: <Purpose>
* **Required GitHub Environment Settings:**
  - Environment: `Production` (Required reviewers / branch protection)
* **Deployment Trigger:** <e.g., Push to main, Release tag v*.*.*, Workflow dispatch>
* **Production Protection:** <Protected Environment / Tag approval / Pre-flight checks>
* **Notification Configuration:** Telegram rich HTML deployment & CI status notifications
* **Validation Performed:** YAML validation, input matching, syntax verification
* **Manual Actions Remaining:** <Step-by-step instructions for repository maintainer>
```
