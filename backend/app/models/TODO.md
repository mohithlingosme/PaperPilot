# TODO.md — PaperPilot (Research‑to‑Publish OS) Complete Development Checklist

> **Purpose:** a single, end‑to‑end task list to build PaperPilot from zero → production.  
> **How to use:** assign boxes to sprints/owners; keep links to PRs/issues next to completed items.

Legend:
- **[P0]** MVP must-have
- **[P1]** v1 (strongly recommended)
- **[P2]** v2 / advanced
- Add an owner + link when you start: `(@owner • #issue • PR link)`

---

## 0) Repo, Standards, and Project Governance

### 0.1 Repository foundation
- [ ] [P0] Initialize repo (mono‑repo recommended): `apps/web`, `apps/api`, `apps/worker`, `packages/shared`, `infra/`, `docs/`, `tests/`, `e2e/`, `load/`, `security/`
- [ ] [P0] Add root `README.md` (what it is, how to run, how to contribute)
- [ ] [P0] Add `Development_plan.md` (link from README)
- [ ] [P0] Add `.editorconfig`, `.gitattributes`
- [ ] [P0] Add lint/format configs (Prettier + ESLint for web; ruff/black for Python OR equivalent for Node)
- [ ] [P0] Add commit conventions (Conventional Commits) + PR template
- [ ] [P0] Add `CODEOWNERS`, `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE`
- [ ] [P0] Add basic issue labels (P0/P1/P2, backend/frontend/infra/bug/security)

### 0.2 Dev workflow
- [ ] [P0] Define branch strategy (feature branches → PR → main)
- [ ] [P0] Define versioning + changelog strategy (tags, `CHANGELOG.md`)
- [ ] [P0] Define DoD (Definition of Done): tests + docs + RBAC checks + logs
- [ ] [P1] Add architecture docs folder: `docs/architecture/*`
- [ ] [P1] Add ADRs (Architecture Decision Records) template

---

## 1) Local Development Environment (Everything runs on a laptop)

### 1.1 Docker + environment
- [ ] [P0] Create `docker-compose.yml` for dev:
  - [ ] Postgres (+ pgvector extension if used)
  - [ ] Redis (queue/cache)
  - [ ] MinIO (S3 compatible) OR local filesystem volume for uploads
  - [ ] API service
  - [ ] Worker service
  - [ ] Web service
- [ ] [P0] Create `.env.example` with all required variables
- [ ] [P0] Create `.env` (local) and `.env.test` (tests)
- [ ] [P0] Add Makefile (or npm scripts) for:
  - [ ] `make dev` (start all)
  - [ ] `make down`
  - [ ] `make logs`
  - [ ] `make db-migrate`
  - [ ] `make test`
- [ ] [P1] Add one-command onboarding: `./scripts/bootstrap.sh`

### 1.2 Observability in dev
- [ ] [P0] Add structured logging to API + worker (request id / job id)
- [ ] [P1] Add health endpoints: `/health`, `/ready`
- [ ] [P1] Add basic metrics endpoint (Prometheus style) OR logging counters

---

## 2) Core Data Model & Database

### 2.1 Database schema (MVP)
- [ ] [P0] Choose DB + ORM (Postgres recommended)
- [ ] [P0] Create migrations for:
  - [ ] users
  - [ ] refresh_sessions / tokens (if using refresh tokens)
  - [ ] projects
  - [ ] project_members (RBAC)
  - [ ] sources (pdf/url)
  - [ ] source_files (storage path, hash, size, mime)
  - [ ] source_pages (optional) OR store page numbers on chunks
  - [ ] source_chunks (text, token_count, page_no, heading_path, embedding vector)
  - [ ] summaries
  - [ ] outlines (versioned, locked flag)
  - [ ] drafts (versioned)
  - [ ] citations (draft ↔ chunk mapping, style, page/locator)
  - [ ] exports (docx/pdf) + status + file pointer
  - [ ] jobs (background job status)
  - [ ] audit_logs
