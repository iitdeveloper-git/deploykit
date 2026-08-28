# Contributing to DeployKit

Thank you for your interest in contributing to **DeployKit by IITDEVELOPER** (`iitdeveloper-git/deploykit`)! We welcome contributions, bug reports, workflow additions, and improvements from the open source community.

---

## Code of Conduct

All contributors and maintainers are expected to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/<your-username>/deploykit.git
   cd deploykit
   ```
3. **Create a topic branch** from `main`:
   ```bash
   git checkout -b feat/my-new-feature
   ```

---

## Development & Guidelines

### 1. Security & Environment Principles
- **No Secrets in Repo:** Never commit credentials, tokens, webhook URLs, internal hostnames, or private keys.
- **Least Privilege:** Always specify explicit `permissions` on reusable workflows (`contents: read`).
- **Input Sanitization:** Avoid direct shell interpolation in scripts (e.g. `"${{ inputs.something }}"`). Always pass inputs via environment variables.
- **Zero Hardcoded Infrastructure:** All workflows and actions must be modular, configurable, and vendor/organization-agnostic.

### 2. Testing Locally
- **Unit Tests & 100% Branch Coverage:**
  ```bash
  python3 -m coverage run --branch -m unittest discover -s tests -p "test_*.py"
  python3 -m coverage report --fail-under=100 -m
  ```
- **Linting & Validation:**
  - Verify action manifests and workflow files using [actionlint](https://github.com/rhysd/actionlint).
  - Verify Python code with [ruff](https://docs.astral.sh/ruff/).
  - Verify YAML formatting with [yamllint](https://yamllint.readthedocs.io/).

---

## Submitting Pull Requests

1. Commit your changes using conventional commit messages (e.g., `feat(deploy): add health check probe timeout`, `fix(security): sanitize link payloads`).
2. Push your topic branch to your fork.
3. Open a Pull Request against the `main` branch of `iitdeveloper-git/deploykit`.
4. Ensure all CI checks (linting, testing, action validation) pass.
5. Maintainers will review your PR and provide constructive feedback.

---

## Release & Versioning Policy

We follow [Semantic Versioning (SemVer)](https://semver.org/):
- **Major (`v1.0.0` -> `v2.0.0`):** Breaking changes to input parameter names, required secrets, or minimum runner requirements.
- **Minor (`v1.0.0` -> `v1.1.0`):** New reusable workflows, new non-breaking action inputs, or feature enhancements.
- **Patch (`v1.0.0` -> `v1.0.1`):** Bug fixes, security patches, documentation updates.

We maintain moving major tags (e.g., `v1`) pointing to the latest stable release of that major version.
