-- Foreign key indexes (automatically created by PostgreSQL, but explicit for clarity)
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_workspace_id ON api_keys(workspace_id);
CREATE INDEX idx_workspace_members_workspace_id ON workspace_members(workspace_id);
CREATE INDEX idx_workspace_members_user_id ON workspace_members(user_id);
CREATE INDEX idx_workspace_members_role_id ON workspace_members(role_id);
CREATE INDEX idx_projects_workspace_id ON projects(workspace_id);
CREATE INDEX idx_sources_workspace_id ON sources(workspace_id);
CREATE INDEX idx_sources_project_id ON sources(project_id);
CREATE INDEX idx_source_versions_source_id ON source_versions(source_id);
CREATE INDEX idx_source_versions_created_by ON source_versions(created_by);
CREATE INDEX idx_source_files_source_version_id ON source_files(source_version_id);
CREATE INDEX idx_source_pages_source_version_id ON source_pages(source_version_id);
CREATE INDEX idx_source_spans_page_id ON source_spans(page_id);
CREATE INDEX idx_pipeline_jobs_workspace_id ON pipeline_jobs(workspace_id);
CREATE INDEX idx_pipeline_jobs_project_id ON pipeline_jobs(project_id);
CREATE INDEX idx_pipeline_jobs_source_id ON pipeline_jobs(source_id);
CREATE INDEX idx_job_attempts_job_id ON job_attempts(job_id);
CREATE INDEX idx_notes_workspace_id ON notes(workspace_id);
CREATE INDEX idx_notes_project_id ON notes(project_id);
CREATE INDEX idx_note_versions_note_id ON note_versions(note_id);
CREATE INDEX idx_drafts_workspace_id ON drafts(workspace_id);
CREATE INDEX idx_drafts_project_id ON drafts(project_id);
CREATE INDEX idx_draft_versions_draft_id ON draft_versions(draft_id);
CREATE INDEX idx_citations_draft_version_id ON citations(draft_version_id);
CREATE INDEX idx_citations_source_span_id ON citations(source_span_id);
CREATE INDEX idx_exports_draft_version_id ON exports(draft_version_id);
CREATE INDEX idx_export_files_export_id ON export_files(export_id);
CREATE INDEX idx_audit_events_workspace_id ON audit_events(workspace_id);
CREATE INDEX idx_audit_events_actor_user_id ON audit_events(actor_user_id);
CREATE INDEX idx_audit_events_entity_type_id ON audit_events(entity_type, entity_id);
CREATE INDEX idx_usage_events_workspace_id ON usage_events(workspace_id);

-- Frequent list filters: (workspace_id, created_at) on major tables
CREATE INDEX idx_workspaces_created_at ON workspaces(created_at);
CREATE INDEX idx_workspace_members_created_at ON workspace_members(workspace_id, created_at);
CREATE INDEX idx_projects_created_at ON projects(workspace_id, created_at);
CREATE INDEX idx_sources_created_at ON sources(workspace_id, created_at);
CREATE INDEX idx_sources_project_created_at ON sources(project_id, created_at);
CREATE INDEX idx_pipeline_jobs_created_at ON pipeline_jobs(workspace_id, created_at);
CREATE INDEX idx_notes_created_at ON notes(workspace_id, created_at);
CREATE INDEX idx_drafts_created_at ON drafts(workspace_id, created_at);
CREATE INDEX idx_citations_created_at ON citations(created_at);
CREATE INDEX idx_exports_created_at ON exports(created_at);
CREATE INDEX idx_audit_events_created_at ON audit_events(workspace_id, created_at);
CREATE INDEX idx_usage_events_created_at ON usage_events(workspace_id, created_at);

-- Pipeline queue index: (status, priority, created_at) on pipeline_jobs
CREATE INDEX idx_pipeline_jobs_queue ON pipeline_jobs(status, priority DESC, created_at);

-- Citations fast lookup: (draft_version_id) and (source_span_id)
-- Already covered by idx_citations_draft_version_id and idx_citations_source_span_id

-- Additional performance indexes
CREATE INDEX idx_source_pages_page_no ON source_pages(source_version_id, page_no);
CREATE INDEX idx_source_spans_offsets ON source_spans(page_id, start_offset, end_offset);
CREATE INDEX idx_job_attempts_attempt_no ON job_attempts(job_id, attempt_no);
CREATE INDEX idx_note_versions_created_at ON note_versions(note_id, created_at);
CREATE INDEX idx_draft_versions_created_at ON draft_versions(draft_id, created_at);
