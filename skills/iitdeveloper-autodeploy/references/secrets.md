# AutoDeploy Secrets Setup Guide

This guide details the standard secrets required by **DeployKit** (`iitdeveloper-git/deploykit@v1`) and downstream deployment jobs.

---

## 1. Telegram Notification Secrets

To send deployment and CI status alerts:

| Secret Name | Level | Description | How to obtain |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Organization or Repo | Telegram HTTP Bot API Token | Message [@BotFather](https://t.me/BotFather) on Telegram and create a bot (`/newbot`). |
| `TELEGRAM_CHAT_ID` | Organization or Repo | Telegram Group or Channel Chat ID | Add bot to group/channel, then get chat ID (e.g. `-1001234567890`) via `@getidsbot` or API. |

> [!TIP]
> Setting `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` at the **Organization level** allows all repositories in the organization to automatically inherit notification capabilities without individual configuration.

---

## 2. Remote Server Deployment Secrets (SSH / VPS / Docker Compose)

When deploying to a remote host via `deploy-ssh-docker.yml`:

| Secret Name | Level | Description |
|---|---|---|
| `DEPLOY_HOST` | Repo / Environment | Server IP address or hostname (e.g. `203.0.113.10` or `api.example.com`). |
| `DEPLOY_USER` | Repo / Environment | SSH deployment user (e.g. `ubuntu`, `deploy`, `root`). |
| `DEPLOY_SSH_KEY` | Repo / Environment | Private SSH Key (ed25519 or RSA) with access to `DEPLOY_HOST`. |
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
