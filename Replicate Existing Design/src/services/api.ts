const API_BASE =
  import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

function authHeaders(): Record<string, string> {
  let token: string | null = null;

  try {
    token = localStorage.getItem("sovereign_token");
  } catch {
    token = null;
  }

  return token
    ? { Authorization: `Bearer ${token}` }
    : {};
}

async function fetchJson<T>(
  url: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(options?.headers || {}),
    },
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }

  return res.json();
}

async function fetchStream(
  url: string,
  options?: RequestInit
): Promise<Response> {
  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(options?.headers || {}),
    },
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }

  return res;
}

async function fetchForm<T>(
  url: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      ...authHeaders(),
      ...(options?.headers || {}),
    },
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }

  return res.json();
}

/* =========================================================
   AUTH
   ========================================================= */

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  full_name: string;
  role?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  full_name: string;
  email: string;
  role: string;
  company_id: string;
  user_id: number;
}

/* =========================================================
   CHAT
   ========================================================= */

export interface ConversationSummary {
  conversation_id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChatSource {
  source: string;
  document_id: string;
  content: string;
  page: number | null;
  section: string | null;
  relevance: number | null;
}

export interface ChatArtifact {
  artifact_id: string;
  name?: string;
  template?: string;
  format?: string;
  download_url?: string;
  approval_id?: string | null;
  version?: number;
  parent_artifact_id?: string | null;
}

export interface ChatMessageMeta {
  model?: string | null;
  verified?: boolean | null;
  analysis?: any;
  calculations?: CalculationResult[];
}

export interface MessageRecord {
  message_id: string;
  role: "user" | "assistant";
  content: string;
  run_id: string | null;
  sources?: ChatSource[];
  artifacts?: ChatArtifact[];
  meta?: ChatMessageMeta;
  attachments?: any[];
  created_at: string;
}

/* =========================================================
   HEALTH
   ========================================================= */

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  company_id: string;
  environment: string;
}

export interface DetailedHealthResponse {
  status: string;
  checks: {
    database: boolean;
    ollama: boolean;
    qdrant: boolean;
  };
  company_id: string;
  environment: string;
}

/* =========================================================
   MODELS
   ========================================================= */

export interface ModelInfo {
  model_id: string;
  role: string;
  provider: string;
  is_local: boolean;
  capabilities: string[];
  context_length: number;
  vram_usage_gb: number;
  status: string;
  last_checked: string | null;
}

export interface ModelListResponse {
  models: ModelInfo[];
}

export interface ModelAvailability {
  model_id: string;
  available: boolean;
  status: string;
  error?: string;
}

export interface ChatRequest {
  query: string;
  conversation_id?: string;
  model?: string;
  attachment_ids?: string[];
}

export interface ChatEvent {
  event: string;
  run_id?: string;
  query?: string;
  model?: string;
  reason?: string;
  steps?: string[];
  error?: string;
  verified?: boolean;
  answer?: string;

  evidence?: Array<{
    source: string;
    document_id: string;
    content: string;
    page: number;
    section: string;
    relevance: number;
  }>;

  tools_used?: string[];
  documents_accessed?: string[];
  analysis?: any;
  calculations?: CalculationResult[];
  artifact?: any;

  artifacts?: Array<{
    artifact_id: string;
    name?: string;
    template?: string;
    format?: string;
    download_url?: string;
  }>;
}

/* =========================================================
   KNOWLEDGE
   ========================================================= */

export interface KnowledgeSearchRequest {
  query: string;
  limit?: number;
  asset_id?: string;
  document_type?: string;
  classification?: string;
}

export interface KnowledgeSearchResult {
  chunk_id: number;
  document_id: string;
  content: string;
  page_number: number;
  section: string | null;
  score: number;
  metadata: Record<string, any>;
}

export interface KnowledgeSearchResponse {
  results: KnowledgeSearchResult[];
  query: string;
  total: number;
}

/* =========================================================
   DOCUMENTS
   ========================================================= */

export interface Document {
  id: number;
  document_id: string;
  file_name: string;
  file_path: string;
  file_type: string;
  file_size: number;
  page_count: number | null;
  classification: string;
  status: string;
  owner: string | null;
  revision: string | null;
  uploaded_at: string | null;
  indexed_at: string | null;
  error_message: string | null;
}

