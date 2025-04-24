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

# SmartReceipt Detailed Roadmap

## Phase 0: Pre-Planning (1 week)
- Assemble the team, secure compute/storage, obtain API keys
- Set up dev environments, Git repo, CI/CD framework

## Phase 1: Planning, Design, & Data Collection (2 weeks)
- Define requirements, scope, and success metrics
- Design system architecture and data flow (OCR → RAG → LLM)
- Plan DB schema for receipts, extracted fields, FAISS index
- Select tech stack: Python 3.10+, Flask, SQLAlchemy, Tesseract, FAISS, Gemini
- Create detailed timeline and milestones
- Collect diverse receipt dataset; manually label sample set

## Iteration 1: MVP Development (4 weeks)
- Scaffold Flask app and SQLAlchemy models
- Implement OCR agent with Tesseract
- Build regex-based field extraction (merchant, date, total)
- Expose REST endpoints (`/upload`, `/receipts`)
- Detect basic currency symbols ($, ¥, €, etc.)
- Write unit/integration tests; deploy MVP to test env

## Iteration 2: RAG Integration (4 weeks)
- Choose embedding model (e.g. SentenceTransformer)
- Build FAISS index over past receipts
- Retrieve top‑k similar receipts as context
- Inject RAG context into AI prompt for parsing
- Update tests, docs, and CI to cover RAG features

## Iteration 3: LLM Enhancement (4 weeks)
- Integrate Gemini LLM for advanced parsing and categorization
- Optimize prompts with retrieved context
- Add self‑healing anomaly detection (flag totals mismatch)
- Expand test suite for LLM-driven logic

## Iteration 4: Advanced Features (4 weeks)
- Implement dynamic currency conversion and locale formatting
- Auto‑categorization and intelligent note generation
- Enable user feedback loop for continuous learning
- Extend API (`/categories`, `/analytics`); update docs

## Iteration 5: Final Testing & Deployment (4 weeks)
- Achieve 100% coverage: unit, integration, edge, stress tests
- Containerize with Docker & docker-compose
- Configure DockerHub automated builds
- Deploy to staging→production; set up monitoring/alerts
- Publish full API specs and user guide

## Post‑Deployment: Maintenance & Evolution (Ongoing)
- Monitor performance, gather user feedback
- Fix bugs and add features per roadmap
- Refresh FAISS index and retrain models as data grows

### Key Principles
- **Modularity**: Pluggable agents (OCR, Categorizer, Currency, Verifier, Reporter)
- **Testing**: 100% automated test coverage; CI on every PR
- **Documentation**: Real-time logs in `planning.md` and `rules.md`
- **Data‑Driven**: Use receipt corpus for continuous AI improvements
- **Scalability**: Design for high volumes
- **Security**: Thread‑safe key rotation, secure configs

### Next Steps
1. Adopt this roadmap in `planning.md` and enforce `rules.md`
2. Delete all legacy files and start fresh under `app/` per plan
3. Execute Phase 0 immediately to confirm resources and kickoff
