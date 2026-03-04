# Database Domains List

This document outlines the logical schema domains for PaperPilot's database, organized by functional area.

## Required Domains

### auth_identity
Stores user authentication and authorization data.
- **Tables**: users, sessions, api_keys
- **Typical Queries**: User lookup by email, session validation, API key authentication
- **Index Expectations**: Unique on email, index on session expires_at, index on api_key last_used_at

### workspaces_projects
Manages multi-tenant workspaces, projects, and membership.
- **Tables**: workspaces, roles, workspace_members, projects
- **Typical Queries**: List user's workspaces, get workspace members, list projects in workspace
- **Index Expectations**: Unique on workspace slug, unique on (workspace_id, user_id) for members, index on (workspace_id, created_at)

### sources_library
Handles document sources, versions, and file storage.
- **Tables**: sources, source_versions, source_files, source_pages, source_spans
- **Typical Queries**: List sources in project, get latest version, find spans for citation
- **Index Expectations**: Index on (project_id, created_at), unique on (source_id, version_no), index on (source_version_id, page_no)

### processing_pipeline
Manages background job processing and retries.
- **Tables**: pipeline_jobs, job_attempts, job_artifacts (optional)
- **Typical Queries**: Claim next job, list failed attempts, get job status
- **Index Expectations**: Index on (status, priority, created_at) for queue, index on (job_id, attempt_no)

### notes_drafts
Stores notes and draft documents with versioning.
- **Tables**: notes, note_versions, drafts, draft_versions
- **Typical Queries**: Get latest draft version, list versions by created_at
- **Index Expectations**: Index on (draft_id, created_at), index on (note_id, created_at)

### citations_claims
Links citations to source spans in drafts.
- **Tables**: citations
- **Typical Queries**: Get citations for draft_version, find citations by source_span
- **Index Expectations**: Index on draft_version_id, index on source_span_id, unique on (draft_version_id, source_span_id)

### exports
Manages document export jobs and files.
- **Tables**: exports, export_files
- **Typical Queries**: List exports for draft, get export status
- **Index Expectations**: Index on (draft_version_id, created_at)

### audit_events
Immutable log of all system actions.
- **Tables**: audit_events
- **Typical Queries**: Audit trail for entity, recent actions by user
- **Index Expectations**: Index on (workspace_id, created_at), index on (actor_user_id, created_at), index on (entity_type, entity_id)

### billing_usage (optional)
Tracks usage for billing purposes.
- **Tables**: usage_events
- **Typical Queries**: Usage summary by workspace, recent events
- **Index Expectations**: Index on (workspace_id, created_at), index on (type, created_at)