export interface DocumentListResponse {
  documents: Document[];
  total: number;
}

/* =========================================================
   ASSETS
   ========================================================= */

export interface Asset {
  id: number;
  asset_id: string;
  asset_type: string;
  unit: string;
  service: string;
  criticality: string;
  manufacturer: string;
  model: string;
  year: number;
  design_pressure: number;
  normal_pressure: number;
  design_temp: number;
  capacity: string;
  specifications: Record<string, any>;
}

export interface AssetListResponse {
  assets: Asset[];
  total: number;
}

/* =========================================================
   PROJECTS
   ========================================================= */

export interface Project {
  id: number;
  project_id: string;
  name: string;
  unit: string;
  asset: string;
  status: string;
  risk: string;
  progress: number;
  classification: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectListResponse {
  projects: Project[];
  total: number;
}

/* =========================================================
   TASKS
   ========================================================= */

export interface Task {
  id: number;
  task_id: string;
  project_id: number;
  title: string;
  description: string | null;
  status: string;
  priority: number;
  owner_id: number | null;
  due_date: string | null;
  asset: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
}

/* =========================================================
   ARTIFACTS
   ========================================================= */

export interface Artifact {
  id: number;
  artifact_id: string;
  project_id: number | null;
  name: string;
  artifact_type: string;
  file_path: string | null;
  status: string;
  classification: string;
  created_by: number;
  version: number;
  parent_artifact_id: string | null;
  preview_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface ArtifactListResponse {
  artifacts: Artifact[];
  total: number;
}

/* =========================================================
   APPROVALS
   ========================================================= */

export interface Approval {
  id: number;
  approval_id: string;
  artifact_id: number;
  artifact_uuid?: string | null;
  artifact_name?: string | null;
  artifact_type?: string | null;
  download_url?: string | null;
  requested_by: number;
  requested_by_name?: string | null;
  reviewed_by: number | null;
  reviewed_by_name?: string | null;
  status: string;
  comments: string | null;
  requested_at: string;
  reviewed_at: string | null;
}

export interface ApprovalListResponse {
  approvals: Approval[];
  total: number;
}

/* =========================================================
   WORK ORDERS
   ========================================================= */

export interface WorkOrder {
  id: number;
  wo_id: string;
  asset_id: string | null;
  title: string;
  description: string | null;
  status: string;
  priority: number;
  assigned_to: number | null;
  created_at: string;
  updated_at: string;
  closed_at: string | null;
}

export interface WorkOrderListResponse {
  work_orders: WorkOrder[];
  total: number;
}

/* =========================================================
   SECURITY
   ========================================================= */

export interface SecurityStatusItem {
  label: string;
  status: string;
  status_color: string;
  status_bg: string;
  desc: string;
  indicator: "active" | "blocked" | "disabled";
}

export interface SecurityStatusResponse {
  items: SecurityStatusItem[];
  overall: "secure" | "degraded" | "warning";
}

/* =========================================================
   CODE EXECUTION
   ========================================================= */

export interface CodeRunResult {
  stdout: string;
  stderr: string;
  return_code: number;
  execution_ms: number;
  sandbox: string;
}

/* =========================================================
   UPLOADS
   ========================================================= */

export interface UploadResponse {
  document_id: string;
  file_name: string;
  status: string;
}

export interface ChatAttachmentResponse {
  attachment_id: string;
  filename: string;
  ext: string;
  size: number;
  summary: string;
  content_excerpt: string;
}

/* =========================================================
   ARTIFACT PREVIEW
   ========================================================= */

export interface ArtifactPreview {
  artifact_id: string;
  name: string;
  content?: string;
  raw?: string;
  mime?: string;
}

/* =========================================================
   DOCUMENT GENERATION
   ========================================================= */

export interface GenerateDocumentRequest {
  template: string;
  data: Record<string, any>;
  format: "docx" | "xlsx" | "pptx" | "pdf";
}

export interface GenerateDocumentResponse {
  artifact_id: string;
  file_path: string;
  download_url: string;
}

/* =========================================================
   CALCULATIONS
   ========================================================= */

export interface CalculationRequest {
  operation: string;

