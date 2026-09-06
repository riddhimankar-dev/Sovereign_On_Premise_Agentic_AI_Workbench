# Sovereign AI Workbench — Implementation Status

> Live ledger. Updated after each phase. Honest labels only:
> `IMPLEMENTED` / `PARTIALLY IMPLEMENTED` / `NOT IMPLEMENTED` / `KNOWN LIMITATION`.

## Phase Map

| Phase | Area | Status |
|---|---|---|
| 0 | Repository audit | IMPLEMENTED |
| 1 | Backend foundation + DB | PARTIALLY IMPLEMENTED |
| 2 | Ollama model registry + capability routing | PARTIALLY IMPLEMENTED |
| 3 | File storage + document ingestion + classification | PARTIALLY IMPLEMENTED |
| 4 | OCR + multimodal extraction | PARTIALLY IMPLEMENTED |
| 5 | BGE-M3 + Qdrant RAG (hybrid) | IMPLEMENTED |
| 6 | Chat persistence + chat API | IMPLEMENTED |
| 7 | Fast path greetings/general queries | IMPLEMENTED (deterministic + LLM greeting fast path) |
| 8 | Agent router + planner + tools | PARTIALLY IMPLEMENTED |
| 9 | Data analysis + chart schema | PARTIALLY IMPLEMENTED (backend IMPLEMENTED, chart not persisted) |
| 10 | Coding agent + sandbox | IMPLEMENTED (coding_agent tool + /code/run + working UI) |
| 11 | Document generation + versioning | IMPLEMENTED (docx/xlsx/pptx/pdf via planner tool; versioning deferred to ph.13) |
| 12 | Approvals + lifecycle | IMPLEMENTED (chat-created approvals, auth, audit, working UI) |
| 13 | Artifacts + versions + download | IMPLEMENTED |
| 14 | Projects + tasks | PARTIALLY IMPLEMENTED |
| 15 | Frontend API integration (services/mock replacement) | IMPLEMENTED (Profile/ProjectDetail/DocumentViewer real API data; GPU claims corrected) |
| 16 | Security / offline verification | IMPLEMENTED (runnable `verify_offline.py`; honest egress result) |
| 17 | Full E2E + docs | IMPLEMENTED (78 tests pass; full E2E verified) |
| 18 | All-format exports + artifact versioning + chat file upload | IMPLEMENTED |

## Detailed Item Status

