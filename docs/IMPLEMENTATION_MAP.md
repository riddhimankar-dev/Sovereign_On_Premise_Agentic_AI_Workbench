# Implementation Map — Sovereign AI Workbench

## Repository Overview

```
Smart India Hackathon/
├── Replicate Existing Design/          # React/TypeScript Frontend
│   ├── src/
│   │   ├── App.tsx                     # Main app with routing
│   │   ├── main.tsx                    # Entry point
│   │   ├── index.css                   # Tailwind v4 + theme
│   │   ├── components/
│   │   │   ├── CommandPalette.tsx
│   │   │   ├── ModelDrawer.tsx
│   │   │   ├── RightPanel.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── TopBar.tsx
│   │   └── screens/
│   │       ├── LoginScreen.tsx
│   │       ├── ChatScreen.tsx          # Main chat with agent UI
│   │       ├── ProjectsScreen.tsx
│   │       ├── ProjectDetailScreen.tsx
│   │       ├── TasksScreen.tsx
│   │       ├── ArtifactsScreen.tsx
│   │       ├── ApprovalsScreen.tsx
│   │       ├── KnowledgeScreen.tsx
│   │       ├── ModelsScreen.tsx
│   │       ├── SecurityScreen.tsx
│   │       ├── FilesScreen.tsx
│   │       ├── DocumentViewerScreen.tsx
│   │       ├── ProfileScreen.tsx
│   │       └── ErrorStateScreen.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── ApexPetro_Sovereign_Dataset_v3/     # Company knowledge base
│   ├── company.json
│   ├── specs/apexpetro_master.yaml     # Full company spec (assets, units, etc.)
│   ├── metadata/
│   │   ├── document_registry.json      # 53 documents with metadata
│   │   ├── company_master.json
│   │   ├── knowledge_base_schema.json
│   │   ├── data_lineage.json
│   │   └── validation_report.json
│   ├── assets/, sops/, manuals/, etc.  # PDF/DOCX/XLSX files
│   └── TEST_DATA_REMOVE_LATER/         # Evaluation data (excluded from prod)
├── SOVEREIGN_AI_MASTER_BACKEND_BUILD_PROMPT.md
└── backend/                            # To be created
```

## Frontend Analysis

### Existing Screens & Mock Data

| Screen | Mock Data | Backend Integration Needed |
|--------|-----------|---------------------------|
| **ChatScreen** | Hardcoded P-102 analysis, agent steps, sources, artifacts | `/api/chat` (SSE), `/api/models`, agent runtime, tools |
| **ModelsScreen** | Fake models (Qwen 32B, Vision, DeepSeek) | `/api/models` → real Ollama models |
| **FilesScreen** | 7 hardcoded files | `/api/documents` (CRUD, upload, status) |
| **KnowledgeScreen** | 6 hardcoded search results | `/api/knowledge/search` (hybrid retrieval) |
| **ProjectsScreen** | 4 hardcoded projects | `/api/projects` (list, detail) |
| **ProjectDetailScreen** | Mock project detail | `/api/projects/{id}` |
| **TasksScreen** | Mock tasks | `/api/tasks` |
| **ArtifactsScreen** | 4 hardcoded artifacts | `/api/artifacts` (list, download, preview) |
| **ApprovalsScreen** | Mock approvals | `/api/approvals` (list, approve/reject) |
| **SecurityScreen** | Hardcoded security status | `/api/security/status` (real verification) |
| **FilesScreen** | Upload UI | `/api/documents/upload` (ingestion pipeline) |
| **DocumentViewerScreen** | Mock viewer | `/api/documents/{id}/content` |

### Frontend API Layer Needed
```
src/services/
├── api.ts              # Base HTTP client
├── chatApi.ts          # Chat, streaming, agent events
├── documentApi.ts      # Upload, list, download, status
├── knowledgeApi.ts     # Search, retrieval
├── modelApi.ts         # Model list, status
├── projectApi.ts       # Projects, tasks
├── artifactApi.ts      # Artifacts, approvals
├── approvalApi.ts      # Approve/reject
└── securityApi.ts      # Security status, audit

src/types/
├── chat.ts
├── document.ts
├── asset.ts
├── model.ts
├── agent.ts
├── artifact.ts
├── approval.ts
└── audit.ts
```

## Dataset Analysis

### Company Structure (from apexpetro_master.yaml)
- **Company**: ApexPetro Energy Limited (apexpetro)
- **Departments**: 12 (Operations, Maintenance, Inspection & Integrity, etc.)
- **Facilities**: 3 (JRC, MUM-HQ, DEL-LIAISON)
- **Units**: 11 (CDU-1 to CDU-4, HCU-1, HDS-1, UTIL-1, TF-1, TF-2, DISP-1)
- **Assets**: 34 assets with full specs (pumps, vessels, exchangers, tanks, heaters, compressors, motors, instruments, valves)

### Key Asset: P-102 (Centrifugal Process Pump)
- Unit: CDU-4, Criticality: HIGH
- Design pressure: 50 bar, Approved max: 40 bar, Normal: 35 bar
- PSV set: 47.5 bar
- History: 2024 (34 bar), 2025 (37 bar), 2026 (42 bar) - **EXCEEDS LIMIT**

### Document Registry (53 documents)
- Types: PDF, XLSX, DOCX
- Classifications: CONFIDENTIAL, INTERNAL
- Status: ACTIVE
- Categories: Policies, SOPs, Manuals, Asset Records, Inspections, Maintenance, Incidents, Vendor, Projects, Operations, Procurement, Instrumentation, Quality

### Excluded from Production
- `TEST_DATA_REMOVE_LATER/` - evaluation only

## Backend Architecture (Target)