  inputs?: Record<
    string,
    {
      value: number;
      unit?: string;
      source?: string;
      source_ref?: string;
    }
  >;

  dataset?: Array<Record<string, unknown>>;
  context?: Record<string, unknown>;
}

export interface CalculationResult {
  calculation_id: string;
  trace_id: string;
  operation: string;
  result: unknown;
  unit?: string | null;
  formula?: string | null;
  status: string;
  verification_status: string;
  trace?: Record<string, unknown>;
}

/* =========================================================
   COST INTELLIGENCE TYPES
   ========================================================= */

export interface CostItem {
  name: string;
  category?: string;
  material?: string;
  quantity: number;
  unit_cost: number;
  installation_cost: number;
  maintenance_cost: number;
  criticality: string;
  safety_critical: boolean;
}

export interface CostItemResult {
  name: string;
  category?: string;
  material?: string;

  quantity: number;
  unit_cost: number;

  installation_unit_cost: number;
  maintenance_unit_cost: number;

  criticality: string;
  safety_critical: boolean;

  equipment_cost: number;
  installation_cost: number;
  maintenance_cost: number;
  base_cost: number;

  contingency_rate: number;
  contingency: number;

  total_cost: number;
}

export interface CostSummary {
  equipment_cost: number;
  installation_cost: number;
  maintenance_cost: number;
  base_cost: number;

  contingency_cost: number;
  total_cost: number;

  budget: number;
  variance: number;
  variance_percent: number;

  risk_level: string;
  budget_status: string;

  recommendation: string;
}

export interface CostEstimateResponse {
  engine_version: string;
  project_name: string;
  budget: number;
  items: CostItemResult[];
  summary: CostSummary;
  calculation_trace: any;
}

export interface WhatIfChange {
  index: number;

  quantity?: number;
  unit_cost?: number;

  installation_cost?: number;
  maintenance_cost?: number;

  criticality?: string;
  safety_critical?: boolean;

  name?: string;
  category?: string;
  material?: string;
}

export interface WhatIfRequest {
  project_name: string;
  budget: number;
  items: CostItem[];
  changes: WhatIfChange[];
  scenario_budget?: number;
}

export interface WhatIfResponse {
  engine_version: string;
  project_name: string;

  baseline: CostEstimateResponse;
  scenario: CostEstimateResponse;

