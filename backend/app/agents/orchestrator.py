from typing import Dict, Any, AsyncGenerator, List, Optional

from app.agents.state import AgentState, AgentPhase
from app.agents.planner import planner
from app.agents.executor import executor
from app.agents.verifier import verifier
from app.agents.greetings import fast_path_response, greet
from app.llm.router import model_router
from app.core.config import settings
from app.core.logging import get_logger
from app.db.models import AgentRun, AgentRunStatus

import json
import uuid
import httpx


logger = get_logger(__name__)


# =============================================================
# LOCAL OLLAMA CLIENT
# =============================================================

class LocalOllamaClient:
    """
    Small built-in Ollama client.

    This avoids depending on:
        app.llm.ollama_client

    Ollama is expected to run locally at:
        http://localhost:11434
    """

    def __init__(self):
        self.base_url = getattr(
            settings,
            "ollama_base_url",
            "http://localhost:11434",
        ).rstrip("/")

    async def is_model_available(self, model: str) -> bool:
        """
        Check whether the requested Ollama model exists locally.
        """

        if not model:
            return False

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/tags"
                )

                response.raise_for_status()

                data = response.json()

                models = data.get("models", [])

                for item in models:
                    name = item.get("name", "")

                    if name == model:
                        return True

                    # Also support model names such as:
                    # qwen2.5:7b vs qwen2.5:7b-instruct
                    if name.split(":")[0] == model.split(":")[0]:
                        return True

                return False

        except Exception as e:
            logger.warning(
                "ollama_model_check_failed",
                model=model,
                error=str(e),
            )

            return False

    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a response from local Ollama.
        """

        if not model:
            raise RuntimeError(
                "No Ollama model was selected."
            )

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }

        if system:
            payload["system"] = system

        if options:
            payload["options"] = options

        try:

            async with httpx.AsyncClient(
                timeout=httpx.Timeout(
                    connect=10.0,
                    read=180.0,
                    write=30.0,
                    pool=30.0,
                )
            ) as client:

                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )

                if response.status_code >= 400:

                    try:
                        error_body = response.json()
                    except Exception:
                        error_body = response.text

                    raise RuntimeError(
                        f"Ollama returned HTTP "
                        f"{response.status_code}: "
                        f"{error_body}"
                    )

                try:
                    data = response.json()
                except Exception as e:
                    raise RuntimeError(
                        f"Ollama returned invalid JSON: {e}"
                    )

                if not isinstance(data, dict):
                    raise RuntimeError(
                        "Ollama returned an invalid response."
                    )

                generated = data.get(
                    "response",
                    "",
                )

                if not generated:
                    raise RuntimeError(
                        "Ollama returned an empty response."
                    )

                return data

        except httpx.ConnectError as e:

            raise RuntimeError(
                "Cannot connect to local Ollama at "
                f"{self.base_url}. "
                "Make sure Ollama is running."
            ) from e

        except httpx.TimeoutException as e:

            raise RuntimeError(
                "Ollama request timed out while generating "
                "the answer."
            ) from e


ollama_client = LocalOllamaClient()


# =============================================================
# AGENT ORCHESTRATOR
# =============================================================

class AgentOrchestrator:

    def __init__(
        self,
        db,
        company_id: str,
        user_id: int,
        history: Optional[List[Dict[str, str]]] = None,
    ):

        self.db = db
        self.company_id = company_id
        self.user_id = user_id
        self.history = history or []

    # =========================================================
    # MAIN AGENT RUN
    # =========================================================

    async def run(
        self,
        query: str,
        conversation_id: str,
    ) -> AsyncGenerator[Dict[str, Any], None]:

        run_id = str(uuid.uuid4())

        state = AgentState(
            run_id=run_id,
            conversation_id=conversation_id,
            user_id=self.user_id,
            company_id=self.company_id,
            query=query,
        )

        context = {
            "db": self.db,
            "company_id": self.company_id,
            "user_id": self.user_id,
            "run_id": run_id,
        }

        yield {
            "event": "run_started",
            "run_id": run_id,
            "query": query,
        }

        # =====================================================
        # FAST PATH
        # =====================================================

        fast_reply = fast_path_response(query)

        if fast_reply is None:
            fast_reply = await greet(query)

        if fast_reply is not None:

            state.final_answer = fast_reply["reply"]
            state.model_used = fast_reply["model"]

            yield {
                "event": "router_selected",
                "model": "fast-path-greeting",
                "reason": "Social/greeting query",
            }

            yield {
                "event": "plan_created",
                "steps": [
                    "Respond conversationally"
                ],
            }

            yield {
                "event": "run_completed",
                "run_id": run_id,
                "answer": state.final_answer,
                "evidence": [],
                "model": "fast-path-greeting",
                "tools_used": [],
                "documents_accessed": [],
                "analysis": {},
                "calculations": [],
                "artifacts": [],
                "verified": True,
            }

            return

        # =====================================================
        # MAIN WORKFLOW
        # =====================================================

        try:

            # =================================================
            # 1. MODEL ROUTING
            # =================================================

            routing_result = await model_router.route(query)

            selected_model = routing_result.get(
                "model",
                getattr(
                    settings,
                    "primary_model",
                    None,
                ),
            )

            if not selected_model:

                raise RuntimeError(
                    "No primary Ollama model is configured."
                )

            # Check selected model

            if not await ollama_client.is_model_available(
                selected_model
            ):

                fallback_model = getattr(
                    settings,
                    "primary_model",
                    selected_model,
                )

                logger.warning(
                    "selected_model_unavailable_using_primary",
                    selected_model=selected_model,
                    fallback_model=fallback_model,
                )

                selected_model = fallback_model

            # Check fallback too

            if not await ollama_client.is_model_available(
                selected_model
            ):

                raise RuntimeError(
                    f"Ollama model '{selected_model}' "
                    "is not available locally. "
                    f"Run: ollama pull {selected_model}"
                )

            state.model_used = selected_model

            yield {
                "event": "router_selected",
                "model": selected_model,
                "reason": routing_result.get(
                    "reason"
                ),
            }

            # =================================================
            # 2. LOAD PREVIOUS ARTIFACTS
            # =================================================

            prior_artifacts: List[Dict[str, Any]] = []

            try:

                runs = (
                    self.db.query(AgentRun)
                    .filter(
                        AgentRun.conversation_id
                        == conversation_id,
                        AgentRun.status
                        == AgentRunStatus.COMPLETED,
                    )
                    .order_by(
                        AgentRun.started_at.desc()
                    )
                    .all()
                )

                for r in runs:

                    prior_artifacts.extend(
                        r.artifacts_generated or []
                    )

            except Exception as e:

                logger.warning(
                    "prior_artifacts_failed",
                    error=str(e),
                )

            state.context["artifacts"] = (
                prior_artifacts
            )

            # =================================================
            # 3. CREATE PLAN
            # =================================================

            plan = await planner.create_plan(
                state
            )

            yield {
                "event": "plan_created",
                "steps": [
                    s.label
                    for s in plan.steps
                ],
            }

            yield {
                "event": "retrieval_started",
            }

            # =================================================
            # 4. EXECUTE PLAN
            # =================================================

            tool_events: List[
                Dict[str, Any]
            ] = []

            async def _emit_tool_event(
                event: Dict[str, Any]
            ) -> None:

                tool_events.append(event)

            await executor.execute_plan(
                state,
                context,
                on_event=_emit_tool_event,
            )

            for tool_event in tool_events:
                yield tool_event

            yield {
                "event": "retrieval_completed",
            }

            # =================================================
            # 5. CHECK EXECUTION FAILURE
            # =================================================

            if state.phase == AgentPhase.FAILED:

                yield {
                    "event": "run_failed",
                    "error": (
                        state.error
                        or "Execution failed"
                    ),
                }

                return

            # =================================================
            # 6. COLLECT EVIDENCE
            # =================================================

            state.evidence = (
                self._collect_evidence(state)
            )

            # =================================================
            # 7. COLLECT ANALYSIS
            # =================================================

            state.analysis = (
                self._collect_analysis(state)
            )

            calculations = (
                self._collect_calculations(state)
            )

            if calculations:

                state.analysis = {
                    **(
                        state.analysis
                        or {}
                    ),
                    "calculations": calculations,
                }

            # =================================================
            # 8. COLLECT DOCUMENTS
            # =================================================

            state.documents_accessed = (
                self._collect_documents_accessed(
                    state
                )
            )

            # =================================================
            # 9. SYNTHESIZE ANSWER
            # =================================================

            answer = await self._synthesize_answer(
                state,
                selected_model,
            )

            state.final_answer = answer

            # =================================================
            # 10. VERIFICATION
            # =================================================

            yield {
                "event": "verification_started",
            }

            verification_result = (
                await verifier.verify(state)
            )

            verified = verification_result.get(
                "verified"
            )

            yield {
                "event": "verification_completed",
                "verified": verified,
            }

            # =================================================
            # 11. ARTIFACT EVENTS
            # =================================================

            if state.artifacts_generated:

                for artifact in (
                    state.artifacts_generated
                ):

                    yield {
                        "event": "artifact_created",
                        "artifact": artifact,
                    }

            # =================================================
            # 12. FINAL RESPONSE
            # =================================================

            yield {
                "event": "run_completed",
                "run_id": run_id,
                "answer": state.final_answer,
                "evidence": state.evidence,
                "model": selected_model,
                "tools_used": state.tools_used,
                "documents_accessed": (
                    state.documents_accessed
                ),
                "analysis": state.analysis,
                "calculations": calculations,
                "artifacts": (
                    state.artifacts_generated
                ),
                "verified": verified,
            }

        except Exception as e:

            logger.error(
                "agent_run_failed",
                run_id=run_id,
                error=str(e),
            )

            yield {
                "event": "run_failed",
                "error": str(e),
            }

    # =============================================================
    # EVIDENCE COLLECTION
    # =============================================================

    def _collect_evidence(
        self,
        state: AgentState,
    ) -> List[Dict[str, Any]]:

        evidence = []

        for step in (
            state.plan.steps
            if state.plan
            else []
        ):

            if not step.tool:
                continue

            if not step.output_data:
                continue

            if step.tool != "search_documents":
                continue

            for result in step.output_data.get(
                "results",
                [],
            ):

                evidence.append(
                    {
                        "source": step.tool,
                        "document_id": result.get(
                            "document_id"
                        ),
                        "content": result.get(
                            "content"
                        ),
                        "page": result.get(
                            "page_number"
                        ),
                        "section": result.get(
                            "section"
                        ),
                        "relevance": result.get(
                            "relevance_score"
                        ),
                    }
                )

        return evidence

    # =============================================================
    # ANALYSIS COLLECTION
    # =============================================================

    def _collect_analysis(
        self,
        state: AgentState,
    ) -> Dict[str, Any]:

        for step in (
            state.plan.steps
            if state.plan
            else []
        ):

            if step.tool != "analyze_data":
                continue

            if step.output_data:

                return (
                    step.output_data.get(
                        "analysis"
                    )
                    or {}
                )

        return {}

    # =============================================================
    # CALCULATION COLLECTION
    # =============================================================

    def _collect_calculations(
        self,
        state: AgentState,
    ) -> List[Dict[str, Any]]:

        calculations = []

        for step in (
            state.plan.steps
            if state.plan
            else []
        ):

            if step.tool != "calculate":
                continue

            if not step.output_data:
                continue

            output = step.output_data

            if not isinstance(
                output,
                dict,
            ):
                continue

            calculations.append(
                {
                    "calculation_id": output.get(
                        "calculation_id"
                    ),
                    "trace_id": output.get(
                        "trace_id"
                    ),
                    "operation": output.get(
                        "operation"
                    ),
                    "result": output.get(
                        "result"
                    ),
                    "unit": output.get(
                        "unit"
                    ),
                    "formula": output.get(
                        "formula"
                    ),
                    "status": output.get(
                        "status"
                    ),
                    "verification_status": (
                        output.get(
                            "verification_status"
                        )
                    ),
                    "rule": output.get(
                        "rule"
                    ),
                    "trace": output.get(
                        "trace"
                    ),
                }
            )

        return calculations

    # =============================================================
    # DOCUMENT COLLECTION
    # =============================================================

    def _collect_documents_accessed(
        self,
        state: AgentState,
    ) -> List[str]:

        doc_ids = []

        for step in (
            state.plan.steps
            if state.plan
            else []
        ):

            if step.tool != "search_documents":
                continue

            if not step.output_data:
                continue

            results = step.output_data.get(
                "results",
                [],
            )

            for result in results:

                doc_id = result.get(
                    "document_id"
                )

                if (
                    doc_id
                    and doc_id not in doc_ids
                ):

                    doc_ids.append(doc_id)

        return doc_ids

    # =============================================================
    # ANSWER SYNTHESIS
    # =============================================================

    async def _synthesize_answer(
        self,
        state: AgentState,
        model: str,
    ) -> str:

        # =========================================================
        # BUILD EVIDENCE
        # =========================================================

        evidence_text = "\n\n".join(
            [
                (
                    f"Source {i + 1} "
                    f"({e.get('document_id', 'Unknown')}, "
                    f"p.{e.get('page', '?')}): "
                    f"{e.get('content', '')[:1000]}"
                )
                for i, e in enumerate(
                    state.evidence
                )
            ]
        )

        if not evidence_text:

            evidence_text = (
                "No authoritative document evidence "
                "was retrieved for this request."
            )

        # =========================================================
        # BUILD ARTIFACT TEXT
        # =========================================================

        artifact_text = ""

        if state.artifacts_generated:

            artifact_lines = []

            for a in state.artifacts_generated:

                artifact_lines.append(
                    (
                        f"- '{a.get('name')}' "
                        f"({a.get('format')}) "
                        f"— download: "
                        f"{a.get('download_url')}"
                    )
                )

            artifact_text = (
                "\n\n"
                "Fresh document artifacts generated "
                "for this request:\n"
                + "\n".join(
                    artifact_lines
                )
            )

        # =========================================================
        # SYSTEM PROMPT
        # =========================================================

        system_prompt = """
