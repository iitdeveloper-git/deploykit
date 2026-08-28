# AutoDeploy Pipeline Examples (Powered by DeployKit)

This reference provides drop-in pipeline blueprints configured for `iitdeveloper-git/deploykit@v1`.

---

## 1. Node.js / Next.js Full CI/CD with Multi-Channel Notifications

```yaml
name: Production CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  ci:
    name: Run CI Suite
    uses: iitdeveloper-git/deploykit/.github/workflows/node-ci.yml@v1
    with:
      node-version: '20'
      package-manager: 'pnpm' # npm, yarn, pnpm, bun
      run-lint: true
      run-test: true
      run-build: true

  deploy:
    name: Deploy to Production
    needs: [ci]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    environment:
      name: Production
      url: https://app.example.com
    steps:
      - name: Checkout Code
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2

      - name: Deploy Application
        run: |
          echo "Executing production deployment..."
          # Application deployment commands

      - name: 📢 Multi-Channel Notification
        if: always()
        uses: iitdeveloper-git/deploykit/actions/notify@v1
        with:
          channel: 'slack' # telegram, slack, teams, discord, webhook (or auto)
          webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
          app_name: 'Frontend Application'
          environment: 'Production'
          status: ${{ job.status }}
          app_url: 'https://app.example.com'
          custom_message: '🚀 Deployed latest changes to Production.'
```

---

## 2. Python / FastAPI Docker Build & Publish Pipeline

```yaml
name: Python API Build & Publish

on:
  push:
    tags: ['v*.*.*']

permissions:
  contents: read
  packages: write

jobs:
  test:
    name: Test Suite
    uses: iitdeveloper-git/deploykit/.github/workflows/python-ci.yml@v1
    with:
      python-version: '3.11'
      requirements-file: 'requirements.txt'
      run-lint: true
      run-test: true

  docker-publish:
    name: Build & Push Container
    needs: [test]
    uses: iitdeveloper-git/deploykit/.github/workflows/docker-build.yml@v1
    with:
      image-name: ghcr.io/${{ github.repository }}
      push: true
      tags: |
        ghcr.io/${{ github.repository }}:${{ github.ref_name }}
        ghcr.io/${{ github.repository }}:latest
      platforms: linux/amd64,linux/arm64
    secrets:
      REGISTRY_USERNAME: ${{ github.actor }}
      REGISTRY_PASSWORD: ${{ secrets.GITHUB_TOKEN }}

  notify:
    name: Notification
    needs: [docker-publish]
    if: always()
    uses: iitdeveloper-git/deploykit/.github/workflows/notify.yml@v1
    with:
      app_name: 'Backend API Service'
      environment: 'Production Container'
      status: ${{ needs.docker-publish.result }}
      release_tag: ${{ github.ref_name }}
    secrets:
      TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
      TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
```

---

## 3. End-to-End VPS / Docker Compose Deployment with Rollback Guard

```yaml
name: Production VPS Deployment

on:
  push:
    branches: [main]

permissions:
  contents: read
  packages: write

jobs:
  # 1. CI Validation
  ci:
    name: Continuous Integration
    uses: iitdeveloper-git/deploykit/.github/workflows/node-ci.yml@v1
    with:
      node-version: '20'
      package-manager: 'pnpm'

  # 2. Production Security Gate (Blocks on Critical/High)
  security:
    name: Security Vulnerability Scan
    needs: [ci]
    uses: iitdeveloper-git/deploykit/.github/workflows/security-scan.yml@v1
    with:
      scan-type: 'fs'
      severity: 'CRITICAL,HIGH'
      exit-code: '1'

  # 3. Build Container Image
  build-container:
    name: Build Container Image
    needs: [security]
    uses: iitdeveloper-git/deploykit/.github/workflows/docker-build.yml@v1
    with:
      image-name: ghcr.io/${{ github.repository }}
      push: true
      tags: |
        ghcr.io/${{ github.repository }}:${{ github.sha }}
        ghcr.io/${{ github.repository }}:latest
    secrets:
      REGISTRY_USERNAME: ${{ github.actor }}
      REGISTRY_PASSWORD: ${{ secrets.GITHUB_TOKEN }}

  # 4. Deploy to Remote Server via SSH & Docker Compose with Rollback Guard
  deploy:
    name: Deploy to Production Host
    needs: [build-container]
    uses: iitdeveloper-git/deploykit/.github/workflows/deploy-ssh-docker.yml@v1
    with:
      environment: 'Production'
      environment-url: 'https://app.example.com'
      compose-directory: '/opt/app'
      compose-file: 'docker-compose.prod.yml'
      service-name: 'api'
      image-tag: ${{ github.sha }}
      health-check-url: 'https://app.example.com/api/health'
      rollback-on-failure: true
    secrets:
      DEPLOY_HOST: ${{ secrets.DEPLOY_HOST }}
      DEPLOY_USER: ${{ secrets.DEPLOY_USER }}
      DEPLOY_SSH_KEY: ${{ secrets.DEPLOY_SSH_KEY }}
      DEPLOY_SSH_KNOWN_HOSTS: ${{ secrets.DEPLOY_SSH_KNOWN_HOSTS }}
      DEPLOY_PORT: ${{ secrets.DEPLOY_PORT }}
      REGISTRY_USERNAME: ${{ github.actor }}
      REGISTRY_PASSWORD: ${{ secrets.GITHUB_TOKEN }}

  # 5. Multi-Channel Status Notification
  notify:
    name: Telegram / Slack Notification
    needs: [deploy]
    if: always()
    uses: iitdeveloper-git/deploykit/.github/workflows/notify.yml@v1
    with:
      app_name: 'Production API'
      environment: 'Production'
      status: ${{ needs.deploy.result }}
      app_url: 'https://app.example.com'
    secrets:
      TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
      TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
      WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```
