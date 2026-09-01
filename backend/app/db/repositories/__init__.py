from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models import (
    User, Company, Document, DocumentChunk, Asset,
    Project, Task, AgentRun, AgentStep, Artifact,
    Approval, WorkOrder, AuditEvent, ModelRegistry,
    Conversation, Message,
    UserRole, DocumentStatus, ArtifactStatus, AgentRunStatus, AgentStepStatus
)


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, email: str, hashed_password: str, full_name: str, role: UserRole, company_id: str) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            company_id=company_id,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, company_id: str) -> Optional[Company]:
        return self.db.query(Company).filter(Company.company_id == company_id).first()

    def create(self, **kwargs) -> Company:
        company = Company(**kwargs)
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, doc_id: str, company_id: str) -> Optional[Document]:
        return self.db.query(Document).filter(
            Document.document_id == doc_id,
            Document.company_id == company_id
        ).first()

    def get_by_db_id(self, db_id: int, company_id: str) -> Optional[Document]:
        return self.db.query(Document).filter(
            Document.id == db_id,
            Document.company_id == company_id
        ).first()

    def list(self, company_id: str, skip: int = 0, limit: int = 50) -> List[Document]:
        return self.db.query(Document).filter(
            Document.company_id == company_id
        ).offset(skip).limit(limit).all()

    def create(self, **kwargs) -> Document:
        doc = Document(**kwargs)
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def update_status(self, doc_id: int, status: DocumentStatus, error: str = None, indexed_at: bool = False) -> Optional[Document]:
        doc = self.db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.status = status
            if error:
                doc.error_message = error
            if indexed_at:
                from datetime import datetime
                doc.indexed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(doc)
        return doc


class DocumentChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_batch(self, chunks: List[DocumentChunk]) -> None:
        self.db.add_all(chunks)
        self.db.commit()

    def get_by_document(self, document_id: int) -> List[DocumentChunk]:
        return self.db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_index).all()

    def get_by_qdrant_ids(self, point_ids: List[str]) -> List[DocumentChunk]:
        return self.db.query(DocumentChunk).filter(
            DocumentChunk.qdrant_point_id.in_(point_ids)
        ).all()


class AssetRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, asset_id: str, company_id: str) -> Optional[Asset]:
        return self.db.query(Asset).filter(
            Asset.asset_id == asset_id,
            Asset.company_id == company_id
        ).first()

    def list(self, company_id: str) -> List[Asset]:
        return self.db.query(Asset).filter(Asset.company_id == company_id).all()

    def search(self, company_id: str, query: str) -> List[Asset]:
        return self.db.query(Asset).filter(
            Asset.company_id == company_id,
            (Asset.asset_id.ilike(f"%{query}%")) |
            (Asset.asset_type.ilike(f"%{query}%")) |
            (Asset.service.ilike(f"%{query}%"))
        ).all()

    def create(self, **kwargs) -> Asset:
        asset = Asset(**kwargs)
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, project_id: str, company_id: str) -> Optional[Project]:
        return self.db.query(Project).filter(
            Project.project_id == project_id,
            Project.company_id == company_id
        ).first()

    def list(self, company_id: str) -> List[Project]:
        return self.db.query(Project).filter(Project.company_id == company_id).all()

    def create(self, **kwargs) -> Project:
        project = Project(**kwargs)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_project(self, project_id: int) -> List[Task]:
        return self.db.query(Task).filter(Task.project_id == project_id).all()


class AgentRunRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> AgentRun:
        run = AgentRun(**kwargs)
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def get_by_id(self, run_id: str) -> Optional[AgentRun]:
        return self.db.query(AgentRun).filter(AgentRun.run_id == run_id).first()

    def update_status(self, run_id: str, status: AgentRunStatus, completed_at=None, error=None) -> Optional[AgentRun]:
        run = self.db.query(AgentRun).filter(AgentRun.run_id == run_id).first()
        if run:
            run.status = status
            if completed_at:
                run.completed_at = completed_at
            if error:
                run.error_message = error
            self.db.commit()
            self.db.refresh(run)
        return run


class AgentStepRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_batch(self, steps: List[AgentStep]) -> None:
        self.db.add_all(steps)
        self.db.commit()

    def update_step(self, step_id: int, status: AgentStepStatus, output: Dict = None, duration_ms: int = None, error: str = None) -> Optional[AgentStep]:
        step = self.db.query(AgentStep).filter(AgentStep.id == step_id).first()
        if step:
            step.status = status
            if output:
                step.output_data = output
            if duration_ms:
                step.duration_ms = duration_ms
            if error:
                step.error_message = error
            if status in [AgentStepStatus.COMPLETED, AgentStepStatus.FAILED]:
                from datetime import datetime
                step.completed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(step)
        return step


class ArtifactRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> Artifact:
        artifact = Artifact(**kwargs)
        self.db.add(artifact)
        self.db.commit()
        self.db.refresh(artifact)
        return artifact

    def get_by_id(self, artifact_id: str, company_id: str) -> Optional[Artifact]:
        return self.db.query(Artifact).filter(
            Artifact.artifact_id == artifact_id,
            Artifact.company_id == company_id
        ).first()

    def list(self, company_id: str, project_id: Optional[int] = None) -> List[Artifact]:
        query = self.db.query(Artifact).filter(Artifact.company_id == company_id)
        if project_id:
            query = query.filter(Artifact.project_id == project_id)
        return query.all()

    def update_status(self, artifact_id: int, status: ArtifactStatus) -> Optional[Artifact]:
        artifact = self.db.query(Artifact).filter(Artifact.id == artifact_id).first()
        if artifact:
            artifact.status = status
            self.db.commit()
            self.db.refresh(artifact)
        return artifact


class ApprovalRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> Approval:
        approval = Approval(**kwargs)
        self.db.add(approval)
        self.db.commit()
        self.db.refresh(approval)
        return approval

    def get_by_artifact(self, artifact_id: int) -> Optional[Approval]:
        return self.db.query(Approval).filter(Approval.artifact_id == artifact_id).first()

    def update_status(self, approval_id: int, status, reviewed_by: int, comments: str = None) -> Optional[Approval]:
        approval = self.db.query(Approval).filter(Approval.id == approval_id).first()
        if approval:
            approval.status = status
            approval.reviewed_by = reviewed_by
            approval.comments = comments
            from datetime import datetime
            approval.reviewed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(approval)
        return approval


class WorkOrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_asset(self, asset_id: str, company_id: str) -> List[WorkOrder]:
        return self.db.query(WorkOrder).filter(
            WorkOrder.asset_id == asset_id,
            WorkOrder.company_id == company_id
        ).all()


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def log(self, **kwargs) -> AuditEvent:
        event = AuditEvent(**kwargs)
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def list(self, company_id: str, limit: int = 100) -> List[AuditEvent]:
        return self.db.query(AuditEvent).filter(
            AuditEvent.company_id == company_id
        ).order_by(AuditEvent.timestamp.desc()).limit(limit).all()


class ModelRegistryRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert(self, **kwargs) -> ModelRegistry:
        model = self.db.query(ModelRegistry).filter(ModelRegistry.model_id == kwargs["model_id"]).first()
        if model:
            for k, v in kwargs.items():
                setattr(model, k, v)
        else:
            model = ModelRegistry(**kwargs)
            self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def list(self) -> List[ModelRegistry]:
        return self.db.query(ModelRegistry).all()

    def get_by_id(self, model_id: str) -> Optional[ModelRegistry]:
        return self.db.query(ModelRegistry).filter(ModelRegistry.model_id == model_id).first()


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_by_conversation_id(self, conversation_id: str, company_id: str, user_id: int) -> Conversation:
        conv = self.db.query(Conversation).filter(Conversation.conversation_id == conversation_id).first()
        if not conv:
            conv = Conversation(
                conversation_id=conversation_id,
                company_id=company_id,
                user_id=user_id,
            )
            self.db.add(conv)
            self.db.commit()
            self.db.refresh(conv)
        return conv

    def list_by_user(self, company_id: str, user_id: int, limit: int = 50) -> List[Conversation]:
        return self.db.query(Conversation).filter(
            Conversation.company_id == company_id,
            Conversation.user_id == user_id,
        ).order_by(Conversation.updated_at.desc()).limit(limit).all()

    def get_messages(self, conversation_id: str, limit: int = 100) -> List[Message]:
        conv = self.db.query(Conversation).filter(Conversation.conversation_id == conversation_id).first()
        if not conv:
            return []
        return self.db.query(Message).filter(
            Message.conversation_id == conv.id
        ).order_by(Message.id.asc()).limit(limit).all()

    def add_message(self, conversation_id: str, user_id: int, role: str, content: str, run_id: str = None) -> Message:
        import uuid
        conv = self.db.query(Conversation).filter(Conversation.conversation_id == conversation_id).first()
        if not conv:
            raise ValueError("Conversation not found")
        msg = Message(
            message_id=str(uuid.uuid4()),
            conversation_id=conv.id,
            user_id=user_id,
            role=role,
            content=content,
            run_id=run_id,
        )
        self.db.add(msg)
        conv.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(msg)
        return msg