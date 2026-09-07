

### Sovereign On-Premise Agentic AI Workbench using Open-Weight Multimodal LLMs for Confidential Industrial Work

The problem belongs to the **Smart Automation** theme and targets industrial environments where AI must operate on sensitive and confidential engineering information.

Industrial organizations such as refineries, oil & gas companies, manufacturing facilities, and process plants maintain huge volumes of confidential technical information.

This information can include:

- Engineering manuals
- Standard Operating Procedures
- Inspection reports
- Maintenance records
- Asset registers
- Equipment specifications
- Historical operating data
- Engineering drawings
- Technical reports
- Spreadsheets
- Work orders
- Process measurements
- Safety procedures
- Internal operational documents

Traditional cloud-based AI systems can create significant concerns around:

- Data privacy
- Data sovereignty
- Confidentiality
- Intellectual property
- Industrial cybersecurity
- Regulatory compliance
- Unauthorized access
- AI hallucination
- Incorrect engineering calculations
- Lack of traceability
- Lack of auditability

---

## 1.2 Project Objective

The objective of this project is to develop an **AI-powered sovereign industrial workbench** that can operate inside an organization's controlled environment.

The platform combines:

- Agentic AI
- Open-weight LLMs
- Local LLM inference
- Retrieval-Augmented Generation
- Industrial document intelligence
- OCR
- Vector search
- Deterministic engineering calculations
- Data analysis
- Controlled code execution
- Document generation
- Verification
- Provenance
- Human approval

The system is designed around the principle:

