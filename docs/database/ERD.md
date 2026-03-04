# Database Entity Relationship Diagram

## ASCII ERD

```
+----------------+     +-----------------+     +-----------------+
|     users      |     |   workspaces    |     |     roles       |
+----------------+     +-----------------+     +-----------------+
| id (UUID) PK   |     | id (UUID) PK    |     | id (UUID) PK    |
| email UNIQUE   |     | name            |     | name UNIQUE     |
| password_hash  |     | slug UNIQUE     |     +-----------------+
| name           |     +-----------------+     |
| status         |     |                 |     +-----------------+
| created_at     |     |                 |     |workspace_members|
| updated_at     |     +-----------------+     +-----------------+
+----------------+           |                       | workspace_id |
    |                        |                       | user_id      |
    |                        |                       | role_id      |
    |                        |                       +-------------+
+----------------+           |
|    sessions    |           |
+----------------+           |
| id (UUID) PK   |           |
| user_id FK     |-----------+
| refresh_token  |
| expires_at     |
+----------------+

+----------------+     +-----------------+     +-----------------+
|   api_keys     |     |    projects     |     |    sources      |
+----------------+     +-----------------+     +-----------------+
| id (UUID) PK   |     | id (UUID) PK    |     | id (UUID) PK    |
| user_id FK     |     | workspace_id FK |--+  | workspace_id FK |
| workspace_id FK|     | name            |  |  | project_id FK   |
| key_hash       |     | description     |  |  | type            |
| last_used_at   |     +-----------------+  |  | title           |
+----------------+                          |  | metadata JSONB  |
                                             |  +-----------------+
+----------------+                          |
|source_versions |                          |
+----------------+                          |
| id (UUID) PK   |                          |
| source_id FK   |<-------------------------+
| version_no     |
| checksum       |
| created_by FK  |
+----------------+
    |
    |  +-----------------+     +-----------------+
    +->|  source_files   |     |  source_pages   |
       +-----------------+     +-----------------+
       | id (UUID) PK    |     | id (UUID) PK    |
       | version_id FK   |     | version_id FK   |
       | storage_provider|     | page_no         |
       | bucket          |     | text            |
       | object_key      |     | ocr_status      |
       | size            |     +-----------------+
       | mime_type       |          |
       +-----------------+          |
                                   |
+----------------+                |
|  source_spans  |                |
+----------------+                |
| id (UUID) PK   |<---------------+
| page_id FK     |
| start_offset   |
| end_offset     |
| snippet        |
+----------------+
    ^
    |
    |  +-----------------+     +-----------------+
    +--|   citations     |     | draft_versions |
       +-----------------+     +-----------------+
       | id (UUID) PK    |     | id (UUID) PK    |
       | draft_ver_id FK |     | draft_id FK     |
       | source_span_id  |     | title           |
       | quote           |     | content         |
       | confidence      |     +-----------------+
       +-----------------+          ^
                                    |
+----------------+                |
|    drafts      |                |
+----------------+                |
| id (UUID) PK   |                |
| workspace_id FK|                |
| project_id FK  |<---------------+
| title          |
| content        |
+----------------+

+----------------+     +-----------------+     +-----------------+
|pipeline_jobs   |     |  job_attempts   |     |  audit_events   |
+----------------+     +-----------------+     +-----------------+
| id (UUID) PK   |     | id (UUID) PK    |     | id (UUID) PK    |
| workspace_id FK|     | job_id FK       |     | workspace_id FK |
| project_id FK  |     | attempt_no      |     | actor_user_id FK|
| source_id FK   |     | started_at      |     | action          |
| type           |     | finished_at     |     | entity_type     |
| status         |     | error_json      |     | entity_id       |
| priority       |     +-----------------+     | payload JSONB   |
| payload JSONB  |                             +-----------------+
+----------------+

+----------------+     +-----------------+     +-----------------+
|    exports     |     | export_files    |     | usage_events    |
+----------------+     +-----------------+     +-----------------+
| id (UUID) PK   |     | id (UUID) PK    |     | id (UUID) PK    |
| draft_ver_id FK|     | export_id FK    |     | workspace_id FK |
| format         |     | storage_provider|     | type            |
| status         |     | bucket          |     | amount          |
+----------------+     | object_key      |     | meta JSONB      |
                       | checksum        |     +-----------------+
                       | size            |
                       | mime_type       |
                       +-----------------+
```

## Key Relationships

- **Users** authenticate via **sessions** and **api_keys**
- **Workspaces** contain **projects** and have **members** with **roles**
- **Projects** contain **sources**, **drafts**, and **notes**
- **Sources** have multiple **versions** with **files** and **pages**
- **Pages** contain **spans** that are cited in **drafts**
- **Drafts** have immutable **versions** linked to **citations**
- **Pipeline jobs** process sources with **attempts** tracking retries
- **Audit events** log all system actions
- **Usage events** track billing metrics

## Multi-tenancy

All major entities include `workspace_id` for tenant isolation, ensuring data separation between organizations.
