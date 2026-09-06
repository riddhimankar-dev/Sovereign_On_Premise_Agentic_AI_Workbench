# Sovereign AI Workbench — Implementation Plan

> Phase 0 deliverable. Read this before changing code. Updated as phases complete.

## 1. Current Architecture (audit result)

```
React 19 / Vite / TS / Tailwind v4 (frontend, port 8443)
        │  fetch (HTTP / SSE)
        ▼
FastAPI backend (port 8000)  ──►  Ollama (11434): qwen2.5:7b, qwen2.5-coder:7b, qwen2.5:3b, bge-m3:latest
        │
        ├─► Qdrant (6333)  collection=apexpetro_knowledge (1024-dim, COSINE)
        └─► SQLite (data/runtime/workbench.db)
```

Backend structure already largely mirrors the target:
`app/{main,agents,api,core,db,llm,rag,services,tools}`.

### What already works (real backend, verified)
- Auth: login/signup/JWT, `/auth/me` decodes token (fixed this session).
- Chat persistence: conversations + messages, `/chat/conversations`, `/chat/stream` (SSE).
- Agent orchestrator emits `run_started, router_selected, plan_created, retrieval_started, retrieval_completed, verification_started, verification_completed, run_completed, run_failed`.
- RAG: BGE-M3 embeddings → Qdrant, HybridRetriever (semantic+keyword), metadata filters. 250 chunks indexed, 56 documents.
- Model registry (4 local models), models API.
- Documents: list/get/delete; upload route is BROKEN (see below).
- Document generation route exists (`/documents/generate`, DOCX/XLSX/PPTX/PDF).
- Artifacts/Approvals/Tasks/Projects/WorkOrders/Security routes exist.
- Code executor tool exists (subprocess) but network NOT blocked.

### Current UI (frontend)
- State-based routing in `App.tsx`, session restored from `localStorage.sovereign_token`.
- Screens: Login, Chat, Projects, ProjectDetail(*mock*), Files, Knowledge, Tasks, Artifacts, Approvals, Models, Security, DocumentViewer(*mock*), Profile(*mock*), ErrorState(*mock*).
- `api.ts` services exist for all domains, BUT **auth token is never attached** to requests (critical).
- ChatScreen is real SSE. Approvals/Artifacts/etc. read real APIs but are display-only.

## 2. Broken / Static Areas (must fix)

| Area | Problem | Fix priority |
|---|---|---|
| Frontend `api.ts` | No `Authorization` header sent | CRITICAL |
| `documents.py` upload | Calls non-existent `chunk_document/get_embeddings/parse_document(fp,type)` → runtime error | CRITICAL |
| `POST /api/chat` | Non-streaming stub returns empty | HIGH |
| Orchestrator | Never emits `tool_started`/`tool_completed`; always uses `primary_model` for synthesis | HIGH |
| Planner/Verifier | Fallback/stub (LLM prompts unused) | MEDIUM |
| Document generation | Route exists but not wired to chat/intent; templates unused | HIGH |
| Sandbox | subprocess only, network not blocked | MEDIUM |
| Data analysis | No module (Feature K) | HIGH |
| Chart schema | No structured chart data in response | HIGH |
| Frontend `sovereign_model` | Saved but never applied to chat | MEDIUM |
| Approvals UI | No approve/reject wiring (backend methods exist) | MEDIUM |
| Sidebar GPU/Profile/ProjectDetail/DocumentViewer | Hard-coded RTX A5000 / mock data | MEDIUM |
| `conversation_id`/auth | user_id hard-coded to 1 in many routes | MEDIUM |

## 3. Target Requirements Ladder (as implemented)

The full spec is 99 sections. This plan tracks progress against them via
`IMPLEMENTATION_STATUS.md`. We implement incrementally, highest real-value first,
preserving the existing UI.

## 4. API Plan (existing + additions)

Existing are listed in §4/§69 of master prompt. Additions needed:
- `GET /api/chat/conversations/{id}` (already), `PATCH/DELETE` conversations (rename/delete)
- `POST /api/chats/{id}/attachments` (chat-scoped file)
- `POST /api/files/{id}/reindex`
- `GET /api/artifacts/{id}/download` (exists)
- `POST /api/approvals/{id}/request-changes` (add)
- `GET /api/audit`
- `GET /api/system/health`, `GET /api/system/security`
- Structured response envelope incl. `charts`, `findings`, `metrics`, `recommendations`

## 5. Database Plan

Largely complete (see §4 audit). Add columns/entities needed:
- `Attachment` (chat attachments) — scope chat_id
- `Artifact.parent_artifact_id`, `version`, `change_summary` (versioning)
- `AuditEvent` (exists)
- `Approval.task_id`, `chat_id` linking (sync w/ chat)
- Index on company_id across objects.

## 6. Agent / Tool / RAG / Artifact / Approval Plan

Per master prompt §8, 12, 58, 26-32. Implement tool registry (exists), add missing tools:
`read_image, analyze_image, ocr_document, read_spreadsheet, analyze_data, compare_documents,
find_conflicts, generate_docx/xlsx/pptx/pdf`. Wire routing by capability via model registry.

## 7. Migration Plan

Backward compatible. We do NOT rewrite the UI. We add auth header to `api.ts`, fix
broken routes, add new endpoints, and progressively replace the worst mock screens.

## 8. Test Plan

- Backend: pytest in `backend/tests/` (currently empty) — unit + integration for auth,
  chat, RAG, documents, document-gen, approvals, sandbox, offline verification.
- Frontend: `npm run build` + `npx tsc --noEmit`.
- Live E2E: curl-driven against running servers (as done for signup→dashboard).

## 9. Risks

- PaddleOCR heavy; scanned-PDF OCR may be slow/absent on CPU.
- Sandbox: real network isolation requires container; provide best-effort firewall-based
  subprocess sandbox on this machine.
- Charting: no chart lib installed; add small dependency-free SVG chart component.
- Full 17-phase build is large; prioritized by real-user value.

## 10. Implementation Order (this run)

1. Frontend `api.ts`: attach auth token (CRITICAL).
2. Fix `documents.py` upload pipeline (CRITICAL).
3. Fix `POST /api/chat` stub + orchestrator tool events.
4. Data analysis module + chart schema (Feature K/J).
5. Wire document generation → chat intent + artifacts + download (Feature M/13/26/27).
6. Approvals lifecycle + chat sync + UI wiring (Feature N/29-32).
7. Sandbox network blocking + coding agent (Feature L/19/20).
8. RAG hybrid retrieval polish + chat-scoped attachments (Feature S/8).
9. Progressive mock replacement (Profile, ProjectDetail, DocumentViewer, GPU).
10. verify_offline.py + security page honest status (Feature 50/49).
11. Tests + `IMPLEMENTATION_STATUS.md` update (Feature 64/65).