### Critical / High-priority items
- [x] Frontend `api.ts` attaches `Authorization: Bearer <token>` to every request
- [x] `POST /api/documents/upload` uses real pipeline (chunk/embed/index) without error
- [x] `POST /api/chat` non-streaming returns structured result
- [x] Orchestrator emits `tool_started`/`tool_completed` events; run_completed carries `documents_accessed` + `analysis`
- [x] Structured response envelope: `findings, metrics, charts, tables, recommendations`
- [x] Data-analysis module (`app/services/analysis_service.py` + `analyze_data` tool, local LLM + live DB facts)
- [x] Chart data schema → frontend renders charts (`components/AnalysisView.tsx`, dependency-free SVG)
- [x] Document generation wired to chat "create" intent: planner routes to `generate_document` tool, fills template sections from RAG evidence (local LLM + deterministic fallback), renders DOCX/XLSX/PPTX/PDF, persists Artifact row + file, streams `artifact_created` + `run_completed.artifacts`, downloadable via `/api/artifacts/{id}/download`, shown in chat as a generated-documents card
- [x] `documents/generate` REST route delegates to shared renderer (`app/services/file_document_generator.py`); no duplicate generators
- [x] `/api/artifacts` list fixed (datetime serialization) — previously 500 on any artifact row
- [x] Approvals full lifecycle: every chat-generated document creates a PENDING `Approval` (approval_id emitted in `run_completed.artifacts`); `GET/POST /api/approvals`, approve/reject use the authenticated user (`reviewed_by` = real reviewer id, 409 on non-pending); `requested_by_name`/`reviewed_by_name`/artifact summary in responses; AuditEvent rows written on approve/reject; UI has working Approve/Reject buttons with comment + linked-artifact download
- [x] Coding sandbox: planner routes code-intent queries to `coding_agent` tool (LLM emits a single stdlib Python script, executed by the hardened `CodeExecutorTool` in `python -I` with temp-dir cwd, per-process CPU/fs/file-descriptor rlimits, no injected network env); `/api/code/run` executes ad-hoc scripts (auth-required, timeout 1–60s, 422 on failure, writes `code.run` AuditEvent); UI Code Sandbox now triggers a real backend execution and renders stdout/exit/sandbox note
- [x] Global `WorkbenchException` handler added — unauthenticated/invalid-token requests on protected routes now return proper 401/403 instead of 500 (was also raw 500 on `/api/approvals`, `/api/code/run`, etc.)
- [x] Greeting fast path (`app/agents/greetings.py`): social/greeting/chitchat/thanks queries bypass the agent pipeline entirely (no router/tool/RAG/verifier); deterministic replies for common greetings, LLM-generated warm reply otherwise; subject hints (assets, documents, "what is", "create", etc.) correctly fall through to the full agent
- [x] Mock replacement in UI: ProfileScreen loads the real user (`/api/auth/me`: name/email/role) with role-derived permissions; ProjectDetailScreen receives the selected Project and loads real documents, tasks (project_id), artifacts, and approvals; DocumentViewerScreen renders the real selected document's metadata instead of a fabricated P-102 report; Sidebar/Profile/Security GPU claims corrected from fabricated "RTX A5000 / 24 GB" to the real "RTX 4050 / 6 GB"
- [x] Offline verification script (`backend/scripts/verify_offline.py`) runnable and accurate: fixes so it executes from any cwd (adds project root to `sys.path`); Qdrant health now uses `/livez` (was `/health` which returns 404); port scan parses `ss -tuln` columns correctly, treats only the local AI stack (uvicorn :8000, Vite :8443, Qdrant :6333/6334, Ollama :11434) as legitimate and ignores loopback system services; adds an active external-egress probe (`https://api.openai.com`, `anthropic.com`, `google.com`). Result honestly reports: (a) all local-services/AI-config/AI-code-path checks PASS, (b) the operator's workstation has general internet (egress probe reachable), i.e. the AI backend is local but the machine is not a fully air-gapped host — documented as a known limitation, not hidden
- [x] Tests added and passing: 39 pytest tests (`backend/tests/`) — unit tests for greetings classification/fast-path, planner intent routing (create-vs-code-vs-analysis-vs-search), coding-agent code-fence parsing, and the hardened code executor (run/timeout/stderr/empty/files); e2e smoke tests against the running backend (auth 401 guard, `/api/auth/me` seed user, `/api/code/run` live execution + anon rejection, offline-script smoke)
- [x] Security page accuracy fixed: `/api/security/status` Qdrant check now uses `/livez` and the DB check uses SQLAlchemy `text("SELECT 1")` — overall now correctly reports `secure` (was `degraded` due to two false-failing checks)
- [x] Document exports in 8 formats: `render_document` now emits DOCX/XLSX/PPTX/PDF/TXT/JSON/MD/CSV and template coverage expanded (approval_note/technical_review/inspection_report → all 8; risk_assessment → xlsx/csv/json/md/txt; management_summary → pptx/pdf/docx/md/txt/json). CSV fallback writes a `Field,Value` header; download endpoints add `text/csv`, `text/plain`, `text/markdown`, `application/json` media types. Planner detects format phrases ("in a sheet/make a ppt/as a pdf/in excel…") via expanded keyword sets + regex.
- [x] Follow-up artifact editing with versioning: new `update_artifact` tool (writes `version+1`, sets `parent_artifact_id`, falls back to the original artifact_id so v1 stays stable), new `convert_artifact` tool (new artifact in target format linked via `parent_artifact_id`); planner resolves the latest artifact from the conversation (`state.context["artifacts"]` seeded from prior COMPLETED runs, most recent first) and routes "expand/update <doc>" / "convert/turn <doc> into <fmt>" intents. Extracted content round-trips across formats via `extract_document_data` (docx sections, xlsx sheets, pptx slides, csv/md/json/txt, pdf text) so conversions preserve the original report body (verified docx→pdf keeps all sections).
- [x] Chat file upload: `POST /api/chat/attachments` accepts txt/csv/json/md/xlsx/docx/pptx (python-* extraction), images (pytesseract OCR), and pdf (pypdf); extracted text is indexed in-memory per conversation (`chat_attachment_service`, cap 20, chat-scoped, not added to permanent RAG by design) and appended to the run query as attachment context. Verified E2E: upload `vib.csv` then ask "highest reading for P-102 from my uploaded file" → answer 7.5 mm/s sourced from the file. Frontend Composer has attach button, per-file status chips (uploading/ready/error), remove, and auto-creates the conversation on first attach.
- [x] Artifacts screen overhaul: PreviewModal fetches `/api/artifacts/{id}/preview` (inline JSON/text for json/csv/txt/md, raw PDF, office text summaries), real download links, date-created grouping (Today/Yesterday/weekday/date), format/status tabs, and a `v{version}` badge with parent-artifact links; ArtifactResponse now exposes `version`, `parent_artifact_id`, `preview_url`.
- [x] Tests expanded: 78 pytest tests — `test_file_formats.py` (8 formats render, txt/json/md/csv content, extract round-trip), `test_doc_tools_and_attachments.py` (tool registration, chat attachment parsing txt/json/csv, chat-scoped isolation), planner follow-up-edit routing (update vs convert vs create), e2e ArtifactsAPI (version/preview fields, preview + download endpoints) and ChatAttachmentAPI (upload parses txt).
- [x] Full chat persistence (4-point requirement): per-message `sources` (citation/evidence), `artifacts` (generated-document download links), and `meta` (model / verified / analysis) persisted on the `messages` row and serialized by `GET /api/chat/conversations/{id}/messages` — sources and download links survive follow-up questions and close/reopen from History. Auto-title on the first message (`generate_title`, deterministic, no LLM call; verified: "Explain how our company's leave policy works" → "Company Leave Policy", "Create a report on Q3 sales performance" → "Q3 Sales Performance Report"); backfilled all 45 pre-existing conversations from their first user message. `PATCH /api/chat/conversations/{id}` renames (400 on empty), `DELETE /api/chat/conversations/{id}` deletes the conversation + cascade-messages + its agent runs (404 on repeat). Frontend: per-message collapsible `Sources (N) ▼` panel (default collapsed) with relevance bars + evidence drawer, per-message document cards with working download links (via `api.artifacts.downloadUrl`), History sidebar rename (inline input, Enter/save/blur) and delete (confirmation modal). Chat uploads remain chat-scoped but are now rebuildable after a backend restart from persisted message attachment metadata (`build_attachment_context` re-reads them).

