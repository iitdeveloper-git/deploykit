---
name: iitdeveloper-autodeploy
description: Automatically turn any repository into a secure, production-ready CI/CD project using DeployKit (iitdeveloper-git/deploykit@v1). Detects language/framework, reuses shared workflows, enforces least-privilege, and configures environments, SSH Docker deployments, and multi-channel notifications (Telegram, Slack, Teams, Discord, Webhooks).
license: MIT
version: 1.0.1
tags:
  - devops
  - ci-cd
  - deployment
  - github-actions
  - docker
  - telegram
  - slack
  - teams
  - discord
  - deploykit
---

# IITDEVELOPER AutoDeploy (Powered by DeployKit)

Configure repositories using reusable workflows & actions from:
```yaml
# Reusable Workflows:
uses: iitdeveloper-git/deploykit/.github/workflows/<workflow>.yml@v1

# Composite Actions:
uses: iitdeveloper-git/deploykit/actions/<action>@v1
```

## Goal

Turn any repository into a secure, production-ready CI/CD project with minimal custom workflow code.

**Primary Principle:** Always prefer reusable workflows from `iitdeveloper-git/deploykit@v1` over duplicating CI/CD logic inside the application repository. Treat `deploykit@v1` as the single source of truth.

---

## Execution Workflow

### 1. Inspect the Project
Automatically detect the project stack without making assumptions:
- **Language / Framework:** Node.js, Next.js, Python, FastAPI, Django, Go, Java, Docker, etc.
- **Package Manager:** `npm`, `yarn`, `pnpm`, `bun`, `pip`, `poetry`, `uv`.
- **Scripts & Commands:** Test, lint, format, type-check, and build commands (e.g. from `package.json`, `pyproject.toml`, `Makefile`, `Dockerfile`).
- **Existing CI/CD:** Inspect `.github/workflows/` for existing pipelines, deployment targets, and custom steps.
- **Environments:** Detect target environments (e.g. UAT, Staging, Production).
- **Deployment Mechanism:** SSH VPS / Docker Compose, Container Registry (GHCR/DockerHub), PM2, Kubernetes, Cloud platforms.
- **Notification Channels:** Detect desired alert channels: Telegram, Slack, Microsoft Teams, Discord, or Webhooks.

---

### 2. Inspect DeployKit Interface (`@v1`)
Verify available reusable workflows and composite actions from `iitdeveloper-git/deploykit@v1`:

| Component | Target Ref | Purpose |
|---|---|---|
| `actions/notify` | `@v1` | Composite action for multi-channel alerts (Telegram, Slack, Teams, Discord, Webhooks) |
| `actions/telegram-notify` | `@v1` | Standalone composite action specifically for Telegram |
| `.github/workflows/notify.yml` | `@v1` | Reusable multi-channel notification workflow |
| `.github/workflows/telegram-notify.yml` | `@v1` | Reusable Telegram notification workflow |
| `.github/workflows/node-ci.yml` | `@v1` | Reusable Node.js matrix test, lint, and build pipeline (npm/yarn/pnpm/bun) |
| `.github/workflows/python-ci.yml` | `@v1` | Reusable Python pytest, ruff lint, and caching pipeline |
| `.github/workflows/docker-build.yml` | `@v1` | Reusable multi-arch Docker build & push with Buildx |
| `.github/workflows/deploy-ssh-docker.yml` | `@v1` | Reusable secure SSH VPS / Docker Compose deployment with rollback guard |
| `.github/workflows/security-scan.yml` | `@v1` | Reusable Trivy filesystem and container vulnerability scan |
| `.github/workflows/release.yml` | `@v1` | Reusable GitHub release automation and artifact attachment |

> [!IMPORTANT]
> Use **only** workflows, actions, inputs, and secrets that actually exist in `@v1`. Do not invent non-existent workflow names or parameters. Never use `@main` or `@master`.

---

### 3. Reuse Before Creating
- Prefer:
  ```yaml
  uses: iitdeveloper-git/deploykit/.github/workflows/<workflow>.yml@v1
  ```
  or:
  ```yaml
  uses: iitdeveloper-git/deploykit/actions/<action>@v1
  ```
