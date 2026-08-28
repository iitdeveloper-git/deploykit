# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.4] - 2026-08-29

### Added
- **Reusable SSH Docker Deployment Workflow (`deploy-ssh-docker.yml`):** Added secure reusable workflow for VPS / Docker Compose deployments with GitHub Environment protection, SSH host key verification, least privilege, immutable tag/image releases, and automated post-deployment health check probes.
- **Workflow Schema & Security Test Suite (`test_workflows_schema.py`):** Added automated unit test validating workflow permissions, `workflow_call` triggers, and zero unpinned action refs.

### Fixed & Hardened
- **Node.js CI Failure Handling:** Replaced failure-suppressing `|| true` with clean script-existence detection; missing scripts are skipped cleanly, while failed scripts properly fail CI.
- **Python CI Dependency Installation:** Clean separation between `requirements.txt` (`pip install -r`) and `pyproject.toml` (`pip install .`) with zero suppressed errors.
- **AutoDeploy Skill Specification:** Added `license: MIT` and tags metadata to `SKILL.md` frontmatter, validated against Agent Skills specification, and updated blueprints with `deploy-ssh-docker.yml`.

---

## [1.0.3] - 2026-08-29

### Fixed & Hardened
- **Node.js CI:** Added full native support for `bun` via `oven-sh/setup-bun` alongside `npm`, `yarn`, and `pnpm`.
- **Python CI:** Fixed `pyproject.toml` dependency installation and removed silent error suppressions so linter and test failures properly trigger job failures.
- **Telegram Reusable Workflow:** Explicitly locked sparse-checkout ref to `v1` to prevent unversioned default branch execution.
- **Contract Consistency:** Enforced consistent `required: true` contracts for Telegram secrets.
- **Production Security Gates:** Configured security scan examples to use `exit-code: '1'` to enforce production security blocking.
- **AutoDeploy Skill & Docs:** Fixed invalid `uses:` syntax in skill definitions, updated release badges, and documented the skill in README, TOC, and repository structure.

---

## [1.0.2] - 2026-08-29

### Added
- **AI Agent Skill (`iitdeveloper-autodeploy`):** Added the standard `iitdeveloper-autodeploy` skill with complete reference documentation and example blueprints, enabling coding agents to automatically configure caller repositories with `iitdeveloper-git/shared-workflows@v1`.

---

## [1.0.1] - 2026-08-29

### Security & Hardening
- **Third-Party Action Pinning:** Pinned all GitHub Actions across reusable workflows (`checkout`, `setup-python`, `setup-node`, `docker`, `trivy-action`, `actionlint`) to immutable full commit SHAs with version comments.
- **Least Privilege:** Reduced permissions in `security-scan.yml` to `contents: read`.
- **Dependabot Integration:** Added automated weekly updates for GitHub Actions and Python dependencies.
- **Coverage Enforcement:** Configured CI to strictly enforce `--branch` and `--fail-under=100` code coverage.

---

## [1.0.0] - 2026-08-29

### Added
- **Telegram Notification Composite Action** (`actions/telegram-notify/action.yml`):
  - Send rich HTML deployment & CI status notifications via Telegram Bot API.
  - Multi-status support: `success`, `failure`, and `cancelled`.
  - Automatic fallback to plain text if Telegram HTML parser rejects malformed inputs.
  - Support for Telegram forum topics (`message_thread_id`).
  - Python-based engine (`send.py`) with zero third-party dependencies.
- **Telegram Notification Reusable Workflow** (`.github/workflows/telegram-notify.yml`):
  - Clean `workflow_call` interface for caller pipelines.
  - Principle of least privilege with `permissions: contents: read`.
- **Full CI/CD Quality Suite** (`.github/workflows/ci.yml`):
  - Actionlint and Yamllint automated validation.
  - Python unit test suite with 100% code branch coverage.
- **Enterprise Reusable Workflows**:
  - `node-ci.yml`: Reusable Node.js build, test, and caching pipeline.
  - `python-ci.yml`: Reusable Python test and linting pipeline.
  - `docker-build.yml`: Multi-arch Docker build & push with Buildx & security scanning.
  - `security-scan.yml`: Trivy vulnerability and secret scanner.
- **Reference Examples** in `examples/`:
  - Starter templates for Node.js, Python, Docker, security scanning, and multi-stage production deployment pipelines with Telegram alerts.
- **OSS Community Governance**:
  - `LICENSE` (MIT)
  - `README.md` with complete documentation, architecture, and guides
  - `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`
  - GitHub issue templates and PR template