```
backend/
├── app/
│   ├── main.py                      # FastAPI app
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py
│   │   │   ├── chat.py
│   │   │   ├── documents.py
│   │   │   ├── knowledge.py
│   │   │   ├── assets.py
│   │   │   ├── projects.py
│   │   │   ├── tasks.py
│   │   │   ├── artifacts.py
│   │   │   ├── approvals.py
│   │   │   ├── models.py
│   │   │   ├── security.py
│   │   │   └── audit.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── security.py
│   │   └── exceptions.py
│   ├── db/
│   │   ├── database.py
│   │   ├── models.py
│   │   └── repositories/
│   ├── llm/
│   │   ├── ollama_client.py
│   │   ├── model_registry.py
│   │   ├── router.py
│   │   └── prompts/
│   ├── rag/
│   │   ├── ingestion.py
│   │   ├── parser.py
│   │   ├── ocr.py
│   │   ├── chunker.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── keyword_search.py
│   │   ├── retriever.py
│   │   └── reranker.py
│   ├── agents/
│   │   ├── state.py
│   │   ├── orchestrator.py
│   │   ├── planner.py
│   │   ├── executor.py
│   │   ├── verifier.py
│   │   └── policies.py
│   ├── tools/
│   │   ├── base.py
│   │   ├── document_search.py
│   │   ├── asset_lookup.py
│   │   ├── work_order_lookup.py
│   │   ├── calculator.py
│   │   ├── document_reader.py
│   │   ├── file_writer.py
│   │   ├── code_executor.py
│   │   └── artifact_generator.py
│   ├── documents/
│   │   ├── generator.py
│   │   ├── docx_renderer.py
│   │   ├── xlsx_renderer.py
│   │   ├── pptx_renderer.py
│   │   ├── pdf_renderer.py
│   │   └── templates.py
│   ├── security/
│   │   ├── access_control.py
│   │   ├── network_monitor.py
│   │   ├── audit.py
│   │   └── classification.py
│   └── services/
│       ├── chat_service.py
│       ├── document_service.py
│       ├── knowledge_service.py
│       ├── agent_service.py
│       ├── artifact_service.py
│       └── model_service.py
├── tests/
├── scripts/
├── data/
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Integration Points

### 1. Chat System
- **Frontend**: ChatScreen.tsx with agent plan, evidence drawer, sources, artifacts
- **Backend**: SSE streaming `/api/chat`, agent orchestrator, tool execution
- **Events**: run_started, router_selected, plan_created, retrieval_started, tool_started, token, verification_completed, artifact_created, run_completed

### 2. Models
- **Frontend**: ModelsScreen.tsx with model cards (auto, reasoning, vision, coding)
- **Backend**: `/api/models` returns actual Ollama models (qwen2.5:7b, qwen2.5-coder:7b, qwen2.5:3b, bge-m3)

### 3. Files/Ingestion
- **Frontend**: FilesScreen.tsx with drag-drop, status (Indexed/Processing/Failed)
- **Backend**: `/api/documents/upload` → parser → OCR → chunker → embeddings → Qdrant

### 4. Knowledge Search
- **Frontend**: KnowledgeScreen.tsx with filters, relevance scores, citations
- **Backend**: `/api/knowledge/search` → hybrid retrieval (semantic + BM25 + metadata)

### 5. Projects/Tasks/Artifacts/Approvals
- **Frontend**: Full CRUD UI with status, risk, progress, classification
- **Backend**: REST APIs with company isolation

### 6. Security
- **Frontend**: SecurityScreen.tsx with status items (LOCAL ONLY badge)
- **Backend**: `/api/security/status` with real verification (not just config)

## Configuration (.env.example)
```
APP_ENV=development
COMPANY_ID=apexpetro

OLLAMA_BASE_URL=http://localhost:11434
PRIMARY_MODEL=qwen2.5:7b
CODING_MODEL=qwen2.5-coder:7b
ROUTER_MODEL=qwen2.5:3b
EMBEDDING_MODEL=bge-m3

QDRANT_URL=http://localhost:6333
DATABASE_URL=sqlite:///./data/runtime/workbench.db

COMPANY_DATA_PATH=../ApexPetro_Sovereign_Dataset_v3
TEST_DATA_ENABLED=false

OFFLINE_MODE=true
ALLOW_EXTERNAL_NETWORK=false
```

## Required Dependencies

### Python Backend
```
fastapi==0.115.0
uvicorn[standard]==0.34.0
pydantic==2.10.0
pydantic-settings==2.6.0
sqlalchemy==2.0.35
aiosqlite==0.20.0
qdrant-client==1.13.0
ollama==0.4.0
PyMuPDF==1.24.0
paddleocr==2.7.0
python-docx==1.1.2
openpyxl==3.1.5
python-pptx==1.0.2
reportlab==4.2.0
python-multipart==0.0.9
httpx==0.27.0
pytest==8.3.0
pytest-asyncio==0.23.0
pytest-cov==5.0.0
python-dotenv==1.0.0
structlog==24.1.0
```

### Frontend (Existing)
- React 19, Vite 8, Tailwind CSS v4, lucide-react

## Development Sequence

1. **IMPLEMENTATION_MAP.md** ✓ (this file)
2. Backend skeleton + config + health
3. Ollama client + model registry + test all 4 models
4. Company ingestion (YAML → DB, document registry → DB)
5. RAG pipeline (parse → OCR → chunk → embed → Qdrant)
6. Chat API (basic non-streaming)
7. Streaming agent (SSE + planner + tools)
8. Tools implementation
9. Document generation (DOCX, XLSX, PPTX, PDF)
10. Sandbox (Docker Python)
11. Frontend API layer + type replacement
12. Security + audit + offline validation
13. Full test suite + E2E validation