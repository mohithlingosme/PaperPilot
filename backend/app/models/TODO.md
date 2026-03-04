# Database Implementation TODO

## 1. Database Domains List (Docs)
- [x] Create docs/database/DB_LIST.md with logical schema domains and what each stores

## 2. Postgres Schema (Normalized, Multi-tenant)
- [x] Redesign all models with UUID primary keys, multi-tenancy via workspace_id
- [x] Implement required entities: users, sessions, api_keys, workspaces, roles, workspace_members, projects, sources, source_versions, source_files, source_pages, source_spans, pipeline_jobs, job_attempts, notes, note_versions, drafts, draft_versions, citations, exports, export_files, audit_events, usage_events
- [x] Add proper FK constraints, created_at/updated_at/deleted_at where useful
- [x] Implement indexes: FKs, (workspace_id, created_at), (project_id, created_at), pipeline queue, citations lookups

## 3. Migrations
- [x] Set up Alembic for migrations
- [x] Create infra/db/migrations/0001_init.sql (schemas + tables + constraints)
- [x] Create infra/db/migrations/0002_indexes.sql (all indexes)
- [x] Create infra/db/migrations/0003_seed.sql (roles + minimal defaults)
- [x] Add scripts: db:migrate, db:reset, db:status
- [x] Update .env.example with DATABASE_URL

## 4. DB Utility Layer (Code)
- [x] Add connection pooling/engine creation
- [x] Transaction helper
- [x] Query helper (typed)
- [x] Pagination helper (cursor-based)
- [x] Soft delete helper
- [x] Implement repositories: Workspace, Project, Source, PipelineJob, Draft, Citation
- [x] Add check_db_ready() for /ready

## 5. Local Docker (Postgres)
- [x] Add infra/docker-compose.db.yml with Postgres service, volume, healthcheck
- [x] Optional pgAdmin
- [x] Add scripts/db-reset.sh, scripts/db-migrate.sh

## 6. Tests (Minimal Integration)
- [x] Add basic integration tests: start DB, run migrations, insert/read via repos, assert constraints

## 7. Documentation
- [x] Create docs/database/ERD.md (ASCII ERD)
- [x] Create docs/database/DB_UTILS.md (how to migrate/reset/seed, repo usage)

# TODO.md — Core Data Model & Database (PaperPilot)

## Goals
- Define the **core relational data model** for PaperPilot (workspaces → projects → sources → processing → notes/drafts → citations → exports).
- Implement **PostgreSQL schema + migrations**.
- Add a **DB utility layer** (connection, migrations, transactions, repositories, seeds, test DB reset).

---

## P0 — Decisions & Foundations

- [ ] [P0] Decide DB strategy:
  - [ ] Use **PostgreSQL** as primary DB
  - [ ] Use **one database** with **multiple schemas/namespaces** (recommended) OR multiple DBs (justify if needed)
  - [ ] Decide PK type: `uuid` everywhere (preferred) vs `bigserial`
- [ ] [P0] Define baseline conventions:
  - [ ] Standard columns: `id`, `created_at`, `updated_at`, `deleted_at` (soft delete where relevant)
  - [ ] `workspace_id` required for multi-tenancy on all workspace-scoped tables
  - [ ] Enforce UTC timestamps at DB layer
- [ ] [P0] Create `/docs/database/` folder structure:
  - [ ] `/docs/database/DB_LIST.md`
  - [ ] `/docs/database/ERD.md`
  - [ ] `/docs/database/SCHEMA_NOTES.md`
  - [ ] `/docs/database/DB_UTILS.md`

---

## P0 — 1A) List of Required Databases / Schema Domains

- [ ] [P0] Write `docs/database/DB_LIST.md` with logical domains (schemas):
  - [ ] `auth_identity` (users, sessions, api keys)
  - [ ] `workspaces_projects` (workspaces, members, roles, projects)
  - [ ] `sources_library` (sources, versions, files/pointers, pages/spans)
  - [ ] `processing_pipeline` (jobs, attempts, status, retries, DLQ)
  - [ ] `notes_drafts` (notes, drafts, versions)
  - [ ] `citations_claims` (citations, claim mappings, source spans)
  - [ ] `exports` (export jobs, export files, templates)
  - [ ] `billing_usage` (usage events, tokens, OCR pages) — optional now
  - [ ] `audit_events` (immutable event log)
