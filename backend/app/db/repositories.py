from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
from uuid import UUID

from backend.app.models import (
    Workspace, Project, Source, SourceVersion, SourceFile,
    PipelineJob, JobAttempt, Draft, DraftVersion, Citation,
    User, WorkspaceMember, Role
)

class WorkspaceRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_workspace(self, name: str, slug: str, owner_id: UUID) -> Workspace:
        workspace = Workspace(name=name, slug=slug)
        self.session.add(workspace)
        self.session.flush()  # Get the ID

        # Add owner as member
        owner_role = self.session.query(Role).filter_by(name="owner").first()
        if not owner_role:
            raise ValueError("Owner role not found")

        member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=owner_id,
            role_id=owner_role.id
        )
        self.session.add(member)

        return workspace

    def get_workspace_by_slug(self, slug: str) -> Optional[Workspace]:
        return self.session.query(Workspace).filter_by(slug=slug).first()

    def list_user_workspaces(self, user_id: UUID) -> List[Workspace]:
        return self.session.query(Workspace).join(WorkspaceMember).filter(
            WorkspaceMember.user_id == user_id
        ).all()

class ProjectRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_project(self, workspace_id: UUID, name: str, description: str = None) -> Project:
        project = Project(
            workspace_id=workspace_id,
            name=name,
            description=description
        )
        self.session.add(project)
        return project

    def list_workspace_projects(self, workspace_id: UUID) -> List[Project]:
        return self.session.query(Project).filter_by(workspace_id=workspace_id).all()

class SourceRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_source(self, workspace_id: UUID, project_id: UUID, type: str, title: str, metadata: dict = None) -> Source:
        source = Source(
            workspace_id=workspace_id,
            project_id=project_id,
            type=type,
            title=title,
            metadata=metadata
        )
        self.session.add(source)
        return source

    def add_version(self, source_id: UUID, version_no: int, checksum: str, created_by: UUID) -> SourceVersion:
        version = SourceVersion(
            source_id=source_id,
            version_no=version_no,
            checksum=checksum,
            created_by=created_by
        )
        self.session.add(version)
        return version

    def attach_file(self, source_version_id: UUID, storage_provider: str, bucket: str, object_key: str, size: int, mime_type: str) -> SourceFile:
        file = SourceFile(
            source_version_id=source_version_id,
            storage_provider=storage_provider,
            bucket=bucket,
            object_key=object_key,
            size=size,
            mime_type=mime_type
        )
        self.session.add(file)
        return file

    def list_project_sources(self, project_id: UUID) -> List[Source]:
        return self.session.query(Source).filter_by(project_id=project_id).order_by(desc(Source.created_at)).all()

class PipelineJobRepository:
    def __init__(self, session: Session):
        self.session = session

    def enqueue_job(self, workspace_id: UUID, project_id: UUID, source_id: UUID = None, type: str = "process", priority: int = 0, payload: dict = None) -> PipelineJob:
        job = PipelineJob(
            workspace_id=workspace_id,
            project_id=project_id,
            source_id=source_id,
            type=type,
            priority=priority,
            payload=payload
        )
        self.session.add(job)
        return job

    def claim_next_job(self) -> Optional[PipelineJob]:
        # Get the highest priority queued job
        job = self.session.query(PipelineJob).filter_by(status="queued").order_by(
            desc(PipelineJob.priority), PipelineJob.created_at
        ).with_for_update().first()

        if job:
            job.status = "running"
            attempt = JobAttempt(job_id=job.id, attempt_no=1)
            self.session.add(attempt)

        return job

    def mark_job_success(self, job_id: UUID) -> None:
        job = self.session.query(PipelineJob).filter_by(id=job_id).first()
        if job:
            job.status = "success"
            attempt = self.session.query(JobAttempt).filter_by(job_id=job_id).order_by(desc(JobAttempt.attempt_no)).first()
            if attempt:
                attempt.finished_at = self.session.execute("SELECT NOW()").scalar()

    def mark_job_failed(self, job_id: UUID, error: dict = None) -> None:
        job = self.session.query(PipelineJob).filter_by(id=job_id).first()
        if job:
            job.status = "failed"
            attempt = self.session.query(JobAttempt).filter_by(job_id=job_id).order_by(desc(JobAttempt.attempt_no)).first()
            if attempt:
                attempt.finished_at = self.session.execute("SELECT NOW()").scalar()
                attempt.error_json = error

class DraftRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_draft(self, workspace_id: UUID, project_id: UUID, title: str, content: str) -> Draft:
        draft = Draft(
            workspace_id=workspace_id,
            project_id=project_id,
            title=title,
            content=content
        )
        self.session.add(draft)
        return draft

    def create_draft_version(self, draft_id: UUID, title: str, content: str) -> DraftVersion:
        version = DraftVersion(
            draft_id=draft_id,
            title=title,
            content=content
        )
        self.session.add(version)
        return version

    def list_draft_versions(self, draft_id: UUID) -> List[DraftVersion]:
        return self.session.query(DraftVersion).filter_by(draft_id=draft_id).order_by(desc(DraftVersion.created_at)).all()

class CitationRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_citation(self, draft_version_id: UUID, source_span_id: UUID, quote: str, confidence: float = 1.0) -> Citation:
        citation = Citation(
            draft_version_id=draft_version_id,
            source_span_id=source_span_id,
            quote=quote,
            confidence=confidence
        )
        self.session.add(citation)
        return citation

    def list_citations_for_draft_version(self, draft_version_id: UUID) -> List[Citation]:
        return self.session.query(Citation).filter_by(draft_version_id=draft_version_id).all()
