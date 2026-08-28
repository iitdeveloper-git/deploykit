# AutoDeploy Secrets Setup Guide

This guide details the standard secrets required by **DeployKit** (`iitdeveloper-git/deploykit@v1`) and downstream deployment jobs.

---

## 1. Notification Secrets

### Telegram
| Secret Name | Level | Description | How to obtain |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Organization or Repo | Telegram HTTP Bot API Token | Message [@BotFather](https://t.me/BotFather) on Telegram and create a bot (`/newbot`). |
| `TELEGRAM_CHAT_ID` | Organization or Repo | Telegram Group or Channel Chat ID | Add bot to group/channel, then get chat ID (e.g. `-1001234567890`) via `@getidsbot` or API. |

### Slack / Microsoft Teams / Discord / Generic Webhook
| Secret Name | Level | Description | How to obtain |
|---|---|---|---|
| `WEBHOOK_URL` | Organization or Repo | Incoming Webhook endpoint URL | Obtain Webhook URL from Slack Apps, MS Teams Connectors, Discord Channel Integrations, or your custom webhook receiver. |

> [!TIP]
> Setting notification secrets at the **Organization level** allows all repositories in the organization to automatically inherit alert capabilities.

---

## 2. Remote Server Deployment Secrets (SSH / VPS / Docker Compose)

When deploying to a remote host via `deploy-ssh-docker.yml`:

| Secret Name | Level | Description |
|---|---|---|
| `DEPLOY_HOST` | Repo / Environment | Server IP address or hostname (e.g. `203.0.113.10` or `api.example.com`). |
| `DEPLOY_USER` | Repo / Environment | SSH deployment user (e.g. `ubuntu`, `deploy`, `root`). |
| `DEPLOY_SSH_KEY` | Repo / Environment | Private SSH Key (ed25519 or RSA) with access to `DEPLOY_HOST`. |
| `DEPLOY_SSH_KNOWN_HOSTS` | Repo / Environment | Public host key (e.g. output from `ssh-keyscan`) for strict host verification. |
| `DEPLOY_PORT` | Repo / Environment | SSH port (defaults to `22` if omitted). |
| `REGISTRY_USERNAME` | Repo / Environment | Container registry username (optional). |
| `REGISTRY_PASSWORD` | Repo / Environment | Container registry password or token (optional). |

---

## 3. Container Registry Secrets

When publishing Docker containers via `docker-build.yml`:

| Secret Name | Level | Description |
|---|---|---|
| `GITHUB_TOKEN` | Built-in | Automatically provided by GitHub Actions runner with `packages: write` permission for GHCR (`ghcr.io`). |
| `DOCKERHUB_USERNAME` | Organization or Repo | Docker Hub account username (if using Docker Hub). |
| `DOCKERHUB_TOKEN` | Organization or Repo | Docker Hub Personal Access Token (PAT). |
