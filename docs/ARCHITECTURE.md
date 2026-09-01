# Architecture Document — Sovereign AI Workbench

## Overview

Sovereign On-Premise Agentic AI Workbench for confidential industrial work using open-weight multimodal LLMs.

## System Components

### Frontend (Existing)
- React 19 + TypeScript + Vite + Tailwind CSS v4
- Screens: Chat, Projects, Files, Knowledge, Tasks, Artifacts, Approvals, Models, Security
- Components: Sidebar, TopBar, RightPanel, CommandPalette, ModelDrawer

### Backend (New)
- FastAPI + Python 3.11+
- SQLite (dev) / PostgreSQL (prod) for structured data
- Qdrant for vector embeddings
- Ollama for local LLM inference

### Local Models
| Model | Role | Parameters | VRAM |
|-------|------|------------|------|
| qwen2.5:7b | Primary reasoning | 7B | 4.7 GB |
| qwen2.5-coder:7b | Code generation | 7B | 4.7 GB |
| qwen2.5:3b | Routing/Classification | 3B | 1.9 GB |
| bge-m3:latest | Embeddings | - | 1.2 GB |

## Data Flow

```
User Query
    ↓
FastAPI /api/chat/stream
    ↓
Model Router (qwen2.5:3b) → Select model
    ↓
Agent Orchestrator
    ↓
Planner → Create execution plan
    ↓
Executor → Run tools sequentially
    ├── search_documents (hybrid RAG)
    ├── get_asset (asset registry)
    ├── get_work_orders (WO history)
    ├── calculate (deterministic math)
    ├── read_document (full doc access)
    └── execute_code (Python sandbox)
    ↓
Evidence Collection
    ↓
Reasoning Model (qwen2.5:7b) → Synthesize answer
    ↓
Verifier → Check against evidence
    ↓
Artifact Generator (if needed) → DOCX/XLSX/PPTX/PDF
    ↓
Stream events to frontend via SSE
```

## RAG Pipeline

```
Document Upload
    ↓
Parser (PyMuPDF, python-docx, openpyxl, python-pptx)
    ↓
OCR (PaddleOCR) for scanned pages
    ↓
Chunker (tiktoken, 512 tokens, 50 overlap)
    ↓
Embeddings (bge-m3 via Ollama)
    ↓
Qdrant Vector Store (+ SQLite metadata)
    ↓
Hybrid Retrieval
    ├── Semantic (cosine similarity)
    ├── Keyword (BM25)
    └── Metadata filters (asset, unit, type, classification)
    ↓
Merge & Rank → Top-K results
```

## Security Model

- **Company Isolation**: All queries scoped to `company_id = apexpetro`
- **Classification**: PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
- **RBAC**: EMPLOYEE, ENGINEER, SUPERVISOR, APPROVER, ADMIN
- **Audit Logging**: All operations logged with user, timestamp, resources
- **Network**: No external connections; Ollama, Qdrant, Backend all local
- **Sandbox**: Code execution in isolated subprocess (no network, tmpfs)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/health/detailed` | GET | Detailed service checks |
| `/api/models` | GET | List local models |
| `/api/models/check-availability` | POST | Verify Ollama models |
| `/api/knowledge/search` | POST | Hybrid RAG search |
| `/api/chat/stream` | POST | Streaming chat (SSE) |
| `/api/documents` | GET/POST | Document CRUD + upload |
| `/api/assets` | GET | Asset registry |
| `/api/projects` | GET | Project management |
| `/api/artifacts` | GET | Generated artifacts |
| `/api/approvals` | GET/POST | Approval workflow |

## Deployment

### Development
```bash
# Terminal 1: Ollama
ollama serve

# Terminal 2: Qdrant
docker run -d -p 6333:6333 qdrant/qdrant

# Terminal 3: Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Terminal 4: Frontend
cd "Replicate Existing Design" && npm run dev
```

### Production (Docker Compose)
```bash
cd backend
docker-compose up -d
```

Ollama runs on host for GPU access.

## Offline Verification

```bash
python scripts/verify_offline.py
```
Checks: Ollama local, Qdrant local, no external AI config, no external URLs, no external ports.

## Hardware Requirements

- **Minimum**: 16 GB RAM, 4 GB VRAM
- **Recommended**: 24 GB RAM, 8 GB VRAM
- **GPU**: NVIDIA RTX 3060+ / A5000+ (CUDA)
- **Storage**: 50 GB for models + data

## Company Data Structure

```
data/companies/apexpetro/
├── specs/apexpetro_master.yaml      # Company, units, assets
├── metadata/document_registry.json  # 53 documents
├── assets/                          # Equipment records
├── sops/                            # Standard operating procedures
├── manuals/                         # Engineering manuals
├── historical_records/              # Inspection history
├── maintenance/                     # Maintenance logs, WOs
├── vendors/                         # Vendor reports
└── templates/                       # DOCX/PPTX templates
```

## Extensibility

- **New Company**: Add folder under `data/companies/`, run ingestion
- **New Model**: Add to MODEL_DEFINITIONS in model_registry.py
- **New Tool**: Extend BaseTool, register in tool_registry
- **New Document Type**: Add parser in rag/parser.py, renderer in documents/
- **New Artifact**: Add template + renderer in documents/generator.py