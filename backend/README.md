# Sovereign AI Workbench — Backend

On-premise agentic AI workbench for confidential industrial work using local LLMs.

## Architecture

```
Frontend (React/TypeScript) → FastAPI Backend → Local Ollama Models
                                    ↓
                              Qdrant Vector DB + SQLite
                                    ↓
                              ApexPetro Knowledge Base
```

## Models (Local Only)

| Model | Role | VRAM |
|-------|------|------|
| qwen2.5:7b | Reasoning, RAG synthesis | 4.7 GB |
| qwen2.5-coder:7b | Code generation, calculations | 4.7 GB |
| qwen2.5:3b | Routing, classification | 1.9 GB |
| bge-m3:latest | Embeddings | 1.2 GB |

## Prerequisites

- Ubuntu 22.04+ / Windows 10+ with WSL2
- Python 3.11+
- Ollama installed and running with models above
- Qdrant (via Docker) or local installation
- 24 GB RAM, NVIDIA GPU with 6+ GB VRAM recommended

## Quick Start (Ubuntu)

```bash
# 1. Clone and navigate
cd /path/to/Smart\ India\ Hackathon/backend

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start Qdrant (requires Docker)
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:latest

# 5. Start Ollama (separate terminal)
ollama serve

# 6. Verify models are available
ollama list
# Should show: qwen2.5:7b, qwen2.5-coder:7b, qwen2.5:3b, bge-m3:latest

# 7. Ingest company data
PYTHONPATH=. python scripts/ingest_company.py

# 8. Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 9. Test endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/api/models
curl -X POST http://localhost:8000/api/knowledge/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the maximum operating pressure for P-102?", "limit": 5}'
```

## Quick Start (Windows)

```powershell
# 1. Navigate
cd "C:\path\to\Smart India Hackathon\backend"

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start Qdrant (requires Docker Desktop)
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:latest

# 5. Start Ollama (separate terminal)
ollama serve

# 6. Verify models
ollama list

# 7. Ingest company data
$env:PYTHONPATH="."; python scripts/ingest_company.py

# 8. Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 9. Test
curl http://localhost:8000/api/health
```

## Using Docker Compose

```bash
cd backend
docker-compose up -d
```

This starts both Qdrant and the backend. Ollama must run on host.

## API Endpoints

### Health
- `GET /api/health` — Basic health check
- `GET /api/health/detailed` — Detailed service checks

### Models
- `GET /api/models` — List available local models
- `POST /api/models/check-availability` — Verify Ollama model availability
- `POST /api/models/initialize` — Register models in registry

### Knowledge Search
- `POST /api/knowledge/search` — Hybrid semantic + keyword search
  ```json
  {
    "query": "P-102 operating pressure limit",
    "limit": 10,
    "asset_id": "P-102",
    "document_type": "SOP"
  }
  ```

### Chat (Streaming)
- `POST /api/chat/stream` — SSE streaming chat with agent
  ```json
  {
    "query": "Analyze the latest P-102 inspection and prepare an approval note",
    "conversation_id": "optional-uuid"
  }
  ```
  Events: `run_started`, `router_selected`, `plan_created`, `retrieval_completed`, `tool_started`, `tool_completed`, `verification_completed`, `artifact_created`, `run_completed`

### Documents
- `GET /api/documents` — List documents
- `POST /api/documents/upload` — Upload and ingest
- `GET /api/documents/{id}` — Get document details

### Assets
- `GET /api/assets` — List all assets
- `GET /api/assets/{asset_id}` — Get asset details

### Projects
- `GET /api/projects` — List projects
- `GET /api/projects/{project_id}` — Get project details

## Frontend Integration

The frontend expects these API contracts. Update `src/services/api.ts` base URL:

```typescript
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
```

## Environment Variables

```env
APP_ENV=development
COMPANY_ID=apexpetro

OLLAMA_BASE_URL=http://localhost:11434
PRIMARY_MODEL=qwen2.5:7b
CODING_MODEL=qwen2.5-coder:7b
ROUTER_MODEL=qwen2.5:3b
EMBEDDING_MODEL=bge-m3:latest

QDRANT_URL=http://localhost:6333
DATABASE_URL=sqlite:///./data/runtime/workbench.db

COMPANY_DATA_PATH=../ApexPetro_Sovereign_Dataset_v3
TEST_DATA_ENABLED=false

OFFLINE_MODE=true
ALLOW_EXTERNAL_NETWORK=false
```

## Offline Verification

```bash
python scripts/verify_offline.py
```

Checks:
- Ollama is local
- Qdrant is local
- No external AI provider configs
- No external URLs in codebase

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app
│   ├── api/routes/             # API endpoints
│   ├── core/                   # Config, logging, security
│   ├── db/                     # Database models & repositories
│   ├── llm/                    # Ollama client, model registry, router
│   ├── rag/                    # Parser, OCR, chunker, embeddings, retriever
│   ├── agents/                 # Planner, executor, verifier, orchestrator
│   ├── tools/                  # Document search, asset lookup, calculator, etc.
│   ├── services/               # Chat, document, knowledge services
│   └── documents/              # DOCX/XLSX/PPTX/PDF generators
├── scripts/                    # Ingestion, health check, verification
├── tests/                      # Unit, integration, E2E tests
├── data/                       # SQLite DB, Qdrant, generated artifacts
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── .env.example
```

## Test Cases

```bash
# Run unit tests
python -m pytest tests/unit -v

# Run integration tests
python -m pytest tests/integration -v

# Run evaluation
python scripts/run_evaluation.py
```

Expected test queries:
- "What is P-102?" → Equipment info
- "What is P-102's approved maximum operating pressure?" → 40 bar
- "What was P-102 pressure in 2024, 2025 and 2026?" → 34, 37, 42 bar
- "Is 42 bar within the approved operating limit?" → No, +2 bar deviation
- "What conflict exists in the vendor report?" → Vendor references 45 bar vs internal 40 bar
- "Analyze the latest P-102 inspection and prepare an approval note" → Full agent workflow + DOCX artifact

## Security

- All inference runs locally via Ollama
- No external API calls
- Qdrant runs locally
- Code execution in isolated subprocess (no network)
- Audit logging for all operations
- Company isolation enforced at DB level
- Document classification preserved (PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED)

## License

Internal use only — ApexPetro Energy Limited