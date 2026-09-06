import json
import re
from typing import Dict, Any, List, Optional

from sqlalchemy.orm import Session

from app.rag.retriever import HybridRetriever
from app.llm.ollama_client import ollama_client
from app.core.config import settings
from app.core.logging import get_logger
from app.db.models import (
    Asset,
    Task,
    TaskStatus,
    WorkOrder,
    WorkOrderStatus,
    Approval,
    ApprovalStatus,
    Document,
    DocumentStatus,
)

logger = get_logger(__name__)

ASSET_PATTERN = re.compile(r"\b([A-Z]{1,4})-\d{3,6}\b", re.IGNORECASE)

ANALYSIS_SYSTEM_PROMPT = (
    "You are the data analysis module of an industrial AI workbench for ApexPetro Energy Limited. "
    "Produce a structured JSON analysis only. Never invent values. "
    "Every finding, metric, and recommendation must be traceable to the provided evidence or database facts. "
    "If the evidence does not answer the question, say so in the summary and set confidence to LOW."
)

ENVELOPE_SCHEMA_HINT = """{
  "summary": "1-3 sentence summary of the analysis",
  "findings": [{"title": "short finding", "detail": "grounded detail", "confidence": "HIGH|MEDIUM|LOW"}],
  "metrics": [{"name": "metric name", "value": "numeric or text value", "unit": "unit or empty", "status": "NORMAL|WARNING|CRITICAL|INFO"}],
  "charts": [{"type": "bar|line|radar", "title": "chart title", "data": [{"label": "x label", "value": 0}]}],
  "tables": [{"title": "table title", "headers": ["col1", "col2"], "rows": [["a", "b"]]}],
  "recommendations": [{"priority": "HIGH|MEDIUM|LOW", "action": "action text", "rationale": "why"}]
}"""