- [ ] [P1] Add org/workspace tables (optional if multi-tenant)
- [ ] [P1] Add usage tracking tables (credits/cost logs)
- [ ] [P2] Add collaboration comments + mentions tables

### 2.2 DB utilities
- [ ] [P0] Add DB connection config (single `DATABASE_URL`)
- [ ] [P0] Add seed scripts for dev (admin user, sample project, sample sources)
- [ ] [P0] Add safe DB reset script for dev/test
- [ ] [P1] Add DB indexes for performance (project_id, source_id, created_at, embeddings index)
- [ ] [P1] Add row-level constraints + FK cascades designed carefully

---

## 3) Authentication, Authorization, and Security Baselines

### 3.1 Auth (MVP)
- [ ] [P0] Implement signup/login/logout
- [ ] [P0] Password hashing (bcrypt/argon2)
- [ ] [P0] JWT access token + refresh token/session rotation
- [ ] [P0] Session expiry and refresh endpoint
- [ ] [P0] Password reset flow (request + confirm)
- [ ] [P0] Rate limit auth endpoints (login/reset)

### 3.2 RBAC (MVP)
- [ ] [P0] Implement project-level roles: viewer/editor/admin
- [ ] [P0] Middleware/dependencies to enforce permissions
- [ ] [P0] Ensure all project scoped endpoints verify membership
- [ ] [P1] Audit logs for role changes + critical actions

### 3.3 MFA (v1)
- [ ] [P1] Add TOTP MFA enable/disable
- [ ] [P1] Add recovery codes
- [ ] [P1] Add MFA required on login when enabled

### 3.4 Security baseline
- [ ] [P0] Input validation everywhere (request schemas)
- [ ] [P0] File upload validation (mime, size, extension, virus stub hook)
- [ ] [P0] URL import sanitization (SSRF protection: allowlist/deny private IP ranges)
- [ ] [P0] CORS config
- [ ] [P0] CSRF strategy (if cookies used)
- [ ] [P1] Secrets management plan (never commit secrets)
- [ ] [P1] Data deletion flow (delete project and purge files)
- [ ] [P2] Encryption at rest plan (DB + object storage)

---

## 4) Backend API (FastAPI/Nest/Express) — Endpoints & Contracts

### 4.1 API foundation
- [ ] [P0] Create API service skeleton
- [ ] [P0] Add request/response schemas + consistent error format:
  - [ ] `error.code`, `error.message`, `error.details`, `request_id`
- [ ] [P0] Add OpenAPI generation (or swagger) + store spec artifact in CI

### 4.2 Projects
- [ ] [P0] CRUD endpoints: list/create/get/update/delete
- [ ] [P0] Member management:
  - [ ] invite flow (email token OR share link)
  - [ ] accept/revoke
  - [ ] role changes

### 4.3 Sources & Library
- [ ] [P0] Upload PDF endpoint (multipart)
- [ ] [P0] Create URL source endpoint
- [ ] [P0] List sources in project (filter/sort/pagination)
- [ ] [P0] Get source detail (metadata + status)
- [ ] [P0] Delete source (and cascade chunks/embeddings/files)
- [ ] [P1] Source versioning (re-upload / update)

### 4.4 Search
- [ ] [P0] Implement semantic search endpoint:
  - [ ] query → embeddings → vector search on chunks
  - [ ] filters: source_id, date, tags, type
  - [ ] include snippet + page locator + score
- [ ] [P1] Implement keyword fallback search (tsvector) and blended ranking
- [ ] [P1] Add “recent searches” + analytics events

### 4.5 Summaries
- [ ] [P0] Summarize a source (job-based)
- [ ] [P0] Read cached summary
- [ ] [P1] Multi-length summaries (short/medium/long)

### 4.6 Outline
- [ ] [P0] Generate outline from topic + sources
- [ ] [P0] Save outline (versioned)
- [ ] [P0] Lock/unlock outline version
- [ ] [P1] Outline templates (legal, business, academic)

