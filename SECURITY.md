# Security Policy

**DeployKit by IITDEVELOPER** (`iitdeveloper-git/deploykit`) is committed to ensuring the security of our reusable workflows, composite actions, and automation tooling for all downstream consumers.

---

## Supported Versions

We provide security updates and bug fixes for the following versions:

| Major Version | Supported          | Release Status |
| ------------- | ------------------ | -------------- |
| `v1.x`        | :white_check_mark: | Current Active |
| `< v1.0`      | :x:                | Deprecated     |

---

## Security Best Practices for Workflow Consumers

When using DeployKit workflows and composite actions in your repositories, we strongly recommend:

1. **Pin Versions or Commit SHAs:**
   Always pin actions/workflows to a major release tag (e.g., `@v1`) or full commit SHA rather than `@main` to prevent unexpected changes.
   
   ```yaml
   uses: iitdeveloper-git/deploykit/actions/telegram-notify@v1
   ```

2. **Principle of Least Privilege:**
   Explicitly specify minimal `permissions` required for your caller workflows:
   
   ```yaml
   permissions:
     contents: read
   ```

3. **Pass Secrets Securely:**
   Never hardcode sensitive tokens or keys in workflow files. Always reference GitHub Secrets:
   
   ```yaml
   bot_token: ${{ secrets.TELEGRAM_BOT_TOKEN }}
   chat_id: ${{ secrets.TELEGRAM_CHAT_ID }}
   ```

4. **Sanitize Inputs:**
   All scripts in DeployKit avoid direct shell interpolation of user inputs and utilize standard environment variable bindings and HTML/URI escaping.

---

## Reporting a Vulnerability

If you discover a security vulnerability or credential leak within this repository, **please do not open a public GitHub issue.**

Instead, please report it via one of the following methods:

1. **GitHub Private Security Advisory (Recommended):**
   Navigate to the **Security** tab of the repository and click **"Report a vulnerability"**.

2. **Email Security Team:**
   Send an email with detailed reproduction steps to [security@iitdeveloper.com](mailto:security@iitdeveloper.com).

### Information to Include
- Detailed description of the vulnerability.
- Steps or proof-of-concept workflow reproducing the issue.
- Potential impact and severity.
- Affected workflow or action files.

### Response Timeline
- **Initial Acknowledgement:** Within 48 hours.
- **Triage & Impact Assessment:** Within 5 business days.
- **Fix & Advisory Release:** Handled according to severity via semantic patch release (e.g. `v1.0.1`).
