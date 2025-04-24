# ROADMAP: Minutely Detailed Execution Plan

**Project Start Date:** Day 0 (2025-04-24)

---

## Phase 0: Pre‑Planning (1 Week, Days 1–7)

**Day 1 (2025-04-24)** ✅ Completed
- Kickoff meeting: define objectives, success metrics, roles
- Initialize GitHub repo, default branch `main`, branch protection rules
- Secure compute resources (cloud VM, storage buckets)
- Obtain API keys (Tesseract, LLM provider, currency service)

**Day 2 (2025-04-25)** ✅ Completed
- Install Python 3.10+, Docker, Docker Compose
- Create virtual environment, install pip-tools
- Draft coding standards: Black, Flake8, isort configs
- Document project scope in `planning.md`

**Day 3 (2025-04-26)** ✅ Completed
- Scaffold GitHub Actions pipeline: lint, format, test
- Write minimal smoke test to verify CI trigger
- Configure environment separation: `.env.dev`, `.env.test`, `.env.prod` templates

**Day 4 (2025-04-27)** ✅ Completed
- Research and finalize tech stack: Flask, SQLAlchemy vs. ORM alternatives
- Draft initial system architecture diagram (OCR → RAG → LLM)
- Identify key database tables and relationships

**Day 5 (2025-04-28)** ✅ Completed
- Design DB schema in detail: receipts, fields, index table for FAISS
- Draft REST API endpoints spec: `/upload`, `/receipts`, `/categories`, `/analytics`

**Day 6 (2025-04-29)** ✅ Completed
- Define agent workflows: OCR pipeline deep dive (image preprocessing, language selection)
- Outline RAG flow: embedding extraction, index update, retrieval logic
- Sketch currency conversion agent logic and error handling

**Day 7 (2025-04-30)** ✅ Completed
- Review Phase 0 deliverables with stakeholders
- Revise planning docs per feedback
- Freeze Phase 0 and transition to Phase 1

---

## Phase 1: Planning, Design & Data Collection (2 Weeks, Days 8–21)

### Week 1 (Days 8–14)

**Day 8 (2025-05-01)**
- Collect 100 sample receipt images (various formats)
- Label merchant, date, total manually in CSV

**Day 9 (2025-05-02)**
- Finalize DB schema: integrate tags, notes, audit fields
- Write SQLAlchemy models and Alembic migration draft

**Day 10 (2025-05-03)**
- Draft OpenAPI spec with example requests/responses
- Peer review API spec, refine field definitions

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
- **Day 26 (2025-05-19):** [ ] Configure CI to run lint, format, migrations, tests
- **Day 27 (2025-05-20):** [ ] Peer review Sprint 1 code, address comments
- **Day 28 (2025-05-21):** [ ] Merge Sprint 1 branch, tag `v0.1-mvp`

### Sprint 2 (Week 2, Days 29–35)

- **Day 29 (2025-05-22):** ✅ Integrate Tesseract OCR, parse raw text + unit tests
- **Day 30 (2025-05-23):** ✅ Implement regex-based field extraction (merchant, date, total) + tests
- **Day 31 (2025-05-24):** ✅ Add currency symbol detection, update models + tests
- **Day 32 (2025-05-25):** ✅ Build minimal UI or Postman mocks to validate endpoints
- **Day 33 (2025-05-26):** [ ] End-to-end integration tests on sample dataset
- **Day 34 (2025-05-27):** [ ] Performance benchmark: 50 receipts/minute
- **Day 35 (2025-05-28):** [ ] Merge Sprint 2 branch, tag `v0.2-mvp`

### Sprint 3 (Week 3, Days 36–42)

- **Day 36 (2025-05-29):** ✅ `/receipts` list endpoint + pagination + tests
- **Day 37 (2025-05-30):** ✅ `/receipts/{id}` detail endpoint + tests
- **Day 38 (2025-05-31):** ✅ Add tags, notes fields, expand schema + tests
- **Day 39 (2025-06-01):** [ ] Create Dockerfile & docker-compose for MVP + local dev smoke tests
- **Day 40 (2025-06-02):** [ ] Update CI to build and push Docker image for staging
- **Day 41 (2025-06-03):** [ ] Integration smoke tests in Docker environment
- **Day 42 (2025-06-04):** [ ] Merge Sprint 3 branch, tag `v0.3-mvp`

### Sprint 4 (Week 4, Days 43–49)

- **Day 43 (2025-06-05):** [ ] Polish OpenAPI docs (Swagger UI) + tests
- **Day 44 (2025-06-06):** [ ] Prepare Postman collection and sample requests
- **Day 45 (2025-06-07):** [ ] Draft user guide and quickstart README
- **Day 46 (2025-06-08):** [ ] Final performance tuning: memory, CPU profiling
- **Day 47 (2025-06-09):** [ ] Resolve edge cases and error flows + tests
- **Day 48 (2025-06-10):** [ ] Final code review and merge Sprint 4
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
