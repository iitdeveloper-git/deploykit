# Shared CI/CD Workflows & Actions (`iitdeveloper-git`)

Centralized, reusable GitHub Actions and workflows for all `iitdeveloper-git` projects.

---

## 📱 Telegram Release & Deployment Notification

### Method A: Composite Action (Recommended for existing jobs)

Add this step to the end of your deployment job in any project repository:

```yaml
      - name: Send Telegram Notification
        if: always()
        uses: iitdeveloper-git/shared-workflows/actions/telegram-notify@main
        with:
          bot_token: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          chat_id: ${{ secrets.TELEGRAM_CHAT_ID }}
          app_name: 'Growixa'
          environment: 'Production' # or 'UAT / Staging'
          status: ${{ job.status }} # passes 'success' or 'failure'
          release_tag: ${{ steps.vars.outputs.tag }}
          app_url: 'https://growixa.iitdeveloper.com'
```

### Method B: Reusable Workflow (`workflow_call`)

Call the notification workflow as a separate job:

```yaml
  notify:
    name: Telegram Notification
    needs: [deploy]
    if: always()
    uses: iitdeveloper-git/shared-workflows/.github/workflows/telegram-notify.yml@main
    with:
      app_name: 'Growixa'
      environment: 'Production'
      status: ${{ needs.deploy.result }}
      release_tag: ${{ needs.deploy.outputs.tag }}
      app_url: 'https://growixa.iitdeveloper.com'
    secrets:
      TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
      TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
```

---

## 🔑 Required Secrets Setup

To avoid adding secrets to each repo manually, configure them once at the **Organization Level**:

1. Go to **Organization Settings** ➔ **Secrets and variables** ➔ **Actions**.
2. Add the following repository secrets:
   - `TELEGRAM_BOT_TOKEN`: Bot token from `@BotFather`
   - `TELEGRAM_CHAT_ID`: Telegram Group/Channel ID (e.g. `-1001234567890`)
3. Select **Repository access** ➔ **All repositories**.

---

## 📋 Action Inputs Reference

| Input | Required | Default | Description |
|---|---|---|---|
| `bot_token` / `TELEGRAM_BOT_TOKEN` | Yes | — | Telegram Bot HTTP API Token |
| `chat_id` / `TELEGRAM_CHAT_ID` | Yes | — | Target Group/Channel Chat ID |
| `app_name` | Yes | — | Name of application (e.g. Growixa) |
| `environment` | Yes | — | Production, UAT, Staging |
| `status` | Yes | — | `success`, `failure`, or `cancelled` |
| `release_tag` | No | `""` | Release tag or version number |
| `app_url` | No | `""` | Live URL of the deployed application |
| `custom_message` | No | `""` | Additional notes or release message |
| `message_thread_id` | No | `""` | Telegram topic ID (if using group topics) |
