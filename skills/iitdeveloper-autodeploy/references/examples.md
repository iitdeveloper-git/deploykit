# AutoDeploy Pipeline Examples

This reference provides drop-in pipeline blueprints configured for `iitdeveloper-git/shared-workflows@v1`.

---

## 1. Node.js / Next.js Full CI/CD with Telegram Notifications

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
    uses: iitdeveloper-git/shared-workflows/.github/workflows/node-ci.yml@v1
    with:
      node-version: '20'
      package-manager: 'npm'
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

      - name: 📢 Telegram Notification
        if: always()
        uses: iitdeveloper-git/shared-workflows/actions/telegram-notify@v1
        with:
          bot_token: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          chat_id: ${{ secrets.TELEGRAM_CHAT_ID }}
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
    uses: iitdeveloper-git/shared-workflows/.github/workflows/python-ci.yml@v1
    with:
      python-version: '3.11'
      requirements-file: 'requirements.txt'
      run-lint: true
      run-test: true

  docker-publish:
    name: Build & Push Container
    needs: [test]
    uses: iitdeveloper-git/shared-workflows/.github/workflows/docker-build.yml@v1
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
    uses: iitdeveloper-git/shared-workflows/.github/workflows/telegram-notify.yml@v1
    with:
      app_name: 'Backend API Service'
      environment: 'Production Container'
      status: ${{ needs.docker-publish.result }}
      release_tag: ${{ github.ref_name }}
    secrets:
      TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
      TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
```