```text
Understand
    ↓
Retrieve
    ↓
Calculate
    ↓
Verify
    ↓
Explain
    ↓
Approve
    ↓
Deliver
2. Complete Project Overview
2.1 What is the System?

The Sovereign On-Premise Agentic AI Workbench is a unified AI platform for confidential industrial work.

Instead of being only a chatbot, it acts as an AI workbench capable of interacting with:

Industrial documents
Asset information
Historical records
Structured datasets
Engineering calculations
Maintenance information
Knowledge repositories
Analysis tools
Code execution tools
Document-generation tools
2.2 Core Idea

A user can ask an industrial question using natural language.

For example:

"What is the pressure of P-102 and how far is it from the approved operating limit?"

The system can:

User Question
      ↓
Intent Understanding
      ↓
Agent Planning
      ↓
Knowledge Retrieval
      ↓
Structured Calculation Request
      ↓
Deterministic Calculation
      ↓
Verification
      ↓
Trace / Provenance
      ↓
LLM Explanation
      ↓
User / Approval / Artifact
2.3 Why Agentic AI?

A conventional chatbot generally follows:

Question
   ↓
LLM
   ↓
Answer

The proposed system follows:

Question
   ↓
Planner
   ↓
Retrieve Information
   ↓
Select Tools
   ↓
Execute Tools
   ↓
Calculate
   ↓
Verify
   ↓
Explain
   ↓
Approve / Deliver

This provides much stronger control and reliability for industrial applications.

3. Previous / Original Implementation

Before the Calculation Engine enhancement, the project already contained a strong foundation for an industrial agentic AI platform.

The original implementation included the following major components.

3.1 Agent Architecture

The project already had:

Agent planner
Agent executor
Agent orchestrator
Agent state
Verification layer

These components provided the basic agentic workflow.

3.2 Local LLM Architecture

The project included infrastructure for:

Local LLM communication
Ollama
Model registration
Model routing

This provided the foundation for sovereign AI inference.

3.3 RAG System

The original project included:

Document parsing
OCR
Chunking
Embeddings
Keyword search
Vector search
Retrieval
Qdrant integration
3.4 Existing Tools

The original tool layer contained:

Asset lookup
Work-order lookup
Document search
Document reader
Data analysis
Code execution
Coding agent
Document generation
Calculator
3.5 Existing Industrial Dataset

The project contains a sovereign industrial dataset:

ApexPetro_Sovereign_Dataset_v3/

with:

assets/
historical_records/
manuals/
sops/
templates/

Example asset data includes an asset register and historical P-102 inspection and maintenance records.

3.6 Existing Frontend

The original project already provided a web-based workbench interface supporting:

Chat
Knowledge interaction
Calculations
Data analysis
Document generation
Code-related operations
Industrial information retrieval
3.7 Existing Backend

The backend already exposed multiple FastAPI routes for:

Authentication
Chat
Assets
Documents
Knowledge
Models
Projects
Tasks
Work orders
Approvals
Security
Artifacts
4. Everything Newly Implemented

The major new enhancement is the transformation of the basic calculator functionality into a structured Sovereign Deterministic Calculation Engine.

4.1 New Calculation Architecture

A dedicated calculation subsystem was introduced:

backend/app/calculation/

containing:

__init__.py
engine.py
errors.py
formulas.py
models.py
registry.py
rules.py
statistics.py
store.py
trace.py
trends.py
units.py
verification.py
spreadsheet.py
4.2 Newly Added Capabilities

The enhanced system supports:

Deterministic arithmetic
Percentage calculations
Absolute deviation
Percentage deviation
Percentage change
Ratios
Statistics
Mean
Median
Trend analysis
Moving averages
Unit validation
Unit conversion
Threshold evaluation
Engineering rules
Calculation verification
Calculation IDs
Trace IDs
Provenance
Structured calculation requests
Structured calculation responses
Spreadsheet processing
CSV support
XLSX support
Agent integration
Calculation API
4.3 Agent Integration

The planner was enhanced to recognize calculation-related natural-language requests.

The calculation workflow is now:

User
 ↓
Planner
 ↓
Calculation Intent
 ↓
Structured Calculation Step
 ↓
Calculator Tool
 ↓
Calculation Engine
 ↓
Verification
 ↓
Orchestrator
 ↓
LLM Explanation
4.4 Calculator Tool Enhancement

The existing calculator tool was converted into a deterministic wrapper around the Calculation Engine.

This ensures that agents do not independently perform engineering calculations using uncontrolled LLM reasoning.

5. Full Calculation Engine Work

The Calculation Engine is one of the core engineering components of the project.

Its purpose is to provide a controlled and deterministic environment for numerical and engineering calculations.

5.1 Calculation Engine Responsibilities

The Calculation Engine handles:

Input validation
Unit validation
Unit normalization
Formula selection
Deterministic execution
Rule evaluation
Result validation
Verification
Trace creation
Provenance recording
5.2 Supported Operations

Current core operations include:

add
subtract
multiply
divide
ratio
absolute_deviation
percentage_deviation
percentage_change
mean
median
statistics
trend
moving_average
5.3 Basic Arithmetic
Addition
A + B

Example:

10 bar + 5 bar = 15 bar
Subtraction
A - B

Example:

42 bar - 40 bar = 2 bar
Multiplication
A × B
Division
A / B

Division by zero is explicitly rejected.

Ratio
A / B

Ratios are returned with appropriate structured metadata.




7. Agent Architecture

The agent architecture consists of:

backend/app/agents/
├── planner.py
├── executor.py
├── orchestrator.py
├── state.py
└── verifier.py
7.1 Planner

The planner determines:

User intent
Required tools
Required calculation
Required documents
Required datasets
Task sequence
7.2 Executor

The executor performs the planned tool actions.

7.3 Orchestrator

The orchestrator coordinates the overall process.

It combines:

User request
Retrieved evidence
Tool outputs
Calculation results
Verification results

before generating the final response.

7.4 State

Agent state maintains information throughout the workflow.

7.5 Verifier

The verification layer validates the workflow and result.

8. LLM / Ollama

The project is designed to use open-weight LLMs locally.

Ollama provides the local inference runtime.

Relevant backend components:

backend/app/llm/
├── model_registry.py
├── ollama_client.py
└── router.py
8.1 LLM Responsibilities

The LLM handles:

Natural-language understanding
Intent classification
Planning
Tool selection
Explanation
Summarization
Response generation
8.2 What the LLM Should Not Do

The LLM should not independently become the authoritative source for:

Engineering calculations
Safety limits
Plant-specific operating limits
Approved formulas
Final numerical results

Instead:

LLM
 ↓
Structured Request
 ↓
Deterministic Engine
9. RAG / Qdrant

The RAG subsystem allows the AI to retrieve confidential industrial knowledge.

backend/app/rag/
├── chunker.py
├── embeddings.py
├── keyword_search.py
├── ocr.py
├── parser.py
├── retriever.py
└── vector_store.py
9.1 RAG Pipeline
Document
   ↓
Parsing
   ↓
OCR if required
   ↓
Chunking
   ↓
Embeddings
   ↓
Qdrant
   ↓
Retrieval
   ↓
Relevant Evidence
   ↓
Agent / Calculation Engine
9.2 RAG Responsibilities

RAG provides:

Authoritative values
SOP information
Equipment specifications
Historical measurements
Maintenance information
Engineering references
Source citations

The Calculation Engine then uses the retrieved values to perform deterministic calculations.

10. OCR / Document Processing

Industrial knowledge is not always stored as machine-readable text.

The platform therefore includes document processing and OCR.

Supported document workflows include:

PDF parsing
OCR
Text extraction
Chunking
Metadata handling
Retrieval

Example:

Scanned Inspection Report
        ↓
OCR
        ↓
Extracted Measurement
        ↓
RAG
        ↓
Calculation Engine
11. Tools

The tool layer provides controlled capabilities to agents.

backend/app/tools/

Current tools include:

asset_lookup.py
base.py
calculator.py
code_executor.py
coding_agent.py
data_analysis.py
document_generation_tool.py
document_reader.py
document_search.py
work_order_lookup.py
11.1 Asset Lookup

Retrieves asset-related information.

11.2 Work Order Lookup

Retrieves maintenance/work-order information.

11.3 Document Search

Searches the industrial knowledge base.

11.4 Document Reader

Reads and extracts information from documents.

11.5 Calculator

Acts as the controlled interface to the deterministic Calculation Engine.

11.6 Data Analysis

Performs structured data-analysis tasks.

11.7 Code Executor

Provides controlled execution for supported analytical/code workflows.

11.8 Coding Agent

Supports programming-related tasks where appropriate.

11.9 Document Generation

Creates structured industrial artifacts.

12. Data Analysis

The workbench supports industrial data analysis.

Potential data sources include:

CSV
Excel
Historical measurements
Asset datasets
Maintenance records
Inspection datasets
12.1 Supported Analysis

Examples include:

Mean
Median
Minimum
Maximum
Range
Standard deviation
Percentiles
Time-series changes
Moving averages
Parameter comparisons
12.2 Multi-Parameter Analysis



The system does not hide engineering information behind an unexplained single score.

13. Code Execution

The project contains a controlled code-execution capability.

It can support:

Python execution
Numerical analysis
Dataset processing
Data transformations
Technical calculations
Analytical workflows

The code execution environment should remain controlled and isolated.

Arbitrary host access and arbitrary network access should not be permitted in a sovereign industrial deployment.

14. Document Generation

The platform supports generation of industrial artifacts.

Potential outputs include:

DOCX
XLSX
PPTX
PDF
14.1 Artifact Workflow
User Request
     ↓
Agent
     ↓
Retrieve Evidence
     ↓
Calculation Engine
     ↓
Verification
     ↓
Artifact Generation
     ↓
Final Document

Calculation IDs can be referenced inside generated artifacts to provide traceability.

15. Approval Workflow

Industrial systems require human oversight for sensitive actions.

The platform supports approval-oriented workflows.

AI Recommendation
       ↓
Verification
       ↓
Human Review
       ↓
Approval
       ↓
Action / Artifact

The system is designed so that AI does not automatically replace human engineering responsibility.

16. Frontend / Backend
16.1 Frontend

The frontend uses:

React
Vite
JavaScript / TypeScript
HTML
CSS

Frontend location:

Replicate Existing Design/
16.2 Backend

The backend uses:

Python
FastAPI
Pydantic
SQLAlchemy
Uvicorn

Backend location:

backend/
16.3 Backend Port

Default development backend:

http://127.0.0.1:8000
16.4 Frontend Port

Development frontend:

http://localhost:5173/
17. Complete Architecture
                         ┌─────────────────────┐
                         │        USER         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    React Frontend   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     FastAPI API     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Agent Orchestrator│
                         └──────────┬──────────┘
                                    │
                      ┌─────────────┼─────────────┐
                      │             │             │
                      ▼             ▼             ▼
                ┌──────────┐ ┌──────────┐ ┌────────────┐
                │ Planner  │ │ Local LLM│ │   RAG      │
                └──────────┘ │ Ollama   │ │ Qdrant     │
                             └──────────┘ └─────┬──────┘
                                                │
                      ┌─────────────────────────┼───────────────────────┐
                      │                         │                       │
                      ▼                         ▼                       ▼
                ┌─────────────┐          ┌─────────────┐        ┌────────────┐
                │ Calculation │          │ Data        │        │ Document   │
                │ Engine      │          │ Analysis    │        │ Processing │
                └──────┬──────┘          └─────────────┘        └────────────┘
                       │
              ┌────────┼─────────┐
              ▼        ▼         ▼
          Formula    Units      Rules
           Engine    Engine     Engine
              │        │         │
              └────────┼─────────┘
                       ▼
                ┌──────────────┐
                │ Verification │
                └──────┬───────┘
                       ▼
                ┌──────────────┐
                │ Trace / Audit│
                └──────┬───────┘
                       ▼
                ┌──────────────┐
                │ LLM Explain  │
                └──────┬───────┘
                       ▼
                ┌──────────────┐
                │ User / Human │
                │   Approval   │
                └──────────────┘
18. Complete Folder Structure
Smart_India_Hackathon_Sovereign_On_Premise_Agentic_AI_Workbench/
│
├── backend/
│   │
│   ├── app/
│   │   │
│   │   ├── agents/
│   │   │   ├── executor.py
│   │   │   ├── orchestrator.py
│   │   │   ├── planner.py
│   │   │   ├── state.py
│   │   │   └── verifier.py
│   │   │
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── approvals.py
│   │   │       ├── artifacts.py
│   │   │       ├── assets.py
│   │   │       ├── auth.py
│   │   │       ├── chat.py
│   │   │       ├── code.py
│   │   │       ├── document_generation.py
│   │   │       ├── documents.py
│   │   │       ├── health.py
│   │   │       ├── knowledge.py
│   │   │       ├── models.py
│   │   │       ├── projects.py
│   │   │       ├── security.py
│   │   │       ├── tasks.py
│   │   │       └── work_orders.py
│   │   │
│   │   ├── calculation/
│   │   │   ├── __init__.py
│   │   │   ├── engine.py
│   │   │   ├── errors.py
│   │   │   ├── formulas.py
│   │   │   ├── models.py
│   │   │   ├── registry.py
│   │   │   ├── rules.py
│   │   │   ├── statistics.py
│   │   │   ├── store.py
│   │   │   ├── trace.py
│   │   │   ├── trends.py
│   │   │   ├── units.py
│   │   │   ├── verification.py
│   │   │   └── spreadsheet.py
│   │   │
│   │   ├── core/
│   │   ├── db/
│   │   │
│   │   ├── llm/
│   │   │   ├── model_registry.py
│   │   │   ├── ollama_client.py
│   │   │   └── router.py
│   │   │
│   │   ├── rag/
│   │   │   ├── chunker.py
│   │   │   ├── embeddings.py
│   │   │   ├── keyword_search.py
│   │   │   ├── ocr.py
│   │   │   ├── parser.py
│   │   │   ├── retriever.py
│   │   │   └── vector_store.py
│   │   │
│   │   ├── services/
│   │   │
│   │   └── tools/
│   │       ├── asset_lookup.py
│   │       ├── base.py
│   │       ├── calculator.py
│   │       ├── code_executor.py
│   │       ├── coding_agent.py
│   │       ├── data_analysis.py
│   │       ├── document_generation_tool.py
│   │       ├── document_reader.py
│   │       ├── document_search.py
│   │       └── work_order_lookup.py
│   │
│   ├── data/
│   ├── scripts/
│   ├── tests/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
│
├── ApexPetro_Sovereign_Dataset_v3/
│   ├── assets/
│   │   └── asset_register.xlsx
│   │
│   ├── historical_records/
│   │   ├── inspection/
│   │   │   ├── P-102_inspection_2024.pdf
│   │   │   ├── P-102_inspection_2025.pdf
│   │   │   └── P-102_inspection_2026.pdf
│   │   │
│   │   └── maintenance/
│   │       └── P-102_maintenance_history.pdf
│   │
│   ├── manuals/
│   │   └── engineering/
│   │
│   ├── sops/
│   │
│   └── templates/
│
├── Replicate Existing Design/
│   └── frontend/
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── IMPLEMENTATION_MAP.md
│   ├── IMPLEMENTATION_PLAN.md
│   └── IMPLEMENTATION_STATUS.md
│
├── .gitignore
└── README.md
19. APIs

The FastAPI backend exposes multiple functional API groups.

Main API categories include:

/api/auth
/api/chat
/api/calculations
/api/assets
/api/documents
/api/knowledge
/api/models
/api/projects
/api/tasks
/api/work-orders
/api/approvals
/api/security
/api/artifacts

Swagger documentation:

http://127.0.0.1:8000/docs
20. Calculation Engine APIs

The dedicated Calculation API provides structured endpoints.

Execute Calculation
POST /api/calculations/execute
Statistics
POST /api/calculations/statistics
Trend
POST /api/calculations/trend
Mean
POST /api/calculations/mean
Median
POST /api/calculations/median
Moving Average
POST /api/calculations/moving-average
Unit Conversion
POST /api/calculations/unit-convert
Threshold Evaluation
POST /api/calculations/threshold
Get Calculation
GET /api/calculations/{calculation_id}
Get Calculation Trace
GET /api/calculations/{calculation_id}/trace
21. Formula Engine

The Formula Engine provides deterministic engineering formulas.

Supported core formulas include:

Addition
Subtraction
Multiplication
Division
Ratio
Absolute Deviation
Percentage Deviation
Percentage Change
Mean
Median
Statistics
Trend
Moving Average
Percentage Deviation
Percentage Deviation =
((Actual - Reference) / Reference) × 100

Example:

Actual = 42
Reference = 40

((42 - 40) / 40) × 100
= 5%
Percentage Change
Percentage Change =
((Current - Previous) / Previous) × 100
Absolute Deviation
Absolute Deviation =
Actual - Reference
22. Unit Engine

The Unit Engine validates and normalizes engineering units.

Responsibilities
Unit validation
Compatibility checking
Conversion
Normalization
Original unit preservation
Normalized unit preservation
Example
Input:
1000 kPa

Normalized:
10 bar
Invalid Example
Pressure + Temperature

must be rejected because the dimensions are incompatible.

The engine must never guess a conversion.

23. Rules Engine

The Rules Engine is separate from the Formula Engine.

This is important because:

Formula
=
Mathematical calculation

Rule
=
Engineering decision condition
Example

Formula:

Deviation =
42 - 40
=
+2 bar

Rule:

Actual Pressure > Approved Limit

Result:

ENGINEERING_REVIEW
Rule Information

A rule can contain:

Rule ID
Rule Name
Parameter
Authority
Version
Unit
Limit
Condition
Actual Value
Deviation
Status
Example Rule
Rule ID:
P102-PRESSURE-LIMIT

Name:
P-102 Operating Pressure Rule

Parameter:
Pressure

Authority:
P-102 approved operating limit

Version:
1.0

Limit:
40 bar
24. Statistics

The Statistics Engine supports:

Count
Sum
Mean
Median
Minimum
Maximum
Range
Variance
Standard Deviation
Percentiles
Mean
Mean =
Sum of Values / Number of Values
Median

The middle value after sorting the dataset.

Range
Range =
Maximum - Minimum
Standard Deviation

Used to measure the spread of values around the mean.

Dataset Scope

Statistical outputs should preserve:

Dataset
Rows
Time range
Asset
Parameter
Number of values

This allows the result to be auditable.

25. Time-Series / Trends

The Trend Engine supports historical data analysis.

Period-to-Period Change

For:

Previous = 34 bar
Current = 42 bar

Absolute change:

42 - 34
=
+8 bar

Percentage change:

((42 - 34) / 34) × 100
=
23.53%
Moving Average

For a window of three values:

10
20
30

Moving average:

(10 + 20 + 30) / 3
=
20

The system can generate rolling averages over historical datasets.

Forecasting Principle

Historical trend analysis must not automatically be described as forecasting.

Forecasting should be treated as a separate capability with its own model, validation, and uncertainty handling.

26. Verification

Verification is a separate stage after deterministic calculation.

The verifier checks:

Source
 ↓
Inputs
 ↓
Units
 ↓
Formula
 ↓
Execution
 ↓
Output
 ↓
Rule
 ↓
Trace
Verification Checks
Input Verification

Are required values present?

Unit Verification

Are units valid and compatible?

Formula Verification

Is the approved formula being used?

Output Verification

Is the result consistent with the calculation?

Rule Verification

Is the rule version valid?

Provenance Verification

Are sources available?

Verification Result

Example:

verification_status:
VERIFIED

If a verification problem occurs, the system should report it rather than silently accepting the result.

27. Trace / Provenance

Every calculation can be assigned:

Calculation ID
Trace ID

Example:

Calculation ID:
CAL-35B858B5ED30

Trace ID:
TRACE-3CAB137224A9
Trace Contents

A calculation trace may contain:

Input Values
Original Units
Normalized Values
Source References
Asset ID
Dataset Reference
Timestamp
Formula
Formula Version
Rule
Rule Version
Engine Version
Result
Verification Status
Warnings
Errors
Why Traceability Matters

Traceability allows an engineer to answer:

Where did this number come from?

The system can show:

Source
  ↓
Input
  ↓
Formula
  ↓
Calculation
  ↓
Rule
  ↓
Result
  ↓
Verification
28. Spreadsheet / Excel / CSV Support

The Calculation Engine supports structured spreadsheet inputs.

Supported formats:

CSV
XLSX
Spreadsheet Workflow
Excel / CSV
     ↓
File Parsing
     ↓
Sheet Detection
     ↓
Column Detection
     ↓
Type Detection
     ↓
Unit Detection
     ↓
Missing Value Detection
     ↓
Structured Dataset
     ↓
Calculation Engine
Example

A spreadsheet containing:

Date | Asset | Pressure | Temperature

can be used for questions such as:

"Calculate the average pressure for P-102."

or:

"Calculate the percentage change in pressure between 2025 and 2026."

29. P-102 End-to-End Example

The P-102 workflow demonstrates the complete architecture.

Step 1 — User Question

Example:

"Is P-102 operating above its approved pressure limit?"

Step 2 — Retrieval

The system retrieves:

Actual Pressure = 42 bar

from the available industrial evidence.

It retrieves:

Approved Limit = 40 bar

from the authoritative source/rule.

Step 3 — Structured Calculation

The agent creates:

Operation:
percentage_deviation

with:

Actual:
42 bar

Reference:
40 bar
Step 4 — Deterministic Calculation

Absolute deviation:

42 - 40
=
+2 bar

Percentage deviation:

((42 - 40) / 40) × 100
=
5%
Step 5 — Rule Evaluation

Condition:

42 > 40

Therefore:

Status =
ENGINEERING_REVIEW
Step 6 — Verification

The result is independently checked.

Verification =
VERIFIED
Step 7 — Trace

Example:

Calculation ID:
CAL-35B858B5ED30

Trace ID:
TRACE-3CAB137224A9
Step 8 — Final Explanation

The LLM explains the verified result:

P-102 is operating 2 bar above the approved
40 bar reference limit.

This corresponds to a 5% deviation.

The deterministic Calculation Engine verified
the result and classified the condition as
ENGINEERING_REVIEW.
30. Security / Sovereignty

Security and sovereignty are fundamental requirements of the platform.

30.1 On-Premise Processing

The system is designed to operate inside the organization's infrastructure.

Sensitive information can remain within the organization's controlled environment.

30.2 Local LLM

LLM inference can be performed using local open-weight models through Ollama.

30.3 Confidential Knowledge Base

Industrial documents can remain in local storage and local vector databases.

30.4 Controlled Tool Access

Agents should only have access to approved tools.

30.5 No Arbitrary File Access

Agents should not be allowed unrestricted access to the host machine.

30.6 No Arbitrary Network Access

Agents should not be allowed unrestricted outbound network access in a confidential deployment.

30.7 Permission-Aware Access

Access should consider:

User
Role
Project
Dataset
Document
Classification
Permission
30.8 Auditability

Important operations should be traceable.

31. Error Handling

The Calculation Engine follows explicit error handling.

Missing Input

Example:

Actual pressure is missing.

The engine must not assume:

Actual pressure = 0

Instead:

ERROR:
Required input is missing.
Invalid Numeric Input

Example:

Pressure = "abc"

Result:

Calculation validation error
Division by Zero

Example:

10 / 0

Result:

Division by zero is not allowed.
Incompatible Units

Example:

40 bar + 100 °C

Result:

Incompatible units.
Unknown Calculation

If an unsupported operation is requested:

Unknown calculation operation.
Invalid Formula

The engine must reject invalid formulas rather than executing arbitrary expressions.

Stale Rule

If a rule is outdated:

Rule verification failed.

The system should not silently use a potentially invalid engineering limit.

Execution Failure

Unexpected calculation failures should return structured errors.

32. Testing

Testing is essential for engineering reliability.

32.1 Formula Tests

Test:

Addition
Subtraction
Multiplication
Division
Ratio
Absolute Deviation
Percentage Deviation
Percentage Change
32.2 Unit Tests

Test:

Valid Conversion
Invalid Conversion
Compatible Units
Incompatible Units
32.3 Rule Tests

Test:

Below Limit
At Limit
Above Limit
32.4 Statistical Tests

Test:

Mean
Median
Minimum
Maximum
Range
Variance
Standard Deviation
Percentiles
32.5 Trend Tests

Test:

Period Change
Percentage Change
Moving Average
32.6 Error Tests

Test:

Missing Input
Invalid Numeric Input
Division by Zero
Invalid Unit
Unknown Operation
Invalid Dataset
32.7 Reproducibility

The same:

Inputs
+
Formula Version
+
Rule Version

should produce the same deterministic result.

32.8 P-102 Test

The P-102 workflow was tested with:

Actual = 42 bar
Reference = 40 bar

Expected:

Absolute Deviation = +2 bar
Percentage Deviation = 5%
Status = ENGINEERING_REVIEW
Verification = VERIFIED
33. Technology Stack
Frontend
React
Vite
JavaScript
TypeScript where applicable
HTML
CSS
Backend
Python
FastAPI
Pydantic
SQLAlchemy
Uvicorn
AI
Open-weight LLMs
Ollama
Agentic AI
RAG
Vector Database
Qdrant
Database
SQLite
SQLAlchemy
Data Processing
Pandas
NumPy
OpenPyXL
CSV
XLSX
Document Processing
PDF processing
OCR
Text extraction
Document parsing
Development
Git
GitHub
VS Code
34. Installation
34.1 Prerequisites

Install:

Python 3.12+
Node.js
npm
Git
Ollama
34.2 Clone Repository
git clone https://github.com/riddhimankar-dev/Sovereign_On_Premise_Agentic_AI_Workbench.git

Enter the project:

cd Sovereign_On_Premise_Agentic_AI_Workbench
34.3 Backend Environment

Open a terminal:

cd backend

Activate the environment:

.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt
34.4 Frontend Dependencies

Open another terminal:

cd "Replicate Existing Design"

Install:

npm install
35. How to Run
35.1 Start Backend
cd "C:\Users\riddh\OneDrive\Desktop\sih_117\Smart_India_Hackathon_Sovereign_On_Premise_Agentic_AI_Workbench\backend"

Activate environment:

.venv\Scripts\activate

Start FastAPI:

python -m uvicorn app.main:app --reload

Backend:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs
35.2 Start Frontend

Open another terminal:

cd "C:\Users\riddh\OneDrive\Desktop\sih_117\Smart_India_Hackathon_Sovereign_On_Premise_Agentic_AI_Workbench\Replicate Existing Design"

Run:

npm run dev -- --port 5173

Open:

http://localhost:5173/
35.3 Ollama

Check installed models:

ollama list

The selected open-weight model should be available locally before using the full local-LLM workflow.

36. Current Implementation Status
🟢 Implemented
Core Platform
Agent architecture
Planner
Executor
Orchestrator
Agent state
Local LLM integration foundation
Ollama integration
Model routing
RAG pipeline
Qdrant vector store
Document parsing
OCR infrastructure
Embeddings
Keyword search
Asset lookup
Work-order lookup
Document search
Document reader
Data analysis
Code execution
Coding agent
Document generation
Approval workflow
FastAPI backend
React/Vite frontend
🟢 Calculation Engine Implemented
Dedicated calculation subsystem
Structured calculation models
Deterministic arithmetic
Addition
Subtraction
Multiplication
Division
Ratio
Absolute deviation
Percentage deviation
Percentage change
Mean
Median
Statistics
Trend calculations
Moving average
Unit validation
Unit conversion architecture
Threshold/rule evaluation
Verification
Calculation IDs
Trace IDs
Calculation storage
Provenance
Agent integration
Calculator tool integration
Calculation API
CSV/XLSX support
P-102 end-to-end calculation workflow
🟡 Being Expanded




39. Team Contribution / Calculation Engine Contribution
Calculation Engine Contribution

The major contribution of the Calculation Engine work is the introduction of a deterministic, verifiable and traceable engineering computation layer inside the agentic AI architecture.

Key Contributions
1. Deterministic Calculations

The system no longer relies solely on the LLM for numerical calculations.

2. Structured Calculation Requests

Natural-language calculation intents can be converted into structured operations.

3. Formula Registry

Calculations are organized through a controlled registry.

4. Unit Validation

Engineering values can be validated and normalized.

5. Rules Engine

Mathematical calculations are separated from engineering decision rules.

6. Statistical Analysis

The system supports deterministic statistical operations.

7. Time-Series Analysis

The system supports historical changes and moving averages.

8. Verification

Calculation outputs can be independently checked.

9. Traceability

Each calculation can have:

Calculation ID
Trace ID
Formula
Inputs
Units
Sources
Rules
Result
Verification
10. Petroleum Engineering Expansion

The architecture has been designed to support a broader petroleum/refinery calculation registry.

11. Agent Integration

The Calculation Engine is exposed through the agent tool layer.

12. P-102 Demonstration

The complete:

Retrieve
→ Calculate
→ Verify
→ Explain

workflow has been demonstrated for P-102 pressure analysis.

40. Demo Workflow

A complete demo can be presented as follows.

Demo 1 — Industrial Question

User asks:

"What is the pressure of P-102?"

System:

Chat
 ↓
Agent
 ↓
RAG
 ↓
P-102 inspection data
 ↓
Answer
Demo 2 — Engineering Calculation

User asks:

"Is P-102 above its approved pressure limit?"

System:

Retrieve actual = 42 bar
Retrieve limit = 40 bar
          ↓
Calculation Engine
          ↓
Deviation = +2 bar
          ↓
Percentage = +5%
          ↓
Rule Evaluation
          ↓
ENGINEERING_REVIEW
          ↓
Verification
          ↓
LLM Explanation
Demo 3 — Historical Trend

User asks:

"Show the pressure trend for P-102."

System:

Historical Documents
       ↓
RAG
       ↓
Structured Time Series
       ↓
Trend Engine
       ↓
Period Changes
       ↓
Moving Average
       ↓
Visualization
Demo 4 — Statistics

User asks:

"What is the average pressure for P-102?"

System:

Historical Dataset
       ↓
Statistics Engine
       ↓
Mean
       ↓
Verification
       ↓
Answer
Demo 5 — Spreadsheet

User uploads:

production_data.xlsx

User asks:

"Calculate the average production and percentage change between two periods."

System:

XLSX
 ↓
Parser
 ↓
Structured Dataset
 ↓
Calculation Engine
 ↓
Statistics
 ↓
Percentage Change
 ↓
Trace
 ↓
Verified Result
41. Limitations

The current implementation has several limitations.

41.1 Petroleum Registry Expansion

Not every petroleum-specific formula is currently implemented as a production-ready registry entry.

The architecture supports expansion, but each new engineering calculation requires:

Formula validation
Unit definitions
Input validation
Test cases
Engineering reference
Versioning
41.2 Plant-Specific Limits

The system must not hard-code plant-specific safety limits unless they are explicitly authoritative and versioned.

Limits should come from:

SOP
Manual
Approved Engineering Rule
Configuration
Authoritative RAG Evidence
41.3 Data Quality

Calculation quality depends on input quality.

Incorrect or outdated sensor/document data can produce incorrect engineering results even when the mathematical calculation is correct.

41.4 LLM Limitations

LLMs can still:

Misunderstand ambiguous questions
Select an inappropriate tool
Misinterpret context
Generate incorrect explanations

This is why deterministic calculations and verification are essential.

41.5 OCR Limitations

OCR may produce errors when documents contain:

Poor image quality
Handwritten information
Complex tables
Engineering symbols
Low-resolution scans

OCR-derived values should be validated when used for important calculations.

41.6 Forecasting

Trend analysis does not automatically constitute forecasting.

A dedicated forecasting model is required for predictive applications.

41.7 Engineering Decision Making

The system is an AI-assisted engineering workbench.

It should not independently replace qualified engineers or approved industrial procedures.

42. Engineering Safety Principles

Safety is a core design requirement.

42.1 Never Invent Safety Limits

The AI must not generate a safety limit from its own knowledge.

Correct:

RAG / Approved Source
        ↓
Safety / Operating Limit
        ↓
Calculation Engine

Incorrect:

LLM
 ↓
Invented Limit
42.2 Never Guess Missing Inputs

If a required input is missing:

STOP
 ↓
Report Missing Input

Do not assume:

0

or any other arbitrary value.

42.3 Never Guess Units

If units are unknown or incompatible:

Reject / Request Clarification
42.4 Deterministic Results Are Authoritative

When an LLM-generated numerical answer differs from the deterministic Calculation Engine:

Calculation Engine Result
=
Authoritative Calculation Result

The mismatch should be surfaced rather than hidden.

42.5 Rules Must Be Versioned

Every engineering decision rule should have:

Rule ID
Authority
Version
Effective Context
42.6 Formulas Must Be Controlled

Only approved formulas should be available to the Calculation Engine.

The system should not execute arbitrary LLM-generated formulas without validation.

42.7 Evidence Must Be Traceable

Important engineering values should have a source reference wherever possible.

42.8 Forecasts Must Be Clearly Identified

A forecast must never be presented as an observed historical measurement.

42.9 Human Approval for Sensitive Actions

AI recommendations should go through human review when required.

42.10 No Unsupported Safety Claims

The AI should not make statements such as:

"The equipment is definitely safe."

unless such a conclusion is explicitly supported by an approved engineering workflow.

Instead, the system should report measurable facts and applicable rules.

🔄 Final System Philosophy

The core philosophy of the project is:

             ┌─────────────────────┐
             │      UNDERSTAND     │
             └──────────┬──────────┘
                        ↓
             ┌─────────────────────┐
             │       RETRIEVE      │
             └──────────┬──────────┘
                        ↓
             ┌─────────────────────┐
             │      CALCULATE      │
             └──────────┬──────────┘
                        ↓
             ┌─────────────────────┐
             │       VERIFY        │
             └──────────┬──────────┘
                        ↓
             ┌─────────────────────┐
             │       EXPLAIN       │
             └──────────┬──────────┘
                        ↓
             ┌─────────────────────┐
             │       APPROVE       │
             └──────────┬──────────┘
                        ↓
             ┌─────────────────────┐
             │       DELIVER       │
             └─────────────────────┘

The system combines the flexibility of AI with the reliability of deterministic engineering software.

🏆 Key Innovation

The key innovation is not simply adding an LLM to an industrial application.

The platform creates a controlled ecosystem where:

Open-Weight LLM
        +
Agentic Planning
        +
RAG
        +
Industrial Documents
        +
Deterministic Calculation Engine
        +
Engineering Rules
        +
Verification
        +
Traceability
        +
Human Approval
        =
Sovereign Industrial AI Workbench

This approach is particularly important for confidential industrial environments where AI systems must be:

Reliable
Explainable
Auditable
Secure
Deterministic where required
Grounded in authoritative information
Deployable on-premise
📌 Summary

The Sovereign On-Premise Agentic AI Workbench provides an integrated platform for confidential industrial AI.

The existing project provides the foundation for:

Agentic AI
Local LLMs
RAG
Qdrant
OCR
Document intelligence
Data analysis
Code execution
Asset lookup
Work-order lookup
Document generation
Approval workflows
Industrial knowledge management

The newly enhanced Calculation Engine adds:

Deterministic engineering calculations
Structured calculation requests
Formula registry
Unit validation
Unit conversion
Percentage deviation
Absolute deviation
Percentage change
Statistics
Trends
Moving averages
Threshold rules
Verification
Provenance
Calculation traces
Calculation IDs
Structured APIs
Spreadsheet support
Agent integration
P-102 end-to-end engineering workflow
#  Installation

## Prerequisites

Before running the project, make sure the following software is installed:

- Python 3.12+
- Node.js
- npm
- Git
- Ollama

Check the installations using:

```bash
python --version
node --version
npm --version
git --version
ollama --version