## Final E2E verification (single pass, all local)
- Greeting fast-path: `hello` → model `fast-path-greeting`, no tools, warm reply
- Code sandbox: `/api/code/run` `print(sum(range(1,101)))` → `5050`, return 0, ~28 ms, sandbox note
- Document generation + approval sync: "Create a risk assessment document…" → XLSX artifact + PENDING approval (`APR-…`); approve as seed user → APPROVED, reviewer + reviewed_at set
- Security status → overall `secure`; local inference/storage/audit all ACTIVE
- Frontend: `tsc --noEmit` clean
- All-format exports: 8 formats render in 0.5 s (docx/xlsx/pptx/pdf/txt/json/md/csv); every chat-created doc appears in Artifacts with download + preview
- Version chain: "Create an inspection report…" → v1 DOCX → "Update … add a risk mitigation section" → v2 DOCX (`parent_artifact_id` = v1) → "Convert the approval note to pdf" → PDF linked to its source; converted PDF verified to contain the full report body (`pdftotext`)
- Chat upload: attach `vib.csv` → "highest vibration reading from my uploaded file" → `7.5 mm/s on 2026-08-20`
- Full suite: 92 passed (80 unit / 12 e2e) in ~5 s; frontend `tsc --noEmit` clean
- Chat persistence E2E (Tests 1–4, API-verified via live backend): (1) "Explain how our company's leave policy works" → run_completed evidence=5, assistant message row persisted `sources`[5], survives GET messages (close/reopen); (2) artifacts/download links round-trip through the messages endpoint (seeded `ART-REOPEN` download_url returned verbatim after reopen); (3) auto-title "Company Leave Policy" on first message, `PATCH` rename → "HR Leave Policy Deep Dive" round-trips, empty-title rejected 400; (4) `DELETE` removes conversation + cascade messages + agent runs (repeat → 404). Full generated-doc link persistence is additionally locked by repo round-trip + messages-serializer e2e tests; live doc routing depends on the 3b Ollama model following the plan (it sometimes answers from search without calling the document tool — unchanged pre-existing model routing).

### Known limitations (on this machine)
- PaddleOCR scanned-PDF OCR is CPU-only and slow; may be skipped on large scans.
- True containerized sandbox not guaranteed; network blocking is best-effort (firewall cgroup),
  documented rather than faked on Security page. Executed Python runs with `-I` (isolated mode),
  per-process CPU/fs/fd rlimits, temp-dir cwd, and no network env on the subprocess, but a malicious
  same-OS process is not a hard VM boundary.
- Only 6 GB VRAM / RTX 4050 → vision (VL) models not run; image analysis = OCR + local heuristics.
- `TEST_DATA_REMOVE_LATER` folder empty in this dataset copy → test data authoring deferred.
- Chat uploads are conversational and chat-scoped: files persist on disk under `backend/chat_uploads/` and per-file metadata is written onto the user message row, so uploaded-file context is rebuilt from the DB after a backend restart (in-memory index + message-metadata fallback). Deliberately not indexed into the permanent RAG/knowledge base.
- Artifact status shown in the API remains the lifecycle string; the UI groups tabs by format and creation date.
