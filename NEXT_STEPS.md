# Next Steps: SOTA Roadmap Implementation (as of 2025-04-24)

This file tracks the immediate, state-of-the-art (SOTA) priorities for the Expense Tracker project. Update this checklist as you progress!

## 🔥 Immediate Priorities

1. **Polish OpenAPI/Swagger Docstrings**
   - Add complete, example-rich docstrings for all endpoints
   - Use Marshmallow schemas for `$ref` and type safety
   - Provide real example requests/responses
   - Ensure error responses are documented for all edge cases
   - Validate schema with CI

2. **Generate Postman Collection**
   - Export from OpenAPI spec for full endpoint coverage
   - Include example requests and authentication flows (if any)

3. **Update README/User Guide**
   - Add quickstart, API usage, and Swagger UI instructions
   - Include “How to contribute” and troubleshooting sections

4. **Add Performance Profiling Hooks**
   - Integrate Flask Profiler or similar lightweight tools
   - Document baseline metrics and performance targets

5. **Expand Edge Case & Error Path Tests**
   - Add/expand pytest unit and integration tests for invalid files, API misuse, and boundary conditions
   - Use pytest-cov and enforce coverage in CI

---

## SOTA Techniques Checklist
- [ ] API docs: Flasgger + Marshmallow, DRY, auto-validating
- [ ] Testing: pytest, pytest-cov, CI enforcement
- [ ] CI/CD: Dockerized tests, OpenAPI validation, auto-lint/format
- [ ] Dependency management: pip-tools, pinned requirements, Docker caching
- [ ] Security: .env for secrets, no hardcoded keys, Docker secrets for prod
- [ ] Dev experience: pre-commit hooks, black/isort/flake8, robust README

---

## 🛠️ SOTA Action Checklist (2025-04-24)

**Immediate Action Items:**

1. **Audit API docstrings**
   - Review all endpoints for Marshmallow-backed, example-rich docstrings
   - Ensure `$ref` usage and error responses are complete
   - Add OpenAPI schema validation to CI

2. **Review/Export OpenAPI spec**
   - Ensure OpenAPI spec is up to date
   - Generate and export Postman collection (include auth/edge flows)

3. **README audit**
   - Identify and fill missing sections: quickstart, API, Swagger UI, contributing, troubleshooting
   - Test onboarding with a fresh user

4. **Integrate Flask Profiler**
   - Add profiling hooks to dev Docker Compose
   - Document baseline metrics and targets

5. **Test coverage audit**
   - Identify and strengthen weak spots with pytest, pytest-cov
   - Enforce >90% coverage in CI

6. **CI/CD check**
   - Confirm OpenAPI validation, lint/format, and test coverage are enforced

7. **Dependency management**
   - Ensure pip-tools and Docker caching are in use

8. **Security/config**
   - Double-check .env usage, no secrets in code, Docker secrets for prod

9. **Dev experience**
   - Confirm pre-commit hooks (black, isort, flake8) are active

---

*Update this file as you check off each item or add new priorities. This is your living action plan for SOTA delivery!*