- [ ] [P0] Map each domain → expected queries + indexes (short section per domain)

---

## P0 — 1B) Schema Design (Relational Model)

### Multi-tenancy & Authorization
- [ ] [P0] Define roles/permissions approach:
  - [ ] `roles` table (predefined: owner/admin/editor/viewer)
  - [ ] `workspace_members` with role assignment
  - [ ] Index membership lookup by `(workspace_id, user_id)`

### Auth / Identity
- [ ] [P0] Tables:
  - [ ] `users` (email, name, status)
  - [ ] `sessions` (user_id, refresh token hash, expires_at)
  - [ ] `api_keys` (user_id/workspace_id, key_hash, last_used_at)
- [ ] [P0] Constraints:
  - [ ] unique email
  - [ ] token/key hashes never stored raw (hash only)

### Workspaces / Projects
- [ ] [P0] Tables:
  - [ ] `workspaces`
  - [ ] `workspace_members`
  - [ ] `projects`
- [ ] [P0] Constraints + indexes:
  - [ ] unique workspace slug (if used)
  - [ ] `(workspace_id, created_at)` index for list pages

### Sources Library
- [ ] [P0] Tables:
  - [ ] `sources` (workspace_id, project_id, type: pdf/url/text, title, metadata json)
  - [ ] `source_versions` (source_id, version_no, checksum, created_by)
  - [ ] `source_files` (source_version_id, storage_provider, bucket, key/path, size, mime)
  - [ ] `source_pages` (source_version_id, page_no, text, ocr_status) — optional but recommended
  - [ ] `source_spans` (page_id, start_offset, end_offset, snippet) for citations
- [ ] [P0] Indexes:
  - [ ] `(workspace_id, project_id, created_at)`
  - [ ] `(source_id, version_no)` unique
  - [ ] spans lookup by `(page_id, start_offset)`

### Processing Pipeline
- [ ] [P0] Tables:
  - [ ] `pipeline_jobs` (workspace_id, project_id, source_id, type, status, priority)
  - [ ] `job_attempts` (job_id, attempt_no, started_at, finished_at, error)
  - [ ] `job_artifacts` (job_id, kind, pointer/json) — optional
- [ ] [P0] Job types (enum or table):
  - [ ] ingest/parse
  - [ ] OCR
  - [ ] embeddings (optional)
  - [ ] summarization
  - [ ] draft_generation
  - [ ] export_generation
- [ ] [P0] Indexes:
  - [ ] job queue fetch index on `(status, priority, created_at)`
  - [ ] `(source_id, type, status)`

### Notes / Drafts + Versioning
- [ ] [P0] Tables:
  - [ ] `notes` + `note_versions`
  - [ ] `drafts` + `draft_versions`
- [ ] [P0] Versioning rules:
  - [ ] `*_versions` immutable rows
  - [ ] latest pointer on parent table (optional) OR query by max version
- [ ] [P0] Indexes:
  - [ ] `(draft_id, version_no)` unique
  - [ ] `(workspace_id, project_id, updated_at)` for listing

### Citations / Claims
- [ ] [P0] Tables:
  - [ ] `citations` (draft_version_id, source_span_id, confidence, note, quote)
  - [ ] `claims` (draft_version_id, claim_text, normalized_hash) — optional
  - [ ] `claim_citations` (claim_id, citation_id) — optional
- [ ] [P0] Constraints:
  - [ ] prevent duplicate citation rows for same (draft_version_id, source_span_id)

### Exports
- [ ] [P0] Tables:
  - [ ] `exports` (draft_version_id, format, status)
  - [ ] `export_files` (export_id, storage pointer, size, checksum)
  - [ ] `export_templates` (workspace_id, name, config json) — optional
- [ ] [P0] Indexes:
  - [ ] `(draft_version_id, created_at)`

### Audit & Usage
- [ ] [P0] Tables:
  - [ ] `audit_events` (workspace_id, actor_user_id, action, entity_type, entity_id, payload json)
  - [ ] `usage_events` (workspace_id, type: llm_tokens/ocr_pages/storage_bytes, amount, meta json)
