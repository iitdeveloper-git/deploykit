<p align="center">
  <img src=".github/assets/banner.jpg" alt="DeployKit banner" width="100%" />
</p>

<p align="center">
  <a href="https://github.com/iitdeveloper-git/deploykit/actions/workflows/ci.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/iitdeveloper-git/deploykit/ci.yml?branch=main&style=for-the-badge&logo=githubactions&logoColor=white&label=CI" alt="CI Status" />
  </a>
  <a href="https://github.com/iitdeveloper-git/deploykit/releases">
    <img src="https://img.shields.io/github/v/release/iitdeveloper-git/deploykit?style=for-the-badge&logo=tag&logoColor=white&label=Release" alt="Release" />
  </a>
  <a href="https://core.telegram.org/bots/api">
    <img src="https://img.shields.io/badge/Telegram_Bot_API-v7-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram Bot API" />
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" />
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License" />
  </a>
</p>

<p align="center">
  <b>DeployKit by IITDEVELOPER</b><br/>
  <i>Open-source CI/CD, security, release, and deployment automation for GitHub Actions.</i><br/>
  Drop-in Telegram notifications, standard CI pipelines, secure container builds, VPS deployments, and vulnerability scanning — zero duplication, zero vendor lock-in.
</p>

---

## 📑 Table of Contents

