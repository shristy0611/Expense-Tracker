# Project Rules

These rules are **non-negotiable** to ensure code quality, consistency, and reliability.

## 1. Code Completeness
- **No placeholders**: Never commit `TODO`, `FIXME`, or incomplete stubs. Every function and module must be fully implemented before merging.
- **SOTA practices**: Use current, state-of-the-art libraries and design patterns. Remove deprecated or outdated code.

## 2. Testing & Verification
- **Unit tests required**: Every new feature, bug fix, or refactor must include unit tests. Aim for high coverage (>90%).
- **Automated CI**: All tests must pass in CI (GitHub Actions) on every PR. Merging is only allowed on a green build.

## 3. Documentation
- **Docstrings and comments**: Each function, class, and module must have clear docstrings describing purpose, inputs, and outputs.
- **Maintain docs**: Update `planning.md`, `rules.md`, and any design documents as decisions evolve.

## 4. Commit & Review Workflow
- **Atomic commits**: Keep commits small and focused, with descriptive messages.
- **Peer review**: All PRs require at least one peer review. No self-merging without review.

## 5. Security & Configuration
- **No secrets in code**: Secrets/config must live in environment variables (`.env`). Do not commit any secrets.
- **Environment separation**: Ensure clear separation of `dev`, `test`, and `prod` configurations.

## 6. Deployment & Infrastructure
- **Container consistency**: Docker images must be reproducible with pinned dependencies. Use `docker-compose` for local dev.
- **Staging validation**: Deploy first to staging, run smoke tests, then promote to production.

## 7. Collaboration & Continual Improvement
- **Retro & feedback**: After each phase, hold a brief retrospective to capture lessons learned.
- **Keep it clean**: Refactor code exceeding 300 lines. Remove dead code promptly.