### 4.7 Draft generation (RAG)
- [ ] [P0] Generate draft section-by-section from outline version
- [ ] [P0] Require citations mapping output → chunks
- [ ] [P0] Save draft version
- [ ] [P1] Style controls (tone, length, audience)
- [ ] [P1] Idempotency keys for retries
- [ ] [P2] Multi-agent generation (planner/writer/citation verifier)

### 4.8 Citations & Reference lists
- [ ] [P0] Store citation markers (sourceId, chunkId, page)
- [ ] [P0] Generate reference list from citations
- [ ] [P1] Style renderers:
  - [ ] APA
  - [ ] MLA
  - [ ] Chicago
  - [ ] Bluebook (basic)
- [ ] [P1] Deduplicate citations + merge references
- [ ] [P1] Edge cases (page ranges, multiple authors)

### 4.9 Exports
- [ ] [P0] Export DOCX job
- [ ] [P0] Export PDF job
- [ ] [P0] Export must include reference list + working citation formatting
- [ ] [P1] Links back to sources (where possible)
- [ ] [P1] Export watermarking / branding options

### 4.10 Jobs / status
- [ ] [P0] Job status model: queued/running/success/failed + progress
- [ ] [P0] `GET /jobs/{id}` endpoint
- [ ] [P0] Standard retry policy + safe idempotency

### 4.11 Audit, notifications, analytics
- [ ] [P1] Audit log endpoint (admin)
- [ ] [P1] Notification events (export complete, invite)
- [ ] [P2] Webhooks / integrations

---

## 5) Worker System (Background Processing)

### 5.1 Queue & worker foundation
- [ ] [P0] Choose worker framework (Celery/RQ/BullMQ/etc)
- [ ] [P0] Configure Redis broker and retry policy
- [ ] [P0] Create job runner + job status updates in DB

### 5.2 Ingestion pipeline jobs
- [ ] [P0] PDF text extraction job
- [ ] [P0] Chunking job (preserve pages/headings)
- [ ] [P0] Embeddings job (store vectors in DB)
- [ ] [P1] OCR job (optional) for scanned PDFs
- [ ] [P1] URL fetch + HTML-to-text job with sanitization and timeout

### 5.3 Writing jobs
- [ ] [P0] Source summarization job
- [ ] [P0] Outline generation job
- [ ] [P0] Draft generation job (section loop, citations)
- [ ] [P1] Provider failover (AI outage fallback)
- [ ] [P2] Quality verification job (claim traceability graph)

### 5.4 Export jobs
- [ ] [P0] DOCX export job
- [ ] [P0] PDF export job
- [ ] [P1] Large document export optimization (streaming, memory control)

---

## 6) AI Layer (Provider Abstraction + Guardrails)

### 6.1 Provider abstraction
- [ ] [P0] Create AI client interface:
  - [ ] `embed(texts[])`
  - [ ] `generate(prompt, context)`
  - [ ] timeout/retry/backoff
- [ ] [P0] Implement at least 1 provider (OpenAI or chosen)
- [ ] [P1] Add second provider as fallback

### 6.2 Prompting & formatting
- [ ] [P0] Define standard system prompts:
  - [ ] summarizer
  - [ ] outline planner
  - [ ] section writer (RAG)
  - [ ] citation formatter
- [ ] [P0] Enforce output schema including citation markers
- [ ] [P0] Store prompts + versions for reproducibility

### 6.3 Anti-hallucination rules
- [ ] [P0] Strict mode: reject paragraphs without citations
- [ ] [P1] Claim-to-snippet verification (basic)
- [ ] [P1] Citation misattribution checks (detect wrong mapping)
- [ ] [P2] Source graph scoring (claim traceability)

### 6.4 Cost tracking (if relevant)
- [ ] [P1] Track tokens and cost per job
- [ ] [P1] Budget limits per project/user
- [ ] [P1] Regression guard: cost per 1000 calls threshold

---

## 7) Storage (Files, Exports, and Access Control)

