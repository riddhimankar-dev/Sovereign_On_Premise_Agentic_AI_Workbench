from typing import Dict, Any
from app.tools.base import BaseTool, ToolInput, ToolOutput, tool_registry
from app.db.repositories import DocumentRepository, DocumentChunkRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class DocumentReaderInput(ToolInput):
    document_id: str
    page_number: int = None
    section: str = None


class DocumentReaderTool(BaseTool):
    name = "read_document"
    description = "Read specific document content by ID, optionally filtered by page or section"
    permission = "read"

    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> ToolOutput:
        db = context.get("db")
        company_id = context.get("company_id")

        if not db or not company_id:
            return ToolOutput(success=False, error="Missing db or company_id in context")

        doc_repo = DocumentRepository(db)
        chunk_repo = DocumentChunkRepository(db)

        document_id = input_data.get("document_id")
        page_number = input_data.get("page_number")
        section = input_data.get("section")

        doc = doc_repo.get_by_id(document_id, company_id)
        if not doc:
            return ToolOutput(success=False, error=f"Document {document_id} not found")

        chunks = chunk_repo.get_by_document(doc.id)

        if page_number is not None:
            chunks = [c for c in chunks if c.page_number == page_number]
        if section:
            chunks = [c for c in chunks if section.lower() in (c.section or "").lower()]

        content = "\n\n".join([c.content for c in chunks])

        return ToolOutput(success=True, data={
            "document_id": doc.document_id,
            "file_name": doc.file_name,
            "classification": doc.classification,
            "page_number": page_number,
            "section": section,
            "content": content,
            "chunk_count": len(chunks),
        })


tool_registry.register(DocumentReaderTool())