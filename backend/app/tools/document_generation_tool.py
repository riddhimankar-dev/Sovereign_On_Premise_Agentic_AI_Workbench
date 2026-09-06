import json
import os
import re
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.tools.base import BaseTool, ToolInput, ToolOutput, tool_registry
from app.rag.retriever import HybridRetriever
from app.llm.ollama_client import ollama_client
from app.services.file_document_generator import (
    render_document,
    extract_document_data,
    SUPPORTED_TEMPLATES,
    SECTION_TEMPLATES,
    MANAGEMENT_SUMMARY_SLIDES,
    RISK_ASSESSMENT_SHEETS,
)
from app.db.models import Artifact, ArtifactType, ArtifactStatus, DocumentClassification, Approval, ApprovalStatus
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

ARTIFACT_DIR = "/home/aum/Desktop/ML/Smart India Hackathon/backend/artifacts"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

TEMPLATE_HINTS = {
    "approval_note": ["approval note", "approval", "sign-off", "ask for approval"],
    "technical_review": ["technical review", "engineering review", "review report"],
    "inspection_report": ["inspection report", "inspection"],
    "risk_assessment": ["risk assessment", "risk register", "hazard analysis"],
    "management_summary": ["management summary", "executive summary", "summary for management", "board summary"],
}

FORMAT_HINTS = {
    "docx": ["word", "docx", ".docx"],
    "pdf": ["pdf", "printable"],
    "xlsx": ["excel", "xlsx", "spreadsheet", "a sheet", "in a sheet", "in excel"],
    "pptx": ["powerpoint", "pptx", "slides", "deck", "make a ppt", "a ppt", "in ppt"],
    "txt": ["text file", "txt", ".txt", "plain text"],
    "json": ["json", ".json"],
    "md": ["markdown", ".md", "md file", "mark-down"],
    "csv": ["csv", ".csv", "comma separated"],
}

FILL_SYSTEM_PROMPT = (
    "You are the document generation module of an industrial AI workbench for ApexPetro Energy Limited. "
    "Fill the requested document sections using ONLY the provided evidence and database facts. "
    "Do not invent numbers. If evidence is missing, write 'Not specified in available knowledge.' "
    "Return ONLY a JSON object."
)


class GenerateDocumentInput(ToolInput):
    query: str
    template: Optional[str] = None
    format: Optional[str] = None
    project_id: Optional[int] = None