class AnalysisEngine:
    def __init__(self, db: Session, company_id: str):
        self.db = db
        self.company_id = company_id
        self.model = getattr(settings, "analysis_model", None) or "qwen2.5:3b"

    def extract_asset_id(self, query: str) -> Optional[str]:
        match = ASSET_PATTERN.search(query or "")
        if match:
            return match.group(0).upper().replace(" ", "")
        return None

    def _gather_db_facts(self, asset_id: Optional[str]) -> List[Dict[str, Any]]:
        facts: List[Dict[str, Any]] = []

        doc_count = self.db.query(Document).filter(
            Document.company_id == self.company_id,
            Document.status == DocumentStatus.READY,
        ).count()
        facts.append({
            "name": "Indexed documents",
            "value": str(doc_count),
            "unit": "",
            "status": "INFO",
        })

        open_tasks = self.db.query(Task).filter(
            Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.REVIEW]),
        ).count()
        facts.append({
            "name": "Open tasks",
            "value": str(open_tasks),
            "unit": "",
            "status": "WARNING" if open_tasks > 0 else "NORMAL",
        })

        open_wos = self.db.query(WorkOrder).filter(
            WorkOrder.company_id == self.company_id,
            WorkOrder.status.in_([WorkOrderStatus.OPEN, WorkOrderStatus.IN_PROGRESS]),
        ).count()
        facts.append({
            "name": "Open work orders",
            "value": str(open_wos),
            "unit": "",
            "status": "WARNING" if open_wos > 0 else "NORMAL",
        })

        pending_approvals = self.db.query(Approval).filter(
            Approval.status == ApprovalStatus.PENDING,
        ).count()
        facts.append({
            "name": "Pending approvals",
            "value": str(pending_approvals),
            "unit": "",
            "status": "INFO",
        })

        if asset_id:
            asset = self.db.query(Asset).filter(
                Asset.company_id == self.company_id,
                Asset.asset_id == asset_id,
            ).first()
            if asset:
                facts.append({
                    "name": "Asset criticality",
                    "value": asset.criticality or "UNSPECIFIED",
                    "unit": "",
                    "status": "CRITICAL" if (asset.criticality or "").upper() == "HIGH" else "INFO",
                })
                if asset.normal_pressure is not None:
                    facts.append({
                        "name": "Normal operating pressure",
                        "value": str(asset.normal_pressure),
                        "unit": "bar",
                        "status": "INFO",
                    })
                if asset.design_pressure is not None:
                    facts.append({
                        "name": "Design pressure",
                        "value": str(asset.design_pressure),
                        "unit": "bar",
                        "status": "INFO",
                    })

        return facts

    async def _gather_evidence(
        self, query: str, asset_id: Optional[str], limit: int = 8
    ) -> List[Dict[str, Any]]:
        try:
            retriever = HybridRetriever(self.db)
            results = await retriever.retrieve_with_metadata(
                query=query,
                company_id=self.company_id,
                asset_id=asset_id,
                limit=limit,
            )
        except Exception as e:
            logger.error("analysis_evidence_failed", error=str(e))
            return []

        evidence = []
        for r in results:
            evidence.append({
                "document_id": r.get("document_id"),
                "page": r.get("page_number"),
                "section": r.get("section"),
                "content": (r.get("content") or "")[:450],
            })
        return evidence

    def _build_prompt(
        self,
        query: str,
        asset_id: Optional[str],
        db_facts: List[Dict[str, Any]],
        evidence: List[Dict[str, Any]],
    ) -> str:
        facts_text = "\n".join(
            f"- {f['name']}: {f['value']} {f['unit']} ({f['status']})" for f in db_facts
        ) or "No database facts."

        evidence_text = "\n\n".join(
            f"Source {i + 1} ({e['document_id']}, page {e['page']}, {e['section'] or 'general'}):\n{e['content']}"
            for i, e in enumerate(evidence)
        ) or "No evidence retrieved."

        asset_line = f"Target asset identified from the question: {asset_id}." if asset_id else "No specific asset identified."

        return (
            f"Question: {query}\n\n"
            f"{asset_line}\n\n"
            f"Database facts (authoritative, do not contradict):\n{facts_text}\n\n"
            f"Retrieved knowledge evidence:\n{evidence_text}\n\n"
            f"Return ONLY valid JSON matching this schema:\n{ENVELOPE_SCHEMA_HINT}"
        )

    async def run(self, query: str) -> Dict[str, Any]:
        asset_id = self.extract_asset_id(query)
        db_facts = self._gather_db_facts(asset_id)
        evidence = await self._gather_evidence(query, asset_id)

        envelope = None
        try:
            response = await ollama_client.generate(
                model=self.model,
                prompt=self._build_prompt(query, asset_id, db_facts, evidence),
                system=ANALYSIS_SYSTEM_PROMPT,
                format="json",
                options={"temperature": 0.2, "top_p": 0.9},
            )
            envelope = self._parse_llm_json(response.get("response", ""))
        except Exception as e:
            logger.error("analysis_llm_failed", error=str(e))

        if not envelope:
            envelope = self._fallback_envelope(query, asset_id, db_facts, evidence)

        envelope.setdefault("_scope", {
            "asset_id": asset_id,
            "evidence_count": len(evidence),
            "db_fact_count": len(db_facts),
        })
        return envelope

    def _parse_llm_json(self, text: str) -> Optional[Dict[str, Any]]:
        if not text:
            return None
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

        candidate = None
        try:
            candidate = json.loads(text)
        except Exception:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    candidate = json.loads(match.group(0))
                except Exception:
                    return None
        if not isinstance(candidate, dict):
            return None

        return {
            "summary": candidate.get("summary") or "",
            "findings": candidate.get("findings") or [],
            "metrics": candidate.get("metrics") or [],
            "charts": candidate.get("charts") or [],
            "tables": candidate.get("tables") or [],
            "recommendations": candidate.get("recommendations") or [],
        }

    def _fallback_envelope(
        self,
        query: str,
        asset_id: Optional[str],
        db_facts: List[Dict[str, Any]],
        evidence: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        findings = []
        for i, e in enumerate(evidence[:4]):
            findings.append({
                "title": f"Retrieved source {i + 1}: {e['document_id']}",
                "detail": (e.get("content") or "")[:220],
                "confidence": "LOW",
            })
        if not findings:
            findings.append({
                "title": "No evidence retrieved",
                "detail": "The knowledge base returned no documents for this question.",
                "confidence": "LOW",
            })

        return {
            "summary": f"Automated analysis for '{query}'. Structured data unavailable; returning retrieved evidence and database facts.",
            "findings": findings,
            "metrics": db_facts,
            "charts": [],
            "tables": [],
            "recommendations": [
                {
                    "priority": "MEDIUM",
                    "action": "Re-run with a more specific asset or numeric question to obtain computed analysis.",
                    "rationale": "LLM structured analysis was not generated.",
                }
            ],
        }