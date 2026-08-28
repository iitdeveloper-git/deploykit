# Changelog

All notable changes to **DeployKit** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [1.0.0] - 2026-08-29

### Added
- **Initial Release of DeployKit by IITDEVELOPER:**
  - Production-grade, secure CI/CD, release automation, and deployment library for GitHub Actions.
- **Reusable Workflows (`.github/workflows/`):**
  - `node-ci.yml`: Multi-version Node.js CI pipeline with native package manager support (`npm`, `yarn`, `pnpm`, `bun`), caching, linting, tests, and builds.
  - `python-ci.yml`: Python test and linting pipeline with pip caching, pyproject.toml / requirements.txt support, and ruff integration.
  - `docker-build.yml`: Multi-arch Docker container build, tag, and publish with Buildx and registry authentication.
  - `deploy-ssh-docker.yml`: Secure VPS / Docker Compose deployment workflow with SSH host key verification, immutable image/tag deployment, post-deploy health check probes, and rollback safety.
  - `security-scan.yml`: Trivy filesystem and container vulnerability scanning with configurable production security gates (`exit-code: '1'`).
  - `telegram-notify.yml`: Reusable standalone workflow for rich Telegram deployment and CI notifications.
  - `ci.yml`: Self-validating quality pipeline with Actionlint, Yamllint, and 100% statement and branch coverage enforcement.
- **Composite Actions (`actions/`):**
  - `telegram-notify`: Standard library Python notification dispatcher with multi-status formatting (`success`, `failure`, `cancelled`, `timed_out`), HTML entity escaping, and plain-text fallback.
- **AI Agent Skill (`skills/iitdeveloper-autodeploy`):**
  - Automated project inspection and deployment configuration skill for AI coding assistants.
- **Community Governance & Security:**
  - `LICENSE` (MIT)
  - `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`
  - GitHub issue templates and pull request template
  - Automated Dependabot dependency updates