class GenerateDocumentTool(BaseTool):
    name = "generate_document"
    description = (
        "Generate a company document from a template (approval_note, technical_review, inspection_report, "
        "risk_assessment, management_summary) using evidence from the knowledge base. Creates an artifact."
    )
    permission = "write"

    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> ToolOutput:
        db = context.get("db")
        company_id = context.get("company_id")
        user_id = context.get("user_id")

        if not db or not company_id:
            return ToolOutput(success=False, error="Missing db or company_id in context")

        query = input_data.get("query", "")
        template = (input_data.get("template") or self._detect_template(query)).lower()
        format = (input_data.get("format") or self._detect_format(query)).lower()

        if template not in SUPPORTED_TEMPLATES:
            return ToolOutput(success=False, error=f"Unsupported template: {template}")
        if format not in SUPPORTED_TEMPLATES[template]:
            format = SUPPORTED_TEMPLATES[template][0]

        evidence = await self._gather_evidence(db, company_id, query)
        fill = await self._build_data(query, template, format, evidence)

        try:
            content = render_document(template, format, fill)
        except Exception as e:
            logger.error("doc_render_failed", template=template, format=format, error=str(e))
            return ToolOutput(success=False, error=f"Render failed: {str(e)}")

        artifact_id = str(uuid.uuid4())
        file_name = f"{artifact_id}.{format}"
        file_path = os.path.join(ARTIFACT_DIR, file_name)
        try:
            with open(file_path, "wb") as f:
                f.write(content)
        except Exception as e:
            return ToolOutput(success=False, error=f"Write failed: {str(e)}")

        artifact = Artifact(
            artifact_id=artifact_id,
            company_id=company_id,
            name=fill.get("title") or f"{template}_{datetime.utcnow().strftime('%Y%m%d')}",
            artifact_type=ArtifactType(format.upper()),
            file_path=file_path,
            status=ArtifactStatus.READY_FOR_REVIEW,
            classification=DocumentClassification.CONFIDENTIAL,
            created_by=user_id or 1,
            sources=[
                {"title": e.get("document_id"), "section": e.get("section")}
                for e in evidence[:6]
            ],
            ai_provenance={
                "tool": "generate_document",
                "template": template,
                "format": format,
            },
        )
        db.add(artifact)
        db.commit()
        db.refresh(artifact)

        approval = None
        try:
            approval = Approval(
                approval_id=f"APR-{uuid.uuid4().hex[:10].upper()}",
                artifact_id=artifact.id,
                requested_by=user_id or 1,
                status=ApprovalStatus.PENDING,
                comments=f"AI-generated {template.replace('_', ' ')} awaiting human review",
            )
            db.add(approval)
            db.commit()
            db.refresh(approval)
        except Exception as e:
            logger.error("approval_creation_failed", error=str(e))
            db.rollback()

        return ToolOutput(success=True, data={
            "artifact_id": artifact_id,
            "name": artifact.name,
            "template": template,
            "format": format,
            "file_path": file_path,
            "download_url": f"/api/artifacts/{artifact_id}/download",
            "title": fill.get("title"),
            "approval_id": approval.approval_id if approval else None,
        })

    def _detect_template(self, query: str) -> str:
        query_lower = (query or "").lower()
        for template, hints in TEMPLATE_HINTS.items():
            if any(h in query_lower for h in hints):
                return template
        return "approval_note"

    def _detect_format(self, query: str) -> str:
        query_lower = (query or "").lower()
        for format, hints in FORMAT_HINTS.items():
            if any(h in query_lower for h in hints):
                return format
        return "docx"

    async def _gather_evidence(self, db, company_id: str, query: str, limit: int = 8) -> List[Dict[str, Any]]:
        try:
            retriever = HybridRetriever(db)
            results = await retriever.retrieve_with_metadata(
                query=query, company_id=company_id, asset_id=None, limit=limit
            )
        except Exception as e:
            logger.error("doc_evidence_failed", error=str(e))
            return []
        return [
            {
                "document_id": r.get("document_id"),
                "page": r.get("page_number"),
                "section": r.get("section"),
                "content": (r.get("content") or "")[:450],
            }
            for r in results
        ]

    async def _build_data(
        self, query: str, template: str, format: str, evidence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        sections_by_template: Dict[str, Any] = {
            "approval_note": SECTION_TEMPLATES.get("approval_note"),
            "technical_review": SECTION_TEMPLATES.get("technical_review"),
            "inspection_report": SECTION_TEMPLATES.get("inspection_report"),
            "risk_assessment": RISK_ASSESSMENT_SHEETS,
            "management_summary": MANAGEMENT_SUMMARY_SLIDES,
        }
        section_names = sections_by_template.get(template, [])

        evidence_text = "\n\n".join(
            f"Source {i + 1} ({e['document_id']}, page {e['page']}, {e['section'] or 'general'}):\n{e['content']}"
            for i, e in enumerate(evidence)
        ) or "No evidence retrieved."

        schema = {"title": "document title"}
        if template == "risk_assessment":
            schema["sheets"] = {name: {"headers": ["Item", "Detail", "Status"], "rows": [["Example", "Not specified", "OPEN"]]} for name in section_names}
        elif template == "management_summary":
            schema["slides"] = {name: ["bullet point 1"] for name in section_names}
        else:
            schema["sections"] = {name: "short grounded paragraph" for name in section_names}

        prompt = (
            f"Template: {template}\n\n"
            f"User request: {query}\n\n"
            f"Retrieved evidence (use ONLY this evidence, quoted or paraphrased verbatim, never invent numbers):\n"
            f"{evidence_text}\n\n"
            f"Return ONLY JSON matching exactly this shape (all keys included; replace each value with real "
            f"content grounded in the evidence above):\n{json.dumps(schema)}"
        )

        data = None
        for model in (settings.primary_model, "qwen2.5:3b"):
            try:
                response = await ollama_client.generate(
                    model=model,
                    prompt=prompt,
                    system=FILL_SYSTEM_PROMPT,
                    format="json",
                    options={"temperature": 0.3, "top_p": 0.9},
                )
                data = self._parse_json(response.get("response", ""))
                if data:
                    break
            except Exception as e:
                logger.error("doc_fill_failed", model=model, error=str(e))
                data = None

        if data:
            data["title"] = data.get("title") or f"{template.replace('_', ' ').title()} - {query[:60]}"
            self._fill_empty_sections(data, section_names, evidence)
            return data

        return self._fallback_data(template, format, query, section_names, evidence)

    def _fill_empty_sections(
        self, data: Dict[str, Any], section_names: List[str], evidence: List[Dict[str, Any]]
    ) -> None:
        filler = "Not specified in available knowledge."
        fallback = [e.get("content") or "" for e in evidence if e.get("content")]
        idx = 0

        def _resolve(value: Any) -> bool:
            nonlocal idx
            if value is None:
                return False
            if isinstance(value, str) and value.strip() and filler not in value:
                return True
            if isinstance(value, list):
                return any(isinstance(i, str) and i.strip() and filler not in i for i in value)
            return isinstance(value, dict) and bool(value)

        sections_box = data.get("sections")
        if isinstance(sections_box, dict):
            for name in section_names:
                for key in sections_box.keys():
                    if key.lower() == name.lower() and not _resolve(sections_box[key]):
                        if idx < len(fallback):
                            sections_box[key] = fallback[idx][:350]
                            idx += 1
                        else:
                            sections_box[key] = filler

        sheets = data.get("sheets")
        if isinstance(sheets, dict):
            for name in section_names:
                sheet = sheets.get(name)
                if not isinstance(sheet, dict):
                    continue
                rows = sheet.get("rows") or []
                placeholder = not rows
                if rows and len(rows) == 1:
                    row = rows[0]
                    if isinstance(row, dict):
                        detail = str(row.get("Detail", ""))
                        placeholder = row.get("Item") == "Example" or "Not specified in available knowledge." in detail
                    elif isinstance(row, (list, tuple)) and row:
                        detail = str(row[1]) if len(row) > 1 else ""
                        placeholder = row[0] == "Example" or "Not specified in available knowledge." in detail
                if placeholder and idx < len(fallback):
                    sheet["rows"] = [[name, fallback[idx][:320], "OPEN"]]
                    idx += 1

        slides = data.get("slides")
        if isinstance(slides, dict):
            for name in section_names:
                content = slides.get(name)
                if not isinstance(content, list) or not content or filler in content[0]:
                    if idx < len(fallback):
                        slides[name] = [fallback[idx][:320]]
                        idx += 1

    def _fallback_data(
        self,
        template: str,
        format: str,
        query: str,
        section_names: List[str],
        evidence: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        sections = {}
        for name in section_names:
            for e in evidence:
                content = e.get("content") or ""
                if content:
                    sections[name] = content[:300]
                    break
            sections.setdefault(name, f"Not specified in available knowledge for: {name}")

        if template == "risk_assessment":
            sheets = {}
            for name in section_names:
                sheets[name] = {
                    "headers": ["Item", "Detail", "Status"],
                    "rows": [[name, sections.get(name, ""), "OPEN"]],
                }
            return {"title": f"Risk Assessment - {query[:60]}", "sheets": sheets}
        if template == "management_summary":
            return {"title": f"Management Summary - {query[:60]}", "slides": {name: [sections.get(name, "")] for name in section_names}}
        return {
            "title": f"{template.replace('_', ' ').title()} - {query[:60]}",
            "sections": sections,
        }

    def _parse_json(self, text: str) -> Optional[Dict[str, Any]]:
        if not text:
            return None
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        try:
            candidate = json.loads(text)
        except Exception:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                return None
            try:
                candidate = json.loads(match.group(0))
            except Exception:
                return None
        return candidate if isinstance(candidate, dict) else None


tool_registry.register(GenerateDocumentTool())


class UpdateArtifactInput(ToolInput):
    artifact_id: str
    change_instruction: Optional[str] = None


class UpdateArtifactTool(BaseTool):
    name = "update_artifact"
    description = (
        "Apply a follow-up change/refinement to an existing generated artifact (e.g. add a section, "
        "expand a finding, update a value). Creates a new version (v2, v3, ...) of the artifact."
    )
    permission = "write"

    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> ToolOutput:
        db = context.get("db")
        company_id = context.get("company_id")
        user_id = context.get("user_id")
        artifact_id = input_data.get("artifact_id")
        change_instruction = input_data.get("change_instruction") or ""

        if not db or not company_id:
            return ToolOutput(success=False, error="Missing db or company_id in context")

        artifact = db.query(Artifact).filter(Artifact.artifact_id == artifact_id).first()
        if not artifact:
            return ToolOutput(success=False, error=f"Artifact not found: {artifact_id}")

        template = (artifact.ai_provenance or {}).get("template") or "approval_note"
        format = (artifact.ai_provenance or {}).get("format") or "docx"
        format = format.lower()

        evidence = await self._gather_evidence(db, company_id, change_instruction or artifact.name, limit=6)
        existing = self._load_existing_data(artifact.file_path, format)

        new_data = await self._build_updated_data(artifact.name, change_instruction, template, format, existing, evidence)

        try:
            content = render_document(template, format, new_data)
        except Exception as e:
            logger.error("update_render_failed", error=str(e))
            return ToolOutput(success=False, error=f"Render failed: {str(e)}")

        next_version = (artifact.version or 1) + 1
        new_artifact_id = str(uuid.uuid4())
        file_name = f"{new_artifact_id}.{format}"
        file_path = os.path.join(ARTIFACT_DIR, file_name)
        try:
            with open(file_path, "wb") as f:
                f.write(content)
        except Exception as e:
            return ToolOutput(success=False, error=f"Write failed: {str(e)}")

        new_artifact = Artifact(
            artifact_id=new_artifact_id,
            company_id=company_id,
            project_id=artifact.project_id,
            name=artifact.name,
            artifact_type=ArtifactType(format.upper()),
            file_path=file_path,
            status=ArtifactStatus.READY_FOR_REVIEW,
            classification=artifact.classification or DocumentClassification.CONFIDENTIAL,
            created_by=user_id or 1,
            sources=artifact.sources or [],
            ai_provenance={
                "tool": "update_artifact",
                "template": template,
                "format": format,
                "change_instruction": change_instruction,
                "previous_artifact_id": artifact_id,
            },
            version=next_version,
            parent_artifact_id=artifact.parent_artifact_id or artifact_id,
        )
        db.add(new_artifact)
        db.commit()
        db.refresh(new_artifact)

        return ToolOutput(success=True, data={
            "artifact_id": new_artifact_id,
            "name": new_artifact.name,
            "template": template,
            "format": format,
            "version": new_artifact.version,
            "parent_artifact_id": new_artifact.parent_artifact_id,
            "file_path": file_path,
            "download_url": f"/api/artifacts/{new_artifact_id}/download",
        })

    def _load_existing_data(self, file_path: Optional[str], format: str) -> Dict[str, Any]:
        if not file_path or not os.path.exists(file_path):
            return {}
        return extract_document_data(file_path, format)

    async def _gather_evidence(self, db, company_id: str, query: str, limit: int = 6) -> List[Dict[str, Any]]:
        try:
            retriever = HybridRetriever(db)
            results = await retriever.retrieve_with_metadata(
                query=query, company_id=company_id, asset_id=None, limit=limit
            )
        except Exception as e:
            logger.error("update_evidence_failed", error=str(e))
            return []
        return [
            {"document_id": r.get("document_id"), "page": r.get("page_number"),
             "section": r.get("section"), "content": (r.get("content") or "")[:450]}
            for r in results
        ]

    async def _build_updated_data(self, title: str, change_instruction: str, template: str,
                                  format: str, existing: Dict[str, Any],
                                  evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        evidence_text = "\n\n".join(
            f"Source {i + 1} ({e['document_id']}, page {e['page'] or '?'}):\n{e['content']}"
            for i, e in enumerate(evidence)
        ) or "No evidence retrieved."

        prompt = (
            f"You are revising an existing document artifact.\n"
            f"Document title: {title}\n"
            f"Template: {template}\n"
            f"Format: {format}\n"
            f"Current content (JSON): {json.dumps(existing)}\n\n"
            f"User's change request: {change_instruction}\n\n"
            f"Relevant evidence (use only this, never invent numbers):\n{evidence_text}\n\n"
            f"Return ONLY a JSON object with the same top-level structure as the current content "
            f"(keep 'title', 'sections'/'sheets'/'slides'/'rows' as appropriate), applying the requested change. "
            f"Produces the new content fully."
        )

        data = None
        for model in (settings.primary_model, "qwen2.5:3b"):
            try:
                response = await ollama_client.generate(
                    model=model, prompt=prompt, system=FILL_SYSTEM_PROMPT,
                    format="json", options={"temperature": 0.3, "top_p": 0.9},
                )
                data = self._parse_json(response.get("response", ""))
                if data:
                    break
            except Exception as e:
                logger.error("update_fill_failed", model=model, error=str(e))
                data = None

        if data:
            data.setdefault("title", title)
            return data
        return self._merge_change(existing, change_instruction, title)

    def _merge_change(self, existing: Dict[str, Any], change: str, title: str) -> Dict[str, Any]:
        result = dict(existing)
        result.setdefault("title", title)
        sections = result.get("sections")
        if isinstance(sections, dict):
            sections.setdefault("Change Log", f"Updated: {change} — note that no new evidence was available; content preserved as-is.")
            result["sections"] = sections
        return result

    def _parse_json(self, text: str) -> Optional[Dict[str, Any]]:
        if not text:
            return None
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        try:
            return json.loads(text) if isinstance(json.loads(text), dict) else None
        except Exception:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                return None
            try:
                return json.loads(match.group(0))
            except Exception:
                return None


tool_registry.register(UpdateArtifactTool())


class ConvertArtifactInput(ToolInput):
    artifact_id: str
    format: str


class ConvertArtifactTool(BaseTool):
    name = "convert_artifact"
    description = (
        "Convert an existing artifact to a different file format (e.g. convert a docx approval note to pdf). "
        "Creates a new artifact in the target format."
    )
    permission = "write"

    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> ToolOutput:
        db = context.get("db")
        company_id = context.get("company_id")
        user_id = context.get("user_id")
        artifact_id = input_data.get("artifact_id")
        target_format = (input_data.get("format") or "").lower().lstrip(".")

        if not db or not company_id:
            return ToolOutput(success=False, error="Missing db or company_id in context")

        artifact = db.query(Artifact).filter(Artifact.artifact_id == artifact_id).first()
        if not artifact:
            return ToolOutput(success=False, error=f"Artifact not found: {artifact_id}")

        template = (artifact.ai_provenance or {}).get("template") or "approval_note"
        source_format = (artifact.ai_provenance or {}).get("format") or "docx"
        data = extract_document_data(artifact.file_path or "", source_format)
        if not data:
            data = {}
        data.setdefault("title", artifact.name)

        try:
            content = render_document(template, target_format, data)
        except Exception as e:
            logger.error("convert_render_failed", error=str(e))
            return ToolOutput(success=False, error=f"Render failed for format {target_format}: {str(e)}")

        new_artifact_id = str(uuid.uuid4())
        file_name = f"{new_artifact_id}.{target_format}"
        file_path = os.path.join(ARTIFACT_DIR, file_name)
        with open(file_path, "wb") as f:
            f.write(content)

        new_artifact = Artifact(
            artifact_id=new_artifact_id,
            company_id=company_id,
            project_id=artifact.project_id,
            name=artifact.name,
            artifact_type=ArtifactType(target_format.upper()),
            file_path=file_path,
            status=ArtifactStatus.READY_FOR_REVIEW,
            classification=artifact.classification or DocumentClassification.CONFIDENTIAL,
            created_by=user_id or 1,
            sources=artifact.sources or [],
            ai_provenance={"tool": "convert_artifact", "template": template, "format": target_format,
                           "original_artifact_id": artifact_id},
            parent_artifact_id=artifact.parent_artifact_id or artifact_id,
        )
        db.add(new_artifact)
        db.commit()
        db.refresh(new_artifact)

        return ToolOutput(success=True, data={
            "artifact_id": new_artifact_id,
            "name": new_artifact.name,
            "template": template,
            "format": target_format,
            "file_path": file_path,
            "download_url": f"/api/artifacts/{new_artifact_id}/download",
        })


tool_registry.register(ConvertArtifactTool())