- [ ] [P0] Indexes:
  - [ ] audit by `(workspace_id, created_at)`
  - [ ] usage by `(workspace_id, type, created_at)`

---

## P0 — Migrations & Schema Artifacts

- [ ] [P0] Add migration framework (choose based on stack):
  - [ ] Node: Prisma/Drizzle/Knex or SQL migrations runner
  - [ ] Python: Alembic or raw SQL runner
- [ ] [P0] Create SQL migration files:
  - [ ] `infra/db/migrations/0001_init.sql` (schemas + tables + constraints)
  - [ ] `infra/db/migrations/0002_indexes.sql` (all indexes)
  - [ ] `infra/db/migrations/0003_seed.sql` (roles, default settings)
- [ ] [P0] Add DB initialization scripts (docker entrypoint compatible)
- [ ] [P0] Produce `docs/database/ERD.md`:
  - [ ] ASCII ERD diagram
  - [ ] short “table purpose” notes

---

## P0 — 1C) Database Utility Layer

### Connection & Config
- [ ] [P0] Implement DB config (env):
  - [ ] `DATABASE_URL`
  - [ ] `DB_POOL_SIZE`
  - [ ] `DB_POOL_TIMEOUT`
- [ ] [P0] Connection pooling
- [ ] [P0] DB health check helper used by `/ready`

### Migration Runner
- [ ] [P0] Add CLI scripts:
  - [ ] `db:migrate`
  - [ ] `db:rollback` (even if limited, document behavior)
  - [ ] `db:status` (optional)
- [ ] [P0] Add `make` targets or npm/pnpm scripts

### Transactions & Query Helpers
- [ ] [P0] Add transaction helper (`withTransaction`)
- [ ] [P0] Add pagination utilities:
  - [ ] cursor-based (preferred) + stable ordering
- [ ] [P0] Add soft delete helpers:
  - [ ] filters to exclude `deleted_at IS NOT NULL` by default

### Repositories (Minimum)
- [ ] [P0] Workspace repository:
  - [ ] create workspace, add member, list members
- [ ] [P0] Project repository:
  - [ ] create project, list projects
- [ ] [P0] Source repository:
  - [ ] create source, add version, attach file pointer, list sources
- [ ] [P0] Pipeline jobs repository:
  - [ ] enqueue job, claim job, mark success/fail, record attempts
- [ ] [P0] Draft repository:
  - [ ] create draft, create draft_version, list versions
- [ ] [P0] Citation repository:
  - [ ] add citation(s), list citations for draft_version

---

## P1 — Local Dev Database Stack (Docker)

- [ ] [P1] Add `infra/docker-compose.db.yml` (or extend existing):
  - [ ] Postgres service
  - [ ] Admin tool (pgAdmin optional)
  - [ ] Volume for persistence
- [ ] [P1] Add `scripts/db-reset` (drop + recreate + migrate + seed)
- [ ] [P1] Add `.env.example` DB section with safe defaults

---

## P1 — Tests & Verification

- [ ] [P1] Add DB integration test setup:
  - [ ] Test container / docker service for CI
  - [ ] Test migration application from scratch
- [ ] [P1] Add repository tests:
  - [ ] create workspace/project/source/draft and assert retrieval
- [ ] [P1] Add readiness test:
  - [ ] start API → `/ready` returns dependency status JSON

---

## P2 — Performance & Hardening

- [ ] [P2] Add query plans / index review for top endpoints
- [ ] [P2] Add row-level security strategy (optional future):
  - [ ] enforce workspace scoping in queries
- [ ] [P2] Add retention policies:
  - [ ] audit log retention (configurable)
  - [ ] job attempts retention
- [ ] [P2] Add partitioning plan (if needed later):
  - [ ] `usage_events` by month
  - [ ] `audit_events` by month

---

## Definition of Done
- [ ] DB list doc exists and matches product scope
- [ ] Migrations create all schemas/tables/constraints/indexes cleanly
- [ ] DB utility layer can:
  - [ ] connect with pooling
  - [ ] migrate/seed/reset
  - [ ] run transactions safely
- [ ] Repositories support core flows:
  - [ ] create workspace → project → source → job → draft_version → citations → export