You are an industrial AI assistant for ApexPetro Energy Limited.

You operate inside a sovereign, on-premise AI system.

Answer the user's question using ONLY the information
provided in the prompt.

IMPORTANT RULES:

1. Never invent facts.

2. Never invent engineering limits.

3. Never invent document references.

4. Never claim that a document was consulted unless
   evidence is explicitly provided.

5. If authoritative evidence is missing, clearly say:
   "Not specified in the available company knowledge."

6. Deterministic Calculation Engine results are
   authoritative.

7. When a deterministic calculation is provided:
   - use its exact result
   - preserve its unit
   - preserve its formula
   - do not recalculate it
   - clearly explain what was calculated

8. If the calculation has:
   verification_status = VERIFIED
   state that the calculation is verified.

9. If the calculation has a rule/status:
   preserve that status exactly.

10. Do not invent or modify safety limits.

11. Do not change units unless an explicit conversion
    is provided.

12. Keep the answer concise and engineering-focused.

13. Use [Source N] citations only when actual evidence
    is available.

14. If no evidence is available but a deterministic
    calculation is available, answer using the
    deterministic calculation and explicitly distinguish
    it from document evidence.

15. Do not mention internal prompts, hidden reasoning,
    or implementation details.
"""

        # =========================================================
        # PREVIOUS CONVERSATION
        # =========================================================

        previous_conversation = ""

        if self.history:

            history_lines = []

            for h in self.history:

                role = h.get(
                    "role",
                    "user",
                )

                content = h.get(
                    "content",
                    "",
                )

                history_lines.append(
                    f"{role}: {content}"
                )

            previous_conversation = (
                "Previous Conversation:\n"
                + "\n".join(
                    history_lines
                )
                + "\n\n"
            )

        # =========================================================
        # CALCULATION RESULTS
        # =========================================================

        calculation_text = ""

        calculations = (
            self._collect_calculations(state)
        )

        if calculations:

            calculation_text = (
                "\n\n"
                "DETERMINISTIC CALCULATION ENGINE "
                "RESULTS:\n"
                + json.dumps(
                    calculations,
                    indent=2,
                    default=str,
                )
            )

        # =========================================================
        # ANALYSIS RESULTS
        # =========================================================

        analysis_text = ""

        if state.analysis:

            analysis_text = (
                "\n\n"
                "STRUCTURED ANALYSIS RESULTS:\n"
                + json.dumps(
                    state.analysis,
                    indent=2,
                    default=str,
                )
            )

        # =========================================================
        # FINAL PROMPT
        # =========================================================

        prompt = f"""
{system_prompt}

