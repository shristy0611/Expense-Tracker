# 🚀 Expense Tracker Project Roadmap

**Start Date:** 2025-04-24

---

## 📑 Table of Contents
- [Legend](#legend)
- [Summary & Key Milestones](#summary--key-milestones)
- [Progress Overview](#progress-overview)
- [Next Up](#next-up)
- [Current Phase: MVP Development](#current-phase-mvp-development)
- [Backlog & Future Phases](#backlog--future-phases)
- [How to Update This Roadmap](#how-to-update-this-roadmap)

---

## 🏷️ Legend
- ✅ = Complete
- 🔄 = In Progress
- ⏭️ = Next Up
- ⏳ = Blocked/Waiting
- [ ] = Not started
- [x] = Done

---

## 🏆 Summary & Key Milestones
- **MVP Target:** Full receipt OCR, tagging, and analytics with robust API, CI/CD, and docs
- **Current Focus:** Polish OpenAPI docs, CI validation, Postman collection, user guide
- **Recent Wins:**
  - Docker Compose, Dockerfile, and CI/CD pipeline refactored for modern best practices ✅
  - Swagger/OpenAPI auto-docs and CI schema validation integrated ✅
  - `/receipts` and `/upload` endpoints fully tested and documented ✅

---

## 📊 Progress Overview

| Phase                 | Status      | Key Deliverables                         |
|---------------------- |------------|------------------------------------------|
| Pre-Planning          | ✅ Done     | Repo, CI, envs, architecture             |
| Planning/Data         | ✅ Done     | DB schema, API spec, test plan           |
| MVP Development       | 🔄 Active   | Core endpoints, CI, docs, Docker         |
| RAG Integration       | [ ]        | Embeddings, FAISS, retrieval             |
| LLM Enhancement       | [ ]        | Gemini, prompt tuning, anomaly detect    |
| Advanced Features     | [ ]        | Currency, auto-categorization, feedback  |
| Final Testing/Deploy  | [ ]        | 100% coverage, staging, prod, monitoring |
| Maintenance           | [ ]        | Sprints, retrain, review, optimize       |

---

## ⏭️ Next Up
- [ ] Polish OpenAPI docs (Swagger UI), add more examples and schema details
- [ ] Validate OpenAPI schema in CI (already integrated, just polish spec)
- [ ] Prepare Postman collection and sample requests
- [ ] Draft user guide and quickstart README
- [ ] Final performance tuning (memory/CPU profiling)
- [ ] Resolve edge cases and error flows + tests

---

## 🔄 Current Phase: MVP Development (Days 22–49)

### Sprint Progress (Checkboxes = Done, Emoji = Status)

- [x] Scaffold Flask app, models, routes, schemas (Day 22)
- [ ] Implement `/upload` endpoint + local storage + unit tests (Day 23)
- [ ] Integrate SQLAlchemy models and Alembic migration + tests (Day 24)
- [ ] Stub OCR agent interface + tests (Day 25)
- [ ] Configure CI to run lint, format, migrations, tests (Day 26)
- [ ] Peer review Sprint 1 code, address comments (Day 27)
- [ ] Merge Sprint 1 branch, tag `v0.1-mvp` (Day 28)
- [x] Integrate Tesseract OCR, parse raw text + unit tests (Day 29)
- [x] Implement regex-based field extraction + tests (Day 30)
- [x] Add currency symbol detection, update models + tests (Day 31)
- [x] Build minimal UI or Postman mocks to validate endpoints (Day 32)
- [x] End-to-end integration tests on sample dataset (Day 33)
- [x] Performance benchmark: 50 receipts/minute (Day 34)
- [ ] Merge Sprint 2 branch, tag `v0.2-mvp` (Day 35)
- [x] `/receipts` list endpoint + pagination + tests (Day 36)
- [x] `/receipts/{id}` detail endpoint + tests (Day 37)
- [x] Add tags, notes fields, expand schema + tests (Day 38)
- [ ] Create Dockerfile & docker-compose for MVP + local dev smoke tests (Day 39)
- [ ] Update CI to build and push Docker image for staging (Day 40)
- [ ] Integration smoke tests in Docker environment (Day 41)
- [ ] Merge Sprint 3 branch, tag `v0.3-mvp` (Day 42)
- [x] Polish OpenAPI docs (Swagger UI) + CI schema validation (Day 43)
- [ ] Prepare Postman collection and sample requests (Day 44)
- [ ] Draft user guide and quickstart README (Day 45)
- [ ] Final performance tuning: memory, CPU profiling (Day 46)
- [ ] Resolve edge cases and error flows + tests (Day 47)
- [ ] Final code review and merge Sprint 4 (Day 48)
- [ ] Release MVP to staging, demo to stakeholders (Day 49)

---

## 🗂️ Backlog & Future Phases

### RAG Integration
- [ ] Select/benchmark embedding model (SentenceTransformer)
- [ ] Build/test FAISS index with 1000+ receipts
- [ ] Implement retrieval function, integrate into parsing flow
- [ ] Integration tests with retrieval context
- [ ] Update CI to include embedding build and RAG tests

### LLM Enhancement
- [ ] Integrate Gemini LLM, define prompt templates
- [ ] Optimize prompt engineering with context injection
- [ ] Implement self-healing anomaly detection
- [ ] Expand unit/integration tests for LLM outputs
- [ ] Demo advanced parsing accuracy (>95%)

### Advanced Features
- [ ] Dynamic currency conversion agent
- [ ] Auto-categorization, intelligent note generation
- [ ] Feedback loop: user corrections → retraining
- [ ] Extend API (`/categories`, `/analytics`) + Swagger tests
- [ ] Comprehensive documentation updates

### Final Testing & Deployment
- [ ] Achieve 100% test coverage (unit, integration, edge, stress)
- [ ] Containerize and automate DockerHub builds
- [ ] Deploy to staging: smoke/load tests
- [ ] Deploy to production: monitoring, alerts, rollback plans

### Maintenance & Evolution
- [ ] Weekly sprints: bugfixes, enhancements
- [ ] Monitor logs/metrics, optimize performance
- [ ] Retrain FAISS index monthly
- [ ] Bi-monthly roadmap reviews/retrospectives

---

## 📝 How to Update This Roadmap
- Mark tasks with `[x]` (done), `[ ]` (not started), or update with emoji for status.
- Move completed items to the top of each section.
- For new features or priorities, add to "Next Up" or "Backlog".
- Keep phase headers and table of contents up to date.
- Review every sprint and after major milestones.

---

*This roadmap is a living document. Update it as priorities shift, features are delivered, or new requirements emerge!*

**Day 11 (2025-05-04)**
- Document error codes, rate limits, retry strategies
- Define logging & metrics schema (Prometheus, ELK)

**Day 12 (2025-05-05)**
- Outline unit-test strategy: coverage targets per module
- Create test skeletons for core modules in `tests/`

**Day 13 (2025-05-06)**
- Prepare data pipeline design doc: ingestion → preprocessing → OCR input
- Select image augmentation strategies to improve OCR accuracy

**Day 14 (2025-05-07)**
- Sign off on architecture diagrams, API specs, test plan
- Freeze Phase 1 artifacts, assign tickets for implementation

### Week 2 (Days 15–21)

**Day 15 (2025-05-08)**
- Kick off Sprint Planning for Iteration 1 (MVP)
- Break down tasks into 2‑day micro‑sprints

**Day 16 (2025-05-09)**
- Set up project board (GitHub Projects / Jira)
- Assign initial user stories: upload, list, detail

**Day 17 (2025-05-10)**
- Final review of backlog, estimate story points
- Prepare demo checklist for MVP

**Days 18–19 (2025-05-11 to 2025-05-12)**
- Buffer for unplanned refinement and stakeholder review

**Day 20 (2025-05-13)**
- Final signoff on Phase 1 deliverables
- Ensure dev/test/prod `.env` templates are locked down

**Day 21 (2025-05-14)**
- Transition to Phase 2: MVP Development

---

## Phase 2: MVP Development (Iteration 1, 4 Weeks, Days 22–49)

### Sprint 1 (Week 1, Days 22–28)

- **Day 22 (2025-05-15):** ✅ Scaffold Flask app (`app/`, `models/`, `routes/`, `schemas/`)
- **Day 23 (2025-05-16):** [ ] Implement `/upload` endpoint + local storage + unit tests
- **Day 24 (2025-05-17):** [ ] Integrate SQLAlchemy models and Alembic migration + tests
- **Day 25 (2025-05-18):** [ ] Stub OCR agent interface + tests for interface behavior
- **Day 26 (2025-05-19):** [ ] Configure CI to run lint, format, migrations, tests (GitHub Actions check)
- **Day 26 (2025-05-19):** [ ] Verify CI passes on PR (GitHub Actions)
- **Day 27 (2025-05-20):** [ ] Peer review Sprint 1 code, address comments
- **Day 28 (2025-05-21):** [ ] Merge Sprint 1 branch, tag `v0.1-mvp` (CI/CD check: ensure all tests pass before merge)

### Sprint 2 (Week 2, Days 29–35)

- **Day 29 (2025-05-22):** ✅ Integrate Tesseract OCR, parse raw text + unit tests
- **Day 30 (2025-05-23):** ✅ Implement regex-based field extraction (merchant, date, total) + tests
- **Day 31 (2025-05-24):** ✅ Add currency symbol detection, update models + tests
- **Day 32 (2025-05-25):** ✅ Build minimal UI or Postman mocks to validate endpoints
- **Day 33 (2025-05-26):** ✅ End-to-end integration tests on sample dataset
- **Day 34 (2025-05-27):** ✅ Performance benchmark: 50 receipts/minute
- **Day 35 (2025-05-28):** [ ] Merge Sprint 2 branch, tag `v0.2-mvp` (CI/CD check: ensure all tests pass before merge)

### Sprint 3 (Week 3, Days 36–42)

- **Day 36 (2025-05-29):** ✅ `/receipts` list endpoint + pagination + tests

---

## [2025-04-24] CI/CD & DockerHub Improvements
- CI/CD workflow now runs all tests inside Docker for full prod/dev parity.
- DockerHub integration is automated: on push to main, images are built and pushed using GitHub Actions and DockerHub credentials stored as secrets.
- No secrets are ever committed to code.
- The obsolete `version` field has been removed from docker-compose.yml for future compatibility.
- **Day 37 (2025-05-30):** ✅ `/receipts/{id}` detail endpoint + tests
- **Day 38 (2025-05-31):** ✅ Add tags, notes fields, expand schema + tests
- **Day 39 (2025-06-01):** [ ] Create Dockerfile & docker-compose for MVP + local dev smoke tests (run locally, not in CI)
- **Day 40 (2025-06-02):** [ ] Update CI to build and push Docker image for staging (GitHub Actions + DockerHub integration)
- **Day 41 (2025-06-03):** [ ] Integration smoke tests in Docker environment (CI/CD check: run tests inside container, GitHub Actions)
- **Day 42 (2025-06-04):** [ ] Merge Sprint 3 branch, tag `v0.3-mvp` (CI/CD check: ensure all tests pass, Docker image built and pushed to DockerHub)

### Sprint 4 (Week 4, Days 43–49)

- **Day 43 (2025-06-05):** [ ] Polish OpenAPI docs (Swagger UI) + tests (CI: validate OpenAPI schema, GitHub Actions)
- **Day 44 (2025-06-06):** [ ] Prepare Postman collection and sample requests
- **Day 45 (2025-06-07):** [ ] Draft user guide and quickstart README
- **Day 46 (2025-06-08):** [ ] Final performance tuning: memory, CPU profiling
- **Day 47 (2025-06-09):** [ ] Resolve edge cases and error flows + tests
- **Day 48 (2025-06-10):** [ ] Final code review and merge Sprint 4 (CI/CD check: all tests pass, Docker image built and pushed to DockerHub)
- **Day 49 (2025-06-11):** [ ] Release MVP to staging, demo to stakeholders

---

## Phase 3: RAG Integration (Iteration 2, 4 Weeks)
**Week 5 (Days 50–56), Week 6 (57–63), Week 7 (64–70), Week 8 (71–77)**
- Select and benchmark embedding model (SentenceTransformer)
- Build and test FAISS index with 1000+ receipts
- Implement retrieval function and integrate into parsing flow
- Write integration tests with retrieval context
- Update CI to include embedding build and RAG tests
- Sprint reviews and merge at end of each week

---

## Phase 4: LLM Enhancement (Iteration 3, 4 Weeks)
**Weeks 9–12**
- Integrate Gemini LLM, define prompt templates
- Optimize prompt engineering with context injection
- Implement self‑healing anomaly detection (flag mismatches)
- Expand unit/integration tests to cover LLM outputs
- Demo advanced parsing accuracy (>95%)

---

## Phase 5: Advanced Features (Iteration 4, 4 Weeks)
**Weeks 13–16**
- Dynamic currency conversion agent: real‑time rates + locale formatting
- Auto‑categorization and intelligent note generation
- Feedback loop: user corrections → retraining pipeline
- Extend API: `/categories`, `/analytics` + Swagger tests
- Comprehensive documentation updates

---

## Phase 6: Final Testing & Deployment (Iteration 5, 4 Weeks)
**Weeks 17–20**
- Achieve 100% test coverage (unit, integration, edge, stress)
- Containerize and automate DockerHub builds
- Deploy to staging: run smoke and load tests
- Deploy to production: setup monitoring, alerts, rollback plans

---

## Post‑Deployment: Maintenance & Evolution (Ongoing)
- Weekly sprint cycles: prioritize bugs, enhancements
- Monitor logs & metrics, optimize performance
- Retrain FAISS index monthly with new data
- Bi‑monthly reviews: roadmap updates, retrospectives