- [Overview & Architecture](#-overview--architecture)
- [Available Workflows & Actions](#-available-workflows--actions)
- [Quick Start](#-quick-start)
  - [1. Telegram Notification Composite Action](#1-telegram-notification-composite-action)
  - [2. Telegram Notification Reusable Workflow](#2-telegram-notification-reusable-workflow)
- [Catalog of Reusable Workflows](#-catalog-of-reusable-workflows)
  - [Node.js CI (`node-ci.yml`)](#nodejs-ci-node-ciyml)
  - [Python CI (`python-ci.yml`)](#python-ci-python-ciyml)
  - [Docker Build & Publish (`docker-build.yml`)](#docker-build--publish-docker-buildyml)
  - [Security Scan (`security-scan.yml`)](#security-scan-security-scanyml)
  - [SSH Docker Deployment (`deploy-ssh-docker.yml`)](#ssh-docker-deployment-deploy-ssh-dockeryml)
- [🤖 AutoDeploy Agent Skill](#-autodeploy-agent-skill)
- [Secrets & Configuration Setup](#-secrets--configuration-setup)
- [Action Inputs Reference](#-action-inputs-reference)
- [Versioning & Release Strategy](#-versioning--release-strategy)
- [Security & Governance](#-security--governance)
- [Repository Structure](#-repository-structure)
- [Migration Guide from Shared Workflows](#-migration-guide-from-shared-workflows)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🏗 Overview & Architecture

Maintaining duplicate GitHub Action workflow YAML files across multiple repositories creates maintenance overhead, security drift, and configuration fragmentation.

**DeployKit** solves this by providing:

1. **Centralized Standardization:** Write once, patch once, inherit everywhere.
2. **Hardened Security & Least Privilege:** Default minimal `permissions: contents: read`, zero secrets logging, and input escaping.
3. **Pure Standard Library Runtime:** Composite actions rely on pure Python standard library scripts with zero third-party dependencies, reducing third-party runtime supply-chain risk.
4. **Resilient Notifications:** Telegram notifications support rich HTML formatting, forum topics, Markdown formatting, and automated fallback to plain text if HTML entity parsing encounters malformed text.
5. **Secure VPS / Docker Deployments:** Parameter-validated Docker Compose updates with SSH host verification and automated post-deployment health check probes.

```
┌────────────────────────────────────────────────────────┐
│                   Caller Repositories                  │
├───────────────────┬──────────────────┬─────────────────┤
│    Frontend Web   │   Backend APIs   │  Microservices  │
└─────────┬─────────┴────────┬─────────┴────────┬────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌────────────────────────────────────────────────────────┐
│             iitdeveloper-git/deploykit@v1              │
├────────────────────────────────────────────────────────┤
│ • actions/telegram-notify (Composite Action)           │
│ • .github/workflows/telegram-notify.yml (Reusable)    │
│ • .github/workflows/node-ci.yml (Reusable)             │
│ • .github/workflows/python-ci.yml (Reusable)           │
│ • .github/workflows/docker-build.yml (Reusable)        │
│ • .github/workflows/deploy-ssh-docker.yml (Reusable)   │
│ • .github/workflows/security-scan.yml (Reusable)       │
│ • skills/iitdeveloper-autodeploy (AI Agent Skill)      │
└────────────────────────────────────────────────────────┘
```

---

## 📦 Available Workflows & Actions

| Workflow / Action | Type | Description |
|---|---|---|
| [`actions/telegram-notify`](actions/telegram-notify/) | **Composite Action** | Dispatches rich HTML / Plaintext Telegram deployment & CI status notifications. |
| [`.github/workflows/telegram-notify.yml`](.github/workflows/telegram-notify.yml) | **Reusable Workflow** | Standalone caller job to trigger Telegram alerts. |
| [`.github/workflows/node-ci.yml`](.github/workflows/node-ci.yml) | **Reusable Workflow** | Matrix CI pipeline for Node.js (lint, test, build with npm/yarn/pnpm/bun). |
| [`.github/workflows/python-ci.yml`](.github/workflows/python-ci.yml) | **Reusable Workflow** | Python test suite and linter runner with pip caching and pyproject.toml support. |
| [`.github/workflows/docker-build.yml`](.github/workflows/docker-build.yml) | **Reusable Workflow** | Multi-arch Docker container build, tag, and publish with Buildx. |
| [`.github/workflows/deploy-ssh-docker.yml`](.github/workflows/deploy-ssh-docker.yml) | **Reusable Workflow** | Secure VPS / Docker Compose deployment with health check & rollback safety. |
| [`.github/workflows/security-scan.yml`](.github/workflows/security-scan.yml) | **Reusable Workflow** | Filesystem and container vulnerability scanning with Trivy. |
| [`skills/iitdeveloper-autodeploy`](skills/iitdeveloper-autodeploy/) | **Agent Skill** | Antigravity AI skill to configure any repository with `deploykit@v1`. |

---

## 🚀 Quick Start

### 1. Telegram Notification Composite Action

Add this step to the end of any job in your repository:

```yaml
      - name: 📢 Send Telegram Notification
        if: always()
        uses: iitdeveloper-git/deploykit/actions/telegram-notify@v1
        with:
          bot_token: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          chat_id: ${{ secrets.TELEGRAM_CHAT_ID }}
          app_name: 'My Service'
          environment: 'Production'
          status: ${{ job.status }}
          release_tag: ${{ steps.version.outputs.tag }}
          app_url: 'https://app.example.com'
          custom_message: '🚀 Deployed hotfix for checkout flow.'
```

#### What your team receives in Telegram:

```text
🚀 My Service — Deployment Succeeded

🏷 Environment: 🟢 Production
📦 Release: v1.4.2
👤 Triggered By: octocat
🔗 Commit: a3f8c91
🌐 Live URL: https://app.example.com

📝 Release Notes:
Deployed hotfix for checkout flow.

📊 View GitHub Actions Run
```

> **Note:** Automatically adapts emoji & headings for `success` 🟢, `failure` 🔴, and `cancelled` ⚪️.

---

### 2. Telegram Notification Reusable Workflow

Call it as a standalone job after deployment steps complete:

```yaml
  notify:
    name: 📢 Telegram Notification
    needs: [deploy]
    if: always()
    uses: iitdeveloper-git/deploykit/.github/workflows/telegram-notify.yml@v1
    with:
      app_name: 'Payment API'
      environment: 'Production'
      status: ${{ needs.deploy.result }}
      release_tag: ${{ needs.deploy.outputs.tag }}
      app_url: 'https://api.example.com'
    secrets:
      TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
      TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
```

---

## 📚 Catalog of Reusable Workflows

### Node.js CI (`node-ci.yml`)

```yaml
jobs:
  test:
    uses: iitdeveloper-git/deploykit/.github/workflows/node-ci.yml@v1
    with:
      node-version: '20'
      package-manager: 'npm' # npm, yarn, pnpm, bun
      run-lint: true
      run-test: true
      run-build: true
```

### Python CI (`python-ci.yml`)

```yaml
jobs:
  test:
    uses: iitdeveloper-git/deploykit/.github/workflows/python-ci.yml@v1
    with:
      python-version: '3.11'
      requirements-file: 'requirements.txt'
      run-lint: true
      run-test: true
      test-command: 'pytest --cov=src'
```

### Docker Build & Publish (`docker-build.yml`)

```yaml
jobs:
  build-and-push:
    uses: iitdeveloper-git/deploykit/.github/workflows/docker-build.yml@v1
    with:
      image-name: ghcr.io/${{ github.repository }}
      push: true
      tags: latest
      platforms: linux/amd64,linux/arm64
    secrets:
      REGISTRY_USERNAME: ${{ github.actor }}
      REGISTRY_PASSWORD: ${{ secrets.GITHUB_TOKEN }}
```

### Security Scan (`security-scan.yml`)

```yaml
jobs:
  security-audit:
    uses: iitdeveloper-git/deploykit/.github/workflows/security-scan.yml@v1
    with:
      scan-type: 'fs'
      severity: 'CRITICAL,HIGH'
      exit-code: '1' # Fails CI if CRITICAL/HIGH vulnerabilities exist
```

### SSH Docker Deployment (`deploy-ssh-docker.yml`)

```yaml
jobs:
  deploy:
    uses: iitdeveloper-git/deploykit/.github/workflows/deploy-ssh-docker.yml@v1
    with:
      environment: 'Production'
      environment-url: 'https://app.example.com'
      compose-directory: '/opt/app'
      compose-file: 'docker-compose.yml'
      image-tag: ${{ github.sha }}
      health-check-url: 'https://app.example.com/health'
    secrets:
      DEPLOY_HOST: ${{ secrets.DEPLOY_HOST }}
      DEPLOY_USER: ${{ secrets.DEPLOY_USER }}
      DEPLOY_SSH_KEY: ${{ secrets.DEPLOY_SSH_KEY }}
```

Check out [`examples/`](examples/) for full end-to-end caller workflow files.

---

## 🤖 AutoDeploy Agent Skill

DeployKit includes the **`iitdeveloper-autodeploy`** AI Agent skill. Any AI coding assistant (like Antigravity) can use this skill to automatically inspect any repository and configure production CI/CD pipelines powered by `iitdeveloper-git/deploykit@v1`.

### How to Use with Your Agent:

1. Copy the skill into your project's `.agents/skills/` directory:
   ```bash
   cp -r skills/iitdeveloper-autodeploy .agents/skills/
   ```
2. Prompt your coding agent:
   > *"Use the `iitdeveloper-autodeploy` skill to set up CI/CD and deployment for this project."*
3. The agent will automatically detect the language/framework, assemble the least-privilege workflow files, configure Telegram notifications, and output the required GitHub secrets list.

---

## 🔑 Secrets & Configuration Setup

To enable notifications across all repositories without repetitive manual configuration, configure secrets at the **Organization Level**:

1. Go to **Organization Settings** → **Secrets and variables** → **Actions**.
2. Add the following repository secrets:
   - `TELEGRAM_BOT_TOKEN`: Bot token from [@BotFather](https://t.me/BotFather).
   - `TELEGRAM_CHAT_ID`: Telegram group or channel chat ID (e.g. `-1001234567890`).
3. Set **Repository access** → **All repositories** (or select specific repos).

---

## 📋 Action Inputs Reference

### `actions/telegram-notify` & `telegram-notify.yml`

| Input | Required | Default | Description |
|---|:---:|---|---|
| `bot_token` / `TELEGRAM_BOT_TOKEN` | ✅ | — | Telegram Bot HTTP API Token (pass via secret). |
| `chat_id` / `TELEGRAM_CHAT_ID` | ✅ | — | Target Group/Channel Chat ID (e.g. `-100xxxxxxx`). |
| `message_thread_id` | ➖ | `""` | Telegram Topic / Thread ID (for Supergroups with forum topics enabled). |
| `app_name` | ➖ | `repo name` | Application or microservice name. |
| `environment` | ➖ | `'Production'` | Environment (e.g. `Production`, `Staging`, `CI / Tests`). |
| `status` | ➖ | `'success'` | Job status (`success`, `failure`, `cancelled`, `timed_out`). |
| `release_tag` | ➖ | `""` | Release tag or SemVer string (e.g. `v1.2.0`). |
| `app_url` | ➖ | `""` | Live application or dashboard URL. |
| `custom_message` | ➖ | `""` | Optional markdown/custom release notes. |

---

## 🏷 Versioning & Release Strategy

DeployKit adheres strictly to [Semantic Versioning (SemVer)](https://semver.org/).

### Recommended Pinning

- **Pinned Major Release (Recommended):**
  ```yaml
  uses: iitdeveloper-git/deploykit/.github/workflows/node-ci.yml@v1
  ```
  *Receives backwards-compatible feature updates and security patches automatically.*

- **Pinned Exact Patch (Highest Determinism):**
  ```yaml
  uses: iitdeveloper-git/deploykit/.github/workflows/node-ci.yml@v1.0.0
  ```

- **Pinned Full Commit SHA (Maximum Security & Zero-Trust):**
  ```yaml
  uses: iitdeveloper-git/deploykit/.github/workflows/node-ci.yml@<FULL_COMMIT_SHA>
  ```

---

## 🔒 Security & Governance

- **Least Privilege:** Reusable workflows define explicit minimum permissions (`contents: read`).
- **No Token Logging:** Tokens are strictly supplied via environment variables and never printed or exposed in logs.
- **Dependency Minimization:** Scripts use the Python Standard Library to avoid third-party supply chain vulnerabilities.
- For vulnerability reports and security policy, see [SECURITY.md](SECURITY.md).

---

## 📁 Repository Structure

```
deploykit/
├── .agents/
│   └── skills/
│       └── iitdeveloper-autodeploy/    # Workspace AI Agent AutoDeploy skill
│           ├── SKILL.md
│           └── references/
│               ├── examples.md
│               └── secrets.md
├── .github/
│   ├── assets/
│   │   └── banner.jpg                  # Project visual banner
│   ├── dependabot.yml                  # Weekly automated dependency maintenance
│   ├── ISSUE_TEMPLATE/                 # Structured bug report & feature request forms
│   │   ├── bug_report.yml
│   │   ├── feature_request.yml
│   │   └── config.yml
│   ├── pull_request_template.md        # Pull request template
│   └── workflows/
│       ├── ci.yml                      # Repository CI (actionlint, linting, tests)
│       ├── deploy-ssh-docker.yml       # Reusable SSH / Docker Compose deploy workflow
│       ├── docker-build.yml            # Reusable Docker build & publish workflow
│       ├── node-ci.yml                 # Reusable Node.js CI workflow
│       ├── python-ci.yml               # Reusable Python CI workflow
│       ├── security-scan.yml           # Reusable Security scan workflow
│       └── telegram-notify.yml         # Reusable Telegram notification workflow
├── actions/
│   └── telegram-notify/
│       ├── action.yml                  # Telegram notification composite action manifest
│       └── send.py                     # Zero-dependency Python dispatcher script
├── examples/                           # Ready-to-use caller workflow templates
│   ├── docker-build-push.yml
│   ├── full-deploy-pipeline.yml
│   ├── nodejs-ci.yml
│   ├── python-ci.yml
│   ├── security-scan.yml
│   └── telegram-notification.yml
├── skills/
│   └── iitdeveloper-autodeploy/        # Exportable Agent skill bundle
│       ├── SKILL.md
│       └── references/
│           ├── examples.md
│           └── secrets.md
├── tests/
│   ├── __init__.py
│   ├── test_telegram_send.py           # Unit test suite for Telegram notifications (100% branch coverage)
│   └── test_workflows_schema.py        # Schema & least-privilege security tests
├── CHANGELOG.md                        # Semantic release changelog
├── CODE_OF_CONDUCT.md                  # Contributor Covenant v2.1
├── CONTRIBUTING.md                     # Contribution & local testing guide
├── LICENSE                             # MIT License
├── README.md                           # Documentation & quick start guide
└── SECURITY.md                         # Security and vulnerability reporting policy
```

---

## 🔄 Migration Guide from Shared Workflows

DeployKit is the evolution of `iitdeveloper-git/shared-workflows`. To migrate existing application repositories to DeployKit, simply update workflow and action references:

| Old Reference | New DeployKit Reference |
|---|---|
| `iitdeveloper-git/shared-workflows/actions/telegram-notify@v1` | `iitdeveloper-git/deploykit/actions/telegram-notify@v1` |
| `iitdeveloper-git/shared-workflows/.github/workflows/telegram-notify.yml@v1` | `iitdeveloper-git/deploykit/.github/workflows/telegram-notify.yml@v1` |
| `iitdeveloper-git/shared-workflows/.github/workflows/node-ci.yml@v1` | `iitdeveloper-git/deploykit/.github/workflows/node-ci.yml@v1` |
| `iitdeveloper-git/shared-workflows/.github/workflows/python-ci.yml@v1` | `iitdeveloper-git/deploykit/.github/workflows/python-ci.yml@v1` |
| `iitdeveloper-git/shared-workflows/.github/workflows/docker-build.yml@v1` | `iitdeveloper-git/deploykit/.github/workflows/docker-build.yml@v1` |
| `iitdeveloper-git/shared-workflows/.github/workflows/security-scan.yml@v1` | `iitdeveloper-git/deploykit/.github/workflows/security-scan.yml@v1` |

> **Compatibility Guarantee:** All inputs, secrets, and outputs in DeployKit `@v1` are 100% compatible with `shared-workflows@v1`. Only the repository path needs to be updated.

---

## 🤝 Contributing

We welcome community contributions! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before opening pull requests.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) &copy; 2026 iitdeveloper-git and contributors.