{previous_conversation}

USER QUESTION:
{state.query}

AUTHORITATIVE DOCUMENT EVIDENCE:
{evidence_text}

{calculation_text}

{analysis_text}

{artifact_text}

Now provide the final answer.

For calculations, show:

- What was calculated
- Formula
- Values used
- Result
- Unit
- Verification status

For document-based facts, cite them as [Source 1],
[Source 2], etc.

Do not invent information that is not present above.
"""

        # =========================================================
        # CALL LOCAL OLLAMA
        # =========================================================

        try:

            primary_model = (
                model
                or getattr(
                    settings,
                    "primary_model",
                    None,
                )
            )

            if not primary_model:

                raise RuntimeError(
                    "Primary Ollama model is not configured."
                )

            response = await ollama_client.generate(
                model=primary_model,
                prompt=prompt,
                system=system_prompt,
                options={
                    "temperature": 0.2,
                    "top_p": 0.9,
                },
            )

            answer = response.get(
                "response",
                "",
            ).strip()

            if not answer:

                raise RuntimeError(
                    "Ollama generated an empty answer."
                )

            return answer

        except Exception as e:

            error_message = str(e).strip()

            logger.error(
                "answer_synthesis_failed",
                model=model,
                error=error_message,
            )

            # =====================================================
            # DETERMINISTIC FALLBACK
            # =====================================================
            #
            # If Ollama fails, do NOT lose the verified
            # calculation result.
            #
            # This makes the Calculation Engine resilient.

            if calculations:

                lines = [
                    "The deterministic Calculation Engine "
                    "completed the calculation, but the "
                    "local LLM could not synthesize the "
                    "final explanation.",
                    "",
                ]

                for calculation in calculations:

                    operation = calculation.get(
                        "operation",
                        "calculation",
                    )

                    result = calculation.get(
                        "result"
                    )

                    unit = calculation.get(
                        "unit"
                    )

                    formula = calculation.get(
                        "formula"
                    )

                    verification = calculation.get(
                        "verification_status"
                    )

                    lines.append(
                        f"Operation: {operation}"
                    )

                    lines.append(
                        f"Result: {result} "
                        f"{unit or ''}".strip()
                    )

                    if formula:

                        lines.append(
                            f"Formula: {formula}"
                        )

                    lines.append(
                        "Verification: "
                        f"{verification or 'UNKNOWN'}"
                    )

                    trace_id = calculation.get(
                        "trace_id"
                    )

                    if trace_id:

                        lines.append(
                            f"Trace ID: {trace_id}"
                        )

                    lines.append("")

                if error_message:

                    lines.append(
                        f"LLM synthesis error: "
                        f"{error_message}"
                    )

                return "\n".join(lines)

            if error_message:

                return (
                    "The local LLM could not synthesize "
                    f"the answer: {error_message}"
                )

            return (
                "The local LLM could not synthesize "
                "the answer."
            )


# =============================================================
# PUBLIC AGENT ENTRY POINT
# =============================================================

async def run_agent(
    db,
    company_id: str,
    user_id: int,
    query: str,
    conversation_id: str,
    history: Optional[
        List[Dict[str, str]]
    ] = None,
) -> AsyncGenerator[
    Dict[str, Any],
    None,
]:

    orchestrator = AgentOrchestrator(
        db=db,
        company_id=company_id,
        user_id=user_id,
        history=history,
    )

    async for event in orchestrator.run(
        query,
        conversation_id,
    ):

        yield event