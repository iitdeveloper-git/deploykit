# AutoDeploy Secrets Setup Guide

This guide details the standard secrets required by `iitdeveloper-git/shared-workflows@v1` and deployment jobs.

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

## 2. Remote Server Deployment Secrets (SSH / VM)

When deploying directly to a Linux server:

| Secret Name | Level | Description |
|---|---|---|
| `DEPLOY_HOST` | Repo / Environment | Server IP address or hostname (e.g. `203.0.113.10` or `api.example.com`). |
| `DEPLOY_USER` | Repo / Environment | SSH deployment user (e.g. `ubuntu`, `deploy`, `root`). |
| `DEPLOY_SSH_KEY` | Repo / Environment | Private SSH Key (ed25519 or RSA) with access to `DEPLOY_HOST`. |
| `DEPLOY_PORT` | Repo / Environment | SSH port (defaults to `22` if omitted). |

---

## 3. Container Registry Secrets

When publishing Docker containers:

| Secret Name | Level | Description |
|---|---|---|
| `GITHUB_TOKEN` | Built-in | Automatically provided by GitHub Actions runner with `packages: write` permission for GHCR (`ghcr.io`). |
| `DOCKERHUB_USERNAME` | Organization or Repo | Docker Hub account username (if using Docker Hub). |
| `DOCKERHUB_TOKEN` | Organization or Repo | Docker Hub Personal Access Token (PAT). |
