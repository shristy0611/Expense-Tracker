# Coding Pattern Preferences
- Always prefer simple solutions
- Avoid duplication of code whenever possible, which means checking for other areas of the codebase that might already have similar code and functionality
- Write code that takes into account the different environments: dev, test, and prod
- You are careful to only make changes that are requested or you are confident are well understood and related to the change being requested
- When fixing an issue or bug, do not introduce a new pattern or technology without first exhausting all options for the existing implementation. And if you finally do this, make sure to remove the old implementation afterwards so we don't have duplicate logic.
- Keep the codebase very clean and organized
- Avoid writing scripts in files if possible, especially if the script is likely only to be run once
- Avoid having files over 200-300 lines of code. Refactor at that point.
- Mocking data is only needed for tests, never mock data for dev or prod
- Never add stubbing or fake data patterns to code that affects the dev or prod environments
- Never overwrite my .env file without first asking and confirming
- Never forget today's date. The year is 2025 and month is April.

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