- For multi-channel alerts (Slack, Teams, Discord, Webhooks, Telegram), use `actions/notify@v1` or `.github/workflows/notify.yml@v1`.
- For VPS / Docker Compose projects, use `.github/workflows/deploy-ssh-docker.yml@v1`.
- For Node.js / Next.js projects, use `.github/workflows/node-ci.yml@v1`.
- For Python / FastAPI projects, use `.github/workflows/python-ci.yml@v1`.
- For GitHub Releases, use `.github/workflows/release.yml@v1`.

---

### 4. Configure Appropriate Pipeline
Build only what the project actually needs. Avoid unnecessary stages.

**Standard Production Lifecycle:**
```
Pull Request / Commit
         ↓
  CI (Lint & Test)
         ↓
   Security Scan (Production Gate: exit-code: '1')
         ↓
  Build / Container Package
         ↓
  UAT Deployment (Optional/Branch-based)
         ↓
Production Deployment (deploy-ssh-docker / Protected Env)
         ↓
Post-Deployment Health Check & Automatic Rollback Guard
         ↓
Multi-Channel Status Notification (Telegram, Slack, Teams, Discord)
```

---

### 5. Deployment Safety & Least Privilege
- **GitHub Environments:** Use GitHub Environments (`Production`, `UAT`, `Staging`) with protection rules.
- **Secret Isolation:** Pass secrets exclusively via GitHub Secrets / Environment Secrets. Never hardcode credentials.
- **Least Privilege:** Declare explicit minimal permissions (e.g. `permissions: contents: read`).
- **No Secret Leakage:** Ensure secrets never appear in logs or process args.
- **Immutability & Rollback:** Deploy immutable artifacts (Docker tags, SemVer git tags).
- **Post-Deploy Health Check:** Verify endpoint status after deployment; if failed, trigger automatic container rollback.
- **Input Validation:** Ensure remote deployment parameters contain only safe, validated characters.

---

### 6. Managing Existing CI/CD
If `.github/workflows/` already exist:
1. Audit existing jobs for custom build steps, environment variables, and deployment secrets.
2. Preserve existing application-specific behavior.
3. Replace duplicated boilerplate (linting, testing, Docker builds, SSH deployments, notifications) with `deploykit@v1`.
4. Delete old duplicated workflow files only after verifying compatibility.
5. Upgrade any legacy references to `iitdeveloper-git/deploykit@v1`.

---

### 7. Required Secrets Configuration
Never invent fake production secrets in files. Use clean secret references:
- **Telegram:** `${{ secrets.TELEGRAM_BOT_TOKEN }}`, `${{ secrets.TELEGRAM_CHAT_ID }}`
- **Slack / Teams / Discord / Webhook:** `${{ secrets.WEBHOOK_URL }}`
- **SSH Deployment:** `${{ secrets.DEPLOY_HOST }}`, `${{ secrets.DEPLOY_USER }}`, `${{ secrets.DEPLOY_SSH_KEY }}`, `${{ secrets.DEPLOY_SSH_KNOWN_HOSTS }}`

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
- ❌ Do NOT duplicate DeployKit shared logic in the caller repo.
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
* **DeployKit Workflows Used (@v1):**
  - `iitdeveloper-git/deploykit/.github/workflows/...@v1`
  - `iitdeveloper-git/deploykit/actions/...@v1`
* **Files Created / Changed:**
  - `.github/workflows/...`
* **Required GitHub Secrets:**
  - `DEPLOY_HOST`: Remote VPS hostname or IP
  - `DEPLOY_USER`: Remote SSH username
  - `DEPLOY_SSH_KEY`: Remote Private SSH key
  - `DEPLOY_SSH_KNOWN_HOSTS`: Public host key (recommended for strict host verification)
  - `WEBHOOK_URL` or `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`: Notification credentials
* **Required GitHub Environment Settings:**
  - Environment: `Production` (Required reviewers / branch protection)
* **Deployment Trigger:** <e.g., Push to main, Release tag v*.*.*, Workflow dispatch>
* **Production Protection:** <Protected Environment / Tag approval / Pre-flight checks / Rollback guard>
* **Notification Configuration:** Multi-channel alert dispatch (Telegram / Slack / Teams / Discord / Webhook)
* **Validation Performed:** YAML validation, input matching, syntax verification
* **Manual Actions Remaining:** <Step-by-step instructions for repository maintainer>
```
