# Project Planning Document

## Overview

Rebuild the codebase from scratch after previous failures, focusing on precision, clarity, and state-of-the-art practices.

## Step-by-Step Plan

### Phase 1: Setup
- [ ] Define project scope and objectives
- [ ] Initialize a clean Git repository on `main`
- [ ] Draft `planning.md` and `rules.md`
- [ ] Research DockerHub integration best practices and versioning
- [ ] Identify key dependencies and SOTA technologies (OCR, RAG, AI APIs)

### Phase 2: Core Development
- [ ] Scaffold base application structure (Flask + SQLAlchemy)
- [ ] Implement and unit-test core modules:
  - Receipt upload and storage
  - OCR extraction agent
  - RAG + AI categorizer agent
  - Currency conversion agent
- [ ] Integrate synchronous, iterative commits with tests
- [ ] Configure CI (GitHub Actions) to run tests on PRs

### Phase 3: Testing & Iteration
- [ ] Write and maintain unit tests for every component
- [ ] Perform integration tests with sample receipts
- [ ] Conduct peer reviews on all PRs
- [ ] Document test results and update `planning.md` if scope changes

### Phase 4: Deployment
- [ ] Containerize with Dockerfile and docker-compose
- [ ] Configure and test DockerHub automated builds
- [ ] Deploy to staging, validate end-to-end flow
- [ ] Promote to production and monitor metrics/logs

## Timeline
- Phase 1: 2 days
- Phase 2: 5 days
- Phase 3: 3 days
- Phase 4: 2 days

## Lessons Learned & Risk Mitigation
- Analyze previous DockerHub failures and common pitfalls
- Enforce peer review to catch misconfigurations early
- Automate environment separation to avoid leaks