### 7.1 File storage
- [ ] [P0] Decide dev storage (local) + prod storage (S3 compatible)
- [ ] [P0] Implement upload storage adapter (put/get/delete)
- [ ] [P0] Store file metadata (hash, size, mime, path)
- [ ] [P0] Secure file access (signed URLs or proxy with RBAC)
- [ ] [P1] Implement dedup by hash per project

### 7.2 Export storage
- [ ] [P0] Save exports (docx/pdf) and allow download
- [ ] [P0] Ensure only project members can download
- [ ] [P1] Add cleanup policy for old exports

---

## 8) Frontend (Web UI) — Pages, Components, UX

### 8.1 App shell
- [ ] [P0] Initialize web app (Next.js/React) with routing
- [ ] [P0] Auth screens: signup/login/forgot/reset
- [ ] [P0] App layout: sidebar/topbar, project switcher

### 8.2 Dashboard & projects
- [ ] [P0] Projects list page
- [ ] [P0] Create/edit project modals
- [ ] [P0] Project settings page (members + roles)

### 8.3 Source library
- [ ] [P0] Upload PDF UI with progress
- [ ] [P0] Add URL source UI
- [ ] [P0] Library table (status, type, date, actions)
- [ ] [P0] Source detail view (metadata + extracted text preview + summary)

### 8.4 Search UI
- [ ] [P0] Search bar + results list
- [ ] [P0] Show snippet, source title, page, open source
- [ ] [P1] Filters (source/type/date)
- [ ] [P1] “Save snippet to notes” feature

### 8.5 Outline builder
- [ ] [P0] Outline generation UI (topic + options)
- [ ] [P0] Outline editor (reorder, add/remove sections)
- [ ] [P0] Version display + lock/unlock
- [ ] [P1] Outline templates

### 8.6 Draft editor (core)
- [ ] [P0] Rich text editor integration (TipTap/Lexical/etc)
- [ ] [P0] Generate draft button + job status
- [ ] [P0] Render citations as chips/footnotes
- [ ] [P0] Reference list panel
- [ ] [P1] Undo/redo, version history
- [ ] [P1] Comments + collaboration basics

### 8.7 Export UI
- [ ] [P0] Export page: choose style + format (docx/pdf)
- [ ] [P0] Download links + history list
- [ ] [P1] Export preview + warnings (missing citations)

### 8.8 Quality UX details
- [ ] [P0] Empty states everywhere (no projects, no sources)
- [ ] [P0] Error toasts and retry actions
- [ ] [P1] Keyboard shortcuts for editor
- [ ] [P1] Accessibility pass (labels, contrast)

---

## 9) Testing (Complete Test Suite)

> Implement tests aligned to the master test script list you created.

### 9.1 Unit tests
- [ ] [P0] Unit tests: auth, RBAC, sources ingestion, chunking, embeddings enqueue, citations formatters, export formatters
- [ ] [P0] Deterministic fixtures (fixed clock/random seed)
- [ ] [P0] No-network rule for unit tests

### 9.2 Integration tests
- [ ] [P0] Integration: ingestion → embed → search
- [ ] [P0] Integration: outline → draft with citations
- [ ] [P0] Integration: export pipeline large doc
- [ ] [P1] Provider failover tests

### 9.3 API contract tests
- [ ] [P0] OpenAPI schema snapshot and breaking-change detection
- [ ] [P0] Pagination/filter/sort consistency tests
- [ ] [P0] Standard error format tests
- [ ] [P0] Permissions tests per endpoint

### 9.4 E2E UI tests (Playwright)
- [ ] [P0] Signup/login + basic auth
- [ ] [P0] Create project + upload PDF
- [ ] [P0] Search + view source
- [ ] [P0] Outline + draft + citations
- [ ] [P0] Export docx/pdf
- [ ] [P1] Collaboration flow
- [ ] [P1] Credits exhausted flow (if billing)

### 9.5 Non-functional tests
- [ ] [P1] Load tests (k6/locust): concurrent uploads, draft generations, search latency p95, export latency
- [ ] [P1] Chaos tests: AI timeout retry, vector index recovery, worker crash resume