  comparison: {
    total_cost_change: number;
    total_cost_change_percent: number;
    budget_change: number;
    risk_change: string;
    budget_status_change: string;
  };
}

/* =========================================================
   COST RESPONSE HELPERS
   ========================================================= */

function toNumber(
  value: unknown,
  fallback = 0
): number {
  const number = Number(value);

  return Number.isFinite(number)
    ? number
    : fallback;
}

function normalizeCostItem(
  item: any
): CostItemResult {
  return {
    name: item?.name ?? "Unnamed Item",

    category:
      item?.category ?? "",

    material:
      item?.material ?? "",

    quantity:
      toNumber(item?.quantity),

    unit_cost:
      toNumber(item?.unit_cost),

    installation_unit_cost:
      toNumber(
        item?.installation_unit_cost ??
          item?.installation_cost
      ),

    maintenance_unit_cost:
      toNumber(
        item?.maintenance_unit_cost ??
          item?.maintenance_cost
      ),

    criticality:
      item?.criticality ?? "low",

    safety_critical:
      Boolean(item?.safety_critical),

    equipment_cost:
      toNumber(item?.equipment_cost),

    installation_cost:
      toNumber(item?.installation_cost),

    maintenance_cost:
      toNumber(item?.maintenance_cost),

    base_cost:
      toNumber(item?.base_cost),

    contingency_rate:
      toNumber(item?.contingency_rate),

    contingency:
      toNumber(
        item?.contingency ??
          item?.contingency_cost
      ),

    total_cost:
      toNumber(item?.total_cost),
  };
}

function normalizeCostResponse(
  response: any
): CostEstimateResponse {
  const data =
    response?.result ??
    response;

  const backendSummary =
    data?.summary ?? {};

  const items =
    Array.isArray(data?.items)
      ? data.items.map(normalizeCostItem)
      : [];

  const budget =
    toNumber(data?.budget);

  const totalCost =
    toNumber(
      backendSummary?.total_estimated_cost ??
        backendSummary?.total_cost
    );

  const variance =
    toNumber(
      backendSummary?.variance
    );

  const variancePercent =
    toNumber(
      backendSummary?.variance_percentage ??
        backendSummary?.variance_percent
    );

  const contingency =
    toNumber(
      backendSummary?.contingency ??
        backendSummary?.contingency_cost
    );

  let recommendation =
    backendSummary?.recommendation;

  if (!recommendation) {
    if (
      backendSummary?.budget_status ===
      "WITHIN_BUDGET"
    ) {
      recommendation =
        "Project is within the approved budget.";
    } else {
      recommendation =
        "Review the estimate against the approved budget.";
    }
  }

  return {
    engine_version:
      data?.engine_version ?? "1.0",

    project_name:
      data?.project_name ?? "",

    budget,

    items,

    summary: {
      equipment_cost:
        toNumber(
          backendSummary?.equipment_cost
        ),

      installation_cost:
        toNumber(
          backendSummary?.installation_cost
        ),

      maintenance_cost:
        toNumber(
          backendSummary?.maintenance_cost
        ),

      base_cost:
        toNumber(
          backendSummary?.base_cost
        ),

      contingency_cost:
        contingency,

      total_cost:
        totalCost,

      budget,

      variance,

      variance_percent:
        variancePercent,

      risk_level:
        backendSummary?.risk_level ??
        "LOW",

      budget_status:
        backendSummary?.budget_status ??
        "WITHIN_BUDGET",

      recommendation,
    },

    calculation_trace:
      data?.calculation_trace ?? {},
  };
}

function normalizeWhatIfResponse(
  response: any
): WhatIfResponse {
  const data =
    response?.result ??
    response;

  const baseline =
    normalizeCostResponse(
      data?.baseline ?? {}
    );

  const scenario =
    normalizeCostResponse(
      data?.scenario ?? {}
    );

  const backendComparison =
    data?.comparison ?? {};

  const baselineTotal =
    baseline.summary.total_cost;

  const scenarioTotal =
    scenario.summary.total_cost;

  const calculatedChange =
    scenarioTotal -
    baselineTotal;

  const calculatedChangePercent =
    baselineTotal !== 0
      ? (calculatedChange /
          baselineTotal) *
        100
      : 0;

  return {
    engine_version:
      data?.engine_version ??
      scenario.engine_version ??
      baseline.engine_version ??
      "1.0",

    project_name:
      data?.project_name ??
      scenario.project_name ??
      baseline.project_name ??
      "",

    baseline,

    scenario,

    comparison: {
      total_cost_change:
        toNumber(
          backendComparison?.total_cost_change,
          calculatedChange
        ),

      total_cost_change_percent:
        toNumber(
          backendComparison?.total_cost_change_percent,
          calculatedChangePercent
        ),

      budget_change:
        toNumber(
          backendComparison?.budget_change
        ),

      risk_change:
        backendComparison?.risk_change ??
        `${baseline.summary.risk_level} → ${scenario.summary.risk_level}`,

      budget_status_change:
        backendComparison?.budget_status_change ??
        `${baseline.summary.budget_status} → ${scenario.summary.budget_status}`,
    },
  };
}

/* =========================================================
   API
   ========================================================= */

export const api = {
  /* =======================================================
     HEALTH
     ======================================================= */

  health: {
    check: () =>
      fetchJson<HealthResponse>(
        "/api/health"
      ),

    detailed: () =>
      fetchJson<DetailedHealthResponse>(
        "/api/health/detailed"
      ),
  },

  /* =======================================================
     AUTH
     ======================================================= */

  auth: {
    login: (
      data: LoginRequest
    ) =>
      fetchJson<LoginResponse>(
        "/api/auth/login",
        {
          method: "POST",
          body: JSON.stringify(data),
        }
      ),

    signup: (
      data: SignupRequest
    ) =>
      fetchJson<LoginResponse>(
        "/api/auth/signup",
        {
          method: "POST",
          body: JSON.stringify(data),
        }
      ),

    me: () =>
      fetchJson<{
        user_id: number;
        full_name: string;
        email: string;
        role: string;
        company_id: string;
      }>(
        "/api/auth/me"
      ),
  },

  /* =======================================================
     MODELS
     ======================================================= */

  models: {
    list: () =>
      fetchJson<ModelListResponse>(
        "/api/models"
      ),

    get: (
      modelId: string
    ) =>
      fetchJson<ModelInfo>(
        `/api/models/${modelId}`
      ),

    checkAvailability: () =>
      fetchJson<{
        availability: ModelAvailability[];
      }>(
        "/api/models/check-availability",
        {
          method: "POST",
        }
      ),

    initialize: () =>
      fetchJson<{
        initialized: number;
        models: string[];
      }>(
        "/api/models/initialize",
        {
          method: "POST",
        }
      ),
  },

  /* =======================================================
     CHAT
     ======================================================= */

  chat: {
    stream: (
      request: ChatRequest
    ) =>
      fetchStream(
        "/api/chat/stream",
        {
          method: "POST",
          body: JSON.stringify(request),
        }
      ),

    getConversation: (
      conversationId: string
    ) =>
      fetchJson<{
        conversation_id: string;
        runs: string[];
      }>(
        `/api/chat/${conversationId}`
      ),

    createConversation: () =>
      fetchJson<ConversationSummary>(
        "/api/chat/conversations",
        {
          method: "POST",
          body: "{}",
        }
      ),

    listConversations: () =>
      fetchJson<{
        conversations: ConversationSummary[];
        total: number;
      }>(
        "/api/chat/conversations"
      ),

    getMessages: (
      conversationId: string
    ) =>
      fetchJson<{
        conversation_id: string;
        messages: MessageRecord[];
        total: number;
      }>(
        `/api/chat/conversations/${conversationId}/messages`
      ),

    renameConversation: (
      conversationId: string,
      title: string
    ) =>
      fetchJson<ConversationSummary>(
        `/api/chat/conversations/${conversationId}`,
        {
          method: "PATCH",
          body: JSON.stringify({
            title,
          }),
        }
      ),

    deleteConversation: (
      conversationId: string
    ) =>
      fetchJson<{
        conversation_id: string;
        deleted: boolean;
      }>(
        `/api/chat/conversations/${conversationId}`,
        {
          method: "DELETE",
        }
      ),

    uploadAttachment: (
      conversationId: string,
      file: File
    ) => {
      const form =
        new FormData();

      form.append(
        "conversation_id",
        conversationId
      );

      form.append(
        "file",
        file
      );

      return fetchForm<ChatAttachmentResponse>(
        "/api/chat/attachments",
        {
          method: "POST",
          body: form,
        }
      );
    },
  },

  /* =======================================================
     KNOWLEDGE
     ======================================================= */

  knowledge: {
    search: (
      request: KnowledgeSearchRequest
    ) =>
      fetchJson<KnowledgeSearchResponse>(
        "/api/knowledge/search",
        {
          method: "POST",
          body: JSON.stringify(request),
        }
      ),

    health: () =>
      fetchJson<{
        status: string;
        service: string;
      }>(
        "/api/knowledge/health"
      ),
  },

  /* =======================================================
     CALCULATIONS
     ======================================================= */

  calculations: {
    execute: (
      request: CalculationRequest
    ) =>
      fetchJson<CalculationResult>(
        "/api/calculations/execute",
        {
          method: "POST",
          body: JSON.stringify(request),
        }
      ),

    spreadsheet: (
      file: File,
      operation: string,
      options?: {
        value_column?: string;
        unit_column?: string;
        period_column?: string;
        sheet_name?: string;
      }
    ) => {
      const form =
        new FormData();

      form.append(
        "file",
        file
      );

      form.append(
        "operation",
        operation
      );

      form.append(
        "value_column",
        options?.value_column ||
          "value"
      );

      form.append(
        "unit_column",
        options?.unit_column ||
          "unit"
      );

      form.append(
        "period_column",
        options?.period_column ||
          "period"
      );

      if (
        options?.sheet_name
      ) {
        form.append(
          "sheet_name",
          options.sheet_name
        );
      }

      return fetchForm<CalculationResult>(
        "/api/calculations/spreadsheet",
        {
          method: "POST",
          body: form,
        }
      );
    },

    list: (
      limit = 50
    ) =>
      fetchJson<{
        calculations: CalculationResult[];
        total: number;
      }>(
        `/api/calculations?limit=${limit}`
      ),

    get: (
      calculationId: string
    ) =>
      fetchJson<CalculationResult>(
        `/api/calculations/${calculationId}`
      ),

    trace: (
      calculationId: string
    ) =>
      fetchJson<Record<string, unknown>>(
        `/api/calculations/${calculationId}/trace`
      ),
  },

  /* =======================================================
     COST INTELLIGENCE
     ======================================================= */

  cost: {
    estimate: async (
      data: {
        project_name: string;
        budget: number;
        items: CostItem[];
      }
    ): Promise<CostEstimateResponse> => {
      const response =
        await fetchJson<any>(
          "/api/cost/estimate",
          {
            method: "POST",
            body: JSON.stringify(data),
          }
        );

      return normalizeCostResponse(
        response
      );
    },

    budgetAnalysis: async (
      data: {
        project_name: string;
        budget: number;
        items: CostItem[];
      }
    ): Promise<CostEstimateResponse> => {
      const response =
        await fetchJson<any>(
          "/api/cost/budget-analysis",
          {
            method: "POST",
            body: JSON.stringify(data),
          }
        );

      return normalizeCostResponse(
        response
      );
    },

    whatIf: async (
      data: WhatIfRequest
    ): Promise<WhatIfResponse> => {
      const response =
        await fetchJson<any>(
          "/api/cost/what-if",
          {
            method: "POST",
            body: JSON.stringify(data),
          }
        );

      return normalizeWhatIfResponse(
        response
      );
    },
  },

  /* =======================================================
     DOCUMENTS
     ======================================================= */

  documents: {
    list: (
      params?: {
        company_id?: string;
        status?: string;
        limit?: number;
        offset?: number;
      }
    ) => {
      const search =
        new URLSearchParams();

      if (
        params?.company_id
      ) {
        search.set(
          "company_id",
          params.company_id
        );
      }

      if (
        params?.status
      ) {
        search.set(
          "status",
          params.status
        );
      }

      if (
        params?.limit !==
        undefined
      ) {
        search.set(
          "limit",
          String(params.limit)
        );
      }

      if (
        params?.offset !==
        undefined
      ) {
        search.set(
          "offset",
          String(params.offset)
        );
      }

      const query =
        search.toString();

      return fetchJson<DocumentListResponse>(
        query
          ? `/api/documents?${query}`
          : "/api/documents"
      );
    },

    upload: (
      file: File,
      metadata?: {
        classification?: string;
        asset_id?: string;
      }
    ) => {
      const form =
        new FormData();

      form.append(
        "file",
        file
      );

      if (
        metadata?.classification
      ) {
        form.append(
          "classification",
          metadata.classification
        );
      }

      if (
        metadata?.asset_id
      ) {
        form.append(
          "asset_id",
          metadata.asset_id
        );
      }

      return fetchForm<UploadResponse>(
        "/api/documents/upload",
        {
          method: "POST",
          body: form,
        }
      );
    },

    get: (
      documentId: string
    ) =>
      fetchJson<Document>(
        `/api/documents/${documentId}`
      ),

    delete: (
      documentId: string
    ) =>
      fetchJson<{
        success: boolean;
      }>(
        `/api/documents/${documentId}`,
        {
          method: "DELETE",
        }
      ),
  },

  /* =======================================================
     ASSETS
     ======================================================= */

  assets: {
    list: (
      params?: {
        company_id?: string;
        unit?: string;
        limit?: number;
        offset?: number;
      }
    ) => {
      const search =
        new URLSearchParams();

      if (
        params?.company_id
      ) {
        search.set(
          "company_id",
          params.company_id
        );
      }

      if (
        params?.unit
      ) {
        search.set(
          "unit",
          params.unit
        );
      }

      if (
        params?.limit !==
        undefined
      ) {
        search.set(
          "limit",
          String(params.limit)
        );
      }

      if (
        params?.offset !==
        undefined
      ) {
        search.set(
          "offset",
          String(params.offset)
        );
      }

      const query =
        search.toString();

      return fetchJson<AssetListResponse>(
        query
          ? `/api/assets?${query}`
          : "/api/assets"
      );
    },

    get: (
      assetId: string
    ) =>
      fetchJson<Asset>(
        `/api/assets/${assetId}`
      ),
  },

  /* =======================================================
     PROJECTS
     ======================================================= */

  projects: {
    list: (
      params?: {
        company_id?: string;
        status?: string;
        limit?: number;
        offset?: number;
      }
    ) => {
      const search =
        new URLSearchParams();

      if (
        params?.company_id
      ) {
        search.set(
          "company_id",
          params.company_id
        );
      }

      if (
        params?.status
      ) {
        search.set(
          "status",
          params.status
        );
      }

      if (
        params?.limit !==
        undefined
      ) {
        search.set(
          "limit",
          String(params.limit)
        );
      }

      if (
        params?.offset !==
        undefined
      ) {
        search.set(
          "offset",
          String(params.offset)
        );
      }

      const query =
        search.toString();

      return fetchJson<ProjectListResponse>(
        query
          ? `/api/projects?${query}`
          : "/api/projects"
      );
    },

    get: (
      projectId: string
    ) =>
      fetchJson<Project>(
        `/api/projects/${projectId}`
      ),

    create: (
      data: Partial<Project>
    ) =>
      fetchJson<Project>(
        "/api/projects",
        {
          method: "POST",
          body: JSON.stringify(data),
        }
      ),

    update: (
      projectId: string,
      data: Partial<Project>
    ) =>
      fetchJson<Project>(
        `/api/projects/${projectId}`,
        {
          method: "PATCH",
          body: JSON.stringify(data),
        }
      ),
  },

  /* =======================================================
     TASKS
     ======================================================= */

  tasks: {
    list: (
      params?: {
        project_id?: number;
        status?: string;
        limit?: number;
        offset?: number;
      }
    ) => {
      const search =
        new URLSearchParams();

      if (
        params?.project_id !==
        undefined
      ) {
        search.set(
          "project_id",
          String(params.project_id)
        );
      }

      if (
        params?.status
      ) {
        search.set(
          "status",
          params.status
        );
      }

      if (
        params?.limit !==
        undefined
      ) {
        search.set(
          "limit",
          String(params.limit)
        );
      }

      if (
        params?.offset !==
        undefined
      ) {
        search.set(
          "offset",
          String(params.offset)
        );
      }

      const query =
        search.toString();

      return fetchJson<TaskListResponse>(
        query
          ? `/api/tasks?${query}`
          : "/api/tasks"
      );
    },

    get: (
      taskId: string
    ) =>
      fetchJson<Task>(
        `/api/tasks/${taskId}`
      ),

    create: (
      data: Partial<Task>
    ) =>
      fetchJson<Task>(
        "/api/tasks",
        {
          method: "POST",
          body: JSON.stringify(data),
        }
      ),

    update: (
      taskId: string,
      data: Partial<Task>
    ) =>
      fetchJson<Task>(
        `/api/tasks/${taskId}`,
        {
          method: "PATCH",
          body: JSON.stringify(data),
        }
      ),
  },

  /* =======================================================
     ARTIFACTS
     ======================================================= */

  artifacts: {
    list: (
      params?: {
        project_id?: number;
        status?: string;
        limit?: number;
        offset?: number;
      }
    ) => {
      const search =
        new URLSearchParams();

      if (
        params?.project_id !==
        undefined
      ) {
        search.set(
          "project_id",
          String(params.project_id)
        );
      }

      if (
        params?.status
      ) {
        search.set(
          "status",
          params.status
        );
      }

      if (
        params?.limit !==
        undefined
      ) {
        search.set(
          "limit",
          String(params.limit)
        );
      }

      if (
        params?.offset !==
        undefined
      ) {
        search.set(
          "offset",
          String(params.offset)
        );
      }

      const query =
        search.toString();

      return fetchJson<ArtifactListResponse>(
        query
          ? `/api/artifacts?${query}`
          : "/api/artifacts"
      );
    },

    get: (
      artifactId: string
    ) =>
      fetchJson<Artifact>(
        `/api/artifacts/${artifactId}`
      ),

    download: (
      artifactId: string
    ) =>
      fetch(
        `${API_BASE}/api/artifacts/${artifactId}/download`,
        {
          headers: {
            ...authHeaders(),
          },
        }
      ),

    preview: (
      artifactId: string
    ) =>
      fetchJson<ArtifactPreview>(
        `/api/artifacts/${artifactId}/preview`
      ),

    downloadUrl: (
      artifactId: string
    ) =>
      `${API_BASE}/api/artifacts/${artifactId}/download`,
  },

  /* =======================================================
     APPROVALS
     ======================================================= */

  approvals: {
    list: (
      params?: {
        status?: string;
        limit?: number;
        offset?: number;
      }
    ) => {
      const search =
        new URLSearchParams();

      if (
        params?.status
      ) {
        search.set(
          "status",
          params.status
        );
      }

      if (
        params?.limit !==
        undefined
      ) {
        search.set(
          "limit",
          String(params.limit)
        );
      }

      if (
        params?.offset !==
        undefined
      ) {
        search.set(
          "offset",
          String(params.offset)
        );
      }

      const query =
        search.toString();

      return fetchJson<ApprovalListResponse>(
        query
          ? `/api/approvals?${query}`
          : "/api/approvals"
      );
    },

    get: (
      approvalId: string
    ) =>
      fetchJson<Approval>(
        `/api/approvals/${approvalId}`
      ),

    create: (
      artifactId: string,
      comments?: string
    ) =>
      fetchJson<Approval>(
        "/api/approvals",
        {
          method: "POST",
          body: JSON.stringify({
            artifact_id:
              artifactId,
            comments,
          }),
        }
      ),

    approve: (
      approvalId: string,
      comments?: string
    ) =>
      fetchJson<Approval>(
        `/api/approvals/${approvalId}/approve`,
        {
          method: "POST",
          body: JSON.stringify({
            comments,
          }),
        }
      ),

    reject: (
      approvalId: string,
      comments?: string
    ) =>
      fetchJson<Approval>(
        `/api/approvals/${approvalId}/reject`,
        {
          method: "POST",
          body: JSON.stringify({
            comments,
          }),
        }
      ),
  },

  /* =======================================================
     WORK ORDERS
     ======================================================= */

  workOrders: {
    list: (
      params?: {
        asset_id?: string;
        status?: string;
        limit?: number;
        offset?: number;
      }
    ) => {
      const search =
        new URLSearchParams();

      if (
        params?.asset_id
      ) {
        search.set(
          "asset_id",
          params.asset_id
        );
      }

      if (
        params?.status
      ) {
        search.set(
          "status",
          params.status
        );
      }

      if (
        params?.limit !==
        undefined
      ) {
        search.set(
          "limit",
          String(params.limit)
        );
      }

      if (
        params?.offset !==
        undefined
      ) {
        search.set(
          "offset",
          String(params.offset)
        );
      }

      const query =
        search.toString();

      return fetchJson<WorkOrderListResponse>(
        query
          ? `/api/work-orders?${query}`
          : "/api/work-orders"
      );
    },

    get: (
      woId: string
    ) =>
      fetchJson<WorkOrder>(
        `/api/work-orders/${woId}`
      ),
  },

  /* =======================================================
     SECURITY
     ======================================================= */

  security: {
    status: () =>
      fetchJson<SecurityStatusResponse>(
        "/api/security/status"
      ),
  },

  /* =======================================================
     CODE EXECUTION
     ======================================================= */

  code: {
    run: (
      code: string,
      timeout = 30
    ) =>
      fetchJson<CodeRunResult>(
        "/api/code/run",
        {
          method: "POST",
          body: JSON.stringify({
            code,
            language: "python",
            timeout,
          }),
        }
      ),
  },

  /* =======================================================
     DOCUMENT GENERATION
     ======================================================= */

  documentsGeneration: {
    generate: (
      request: GenerateDocumentRequest
    ) =>
      fetchJson<GenerateDocumentResponse>(
        "/api/documents/generate",
        {
          method: "POST",
          body: JSON.stringify(request),
        }
      ),
  },
};