### 9.6 AI eval harness
- [ ] [P1] Create offline eval dataset fixtures
- [ ] [P1] Summarization faithfulness scoring
- [ ] [P1] Citation coverage rate
- [ ] [P1] Hallucination rate in strict mode
- [ ] [P1] Bluebook format accuracy suite
- [ ] [P1] Regression suite for fixed prompt bugs

---

## 10) CI/CD (GitHub Actions)

### 10.1 Pipelines
- [ ] [P0] Lint workflow (web + api)
- [ ] [P0] Unit tests workflow
- [ ] [P0] Integration tests workflow (with Postgres + Redis services)
- [ ] [P0] E2E workflow (Playwright with web+api+worker)
- [ ] [P1] Security scans (deps + SAST)
- [ ] [P1] Upload artifacts: coverage, junit xml, playwright report

### 10.2 Deployment
- [ ] [P1] Create staging deployment workflow
- [ ] [P1] Create production deployment workflow (tag-based)
- [ ] [P1] Add DB migration step to deploy pipeline
- [ ] [P1] Rollback strategy (previous image + migrations safe plan)

---

## 11) Security Tooling & Compliance

### 11.1 Automated security checks
- [ ] [P0] Dependency scanning (npm/pip) in CI
- [ ] [P1] SAST config (semgrep/bandit/eslint security)
- [ ] [P1] DAST smoke (OWASP ZAP) for auth bypass checks
- [ ] [P1] RBAC privilege escalation tests

### 11.2 Data governance
- [ ] [P1] Project delete = remove DB rows + delete stored files
- [ ] [P1] Export/delete user data (basic)
- [ ] [P2] Data residency / region configuration docs (India-first)

---

## 12) Observability (Prod Readiness)

- [ ] [P1] Centralized logs (JSON)
- [ ] [P1] Request tracing (request_id across API + worker)
- [ ] [P1] Metrics dashboard (latency, queue depth, errors)
- [ ] [P1] Alert rules (worker down, queue backlog, DB errors)

---

## 13) Billing / Usage (Only if you need it)

- [ ] [P1] Credits model definition (what costs what)
- [ ] [P1] Track usage per job (tokens, embeddings, exports)
- [ ] [P1] Subscription state machine
- [ ] [P1] Webhook verification for payment provider
- [ ] [P1] UI: usage dashboard + limits
- [ ] [P2] Team billing (org-level)

---

## 14) Content, Templates, and Onboarding

- [ ] [P0] Sample project + sample sources for demo
- [ ] [P0] Onboarding checklist in UI (“upload first source”)
- [ ] [P1] Template library:
  - [ ] Legal brief
  - [ ] Business plan
  - [ ] Academic report
  - [ ] Blog/article

---

## 15) Release Checklist (Before launch)

### 15.1 Functional
- [ ] [P0] Upload works reliably (PDF + URL)
- [ ] [P0] Search returns relevant snippets with page locators
- [ ] [P0] Draft generation produces citations correctly
- [ ] [P0] Export docx/pdf passes sanity check (headings + references)
- [ ] [P0] RBAC prevents data leaks

### 15.2 Quality
- [ ] [P0] Full test suite green in CI
- [ ] [P1] Load test baseline results recorded
- [ ] [P1] Security scans clean or documented exceptions

### 15.3 Operations
- [ ] [P1] Backups configured (DB + storage)
- [ ] [P1] Monitoring + alerts configured
- [ ] [P1] Incident runbook in `docs/ops/runbook.md`

---

## 16) Optional Advanced Roadmap (v2+)

- [ ] [P2] Claim traceability graph UI (claim → snippet → source)
- [ ] [P2] Human approval loop for AI output
- [ ] [P2] Multi-agent orchestration (planner/writer/verifier)
- [ ] [P2] Advanced plagiarism workflows + similarity highlights
- [ ] [P2] Team workflows: approvals, tasks, assignments
- [ ] [P2] Public sharing with redactions and permission controls

---
