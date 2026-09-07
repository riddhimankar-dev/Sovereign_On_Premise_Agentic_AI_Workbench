Sovereign On-Premise Agentic AI Workbench

Using Open-Weight Multimodal LLMs for Confidential Industrial Work

This project is developed for Smart India Hackathon 2026 – SIH26117 under the Smart Automation theme.

The Sovereign On-Premise Agentic AI Workbench is an AI-powered platform designed for confidential industrial environments such as refineries, oil & gas facilities, manufacturing plants, process industries, and engineering organizations.

The platform combines local/open-weight AI with Retrieval-Augmented Generation (RAG), deterministic engineering calculations, verification, provenance, and human approval.

1. Problem Statement

Industrial organizations maintain large volumes of confidential technical information, including:

Engineering manuals

Standard Operating Procedures (SOPs)

Inspection reports

Maintenance records

Asset registers

Equipment specifications

Historical operating data

Engineering drawings

Technical reports

Spreadsheets

Work orders

Process measurements

Safety procedures

Using cloud-based AI systems for such information can create concerns related to:

Data privacy

Data sovereignty

Confidentiality

Intellectual property

Industrial cybersecurity

Regulatory compliance

Unauthorized access

AI hallucination

Incorrect engineering calculations

Lack of traceability

Lack of auditability

The proposed system provides a controlled AI workbench that can operate inside an organization's infrastructure.

2. Project Objective

The objective is to build a sovereign industrial AI workbench capable of assisting engineers with confidential industrial tasks while maintaining control over:

Data

AI inference

Tools

Engineering calculations

Rules

Results

Provenance

Generated artifacts

The platform combines:

Agentic AI

Open-weight LLMs

Local LLM inference

Retrieval-Augmented Generation

Industrial document intelligence

OCR infrastructure

Vector search

Deterministic engineering calculations

Data analysis

Controlled code execution

Document generation

Verification

Provenance

Human approval

Core philosophy:

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

3. Complete System Overview

Instead of acting only as a chatbot, the platform acts as an AI workbench capable of interacting with:

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

A typical industrial workflow is:

User Question
      ↓
Frontend
      ↓
FastAPI Backend
      ↓
Agent Orchestrator
      ↓
Planner
      ↓
Knowledge / Data Retrieval
      ↓
Structured Calculation Request
      ↓
Deterministic Calculation Engine
      ↓
Verification
      ↓
Trace / Provenance
      ↓
Local LLM Explanation
      ↓
User / Human Approval / Artifact

4. Why Agentic AI?

A conventional chatbot generally follows:

Question
   ↓
LLM
   ↓
Answer

This project follows a controlled agentic workflow:

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

This architecture separates language understanding from deterministic engineering computation.

The core principle is:

The LLM understands and explains. The deterministic Calculation Engine calculates.

5. Existing Project Foundation

The project already contains an industrial agentic AI foundation.

5.1 Agent Architecture

backend/app/agents/
├── planner.py
├── executor.py
├── orchestrator.py
├── state.py
└── verifier.py

These components provide:

Planning

Tool execution

Orchestration

Agent state

Verification-oriented workflow handling

5.2 Local LLM Infrastructure

The project contains infrastructure for:

Local LLM communication

Ollama integration

Model registration

Model routing

5.3 RAG Infrastructure

The project contains components for:

Document parsing

OCR

Chunking

Embeddings

Keyword search

Vector search

Retrieval

Qdrant integration

5.4 Existing Tools

The tool layer contains:

Asset lookup

Work-order lookup

Document search

Document reader

Data analysis

Code execution

Coding agent

Document generation

Calculator

5.5 Industrial Dataset

The project contains a sovereign industrial dataset structure:

ApexPetro_Sovereign_Dataset_v3/
├── assets/
├── historical_records/
├── manuals/
├── sops/
└── templates/

Example P-102 inspection and maintenance records are used for demonstrating industrial workflows.

5.6 Existing Frontend

The web workbench supports workflows involving:

Chat

Knowledge interaction

Calculations

Data analysis

Industrial information retrieval

Document-related operations

5.7 Existing Backend

The FastAPI backend provides routes for multiple functions including:

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

Calculations

6. Major New Implementation: Calculation Engine

The major enhancement implemented in this project is the transformation of the basic calculator into a structured deterministic Calculation Engine.

The calculation subsystem is located at:

backend/app/calculation/

Current modules:

backend/app/calculation/
├── __init__.py
├── engine.py
├── errors.py
├── formulas.py
├── models.py
├── registry.py
├── rules.py
├── statistics.py
├── store.py
├── trace.py
├── trends.py
├── units.py
├── verification.py
├── spreadsheet.py
├── petroleum.py
├── equipment.py
└── multi_parameter.py

7. Calculation Engine Architecture

The Calculation Engine follows:

Structured Request
       ↓
Input Validation
       ↓
Unit Validation / Normalization
       ↓
Formula / Operation Selection
       ↓
Deterministic Execution
       ↓
Rule Evaluation
       ↓
Result Validation
       ↓
Independent Verification
       ↓
Trace Creation
       ↓
Structured Response

The engine does not rely on the LLM to directly calculate engineering results.

8. Calculation Engine Responsibilities

The Calculation Engine handles:

Input validation

Missing-input detection

Numeric validation

Unit validation

Unit normalization

Formula selection

Deterministic execution

Rule evaluation

Result validation

Verification

Trace generation

Provenance recording

Calculation storage

Missing values are not silently converted to zero.

For example:

Required input missing
        ↓
Calculation Error

instead of:

Missing input
      ↓
Assume 0

9. Supported Calculation Operations

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

The architecture also contains petroleum, equipment, and multi-parameter calculation modules for expansion.

10. Basic Arithmetic

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

Example:

10 / 0

returns a structured calculation error.

Ratio

A / B

Ratios are returned as structured calculation results.

11. Percentage and Deviation Calculations

Absolute Deviation

Actual - Reference

Example:

42 - 40 = +2

Percentage Deviation

((Actual - Reference) / Reference) × 100

Example:

Actual = 42
Reference = 40

((42 - 40) / 40) × 100
= 5%

Percentage Change

((Current - Previous) / Previous) × 100

Example:

Previous = 34 bar
Current = 42 bar

((42 - 34) / 34) × 100
= 23.53%

12. Formula Registry

The Calculation Engine uses a controlled registry rather than executing arbitrary formulas supplied by an LLM.

The registry stores calculation metadata such as:

Operation ID

Name

Description

Required inputs

Formula

Output

Unit

Authority

Version

Enabled/disabled state

This provides a controlled calculation vocabulary.

13. Unit Engine

The Unit Engine validates and normalizes engineering units.

Responsibilities include:

Unit validation

Compatibility checking

Unit conversion

Normalization

Preservation of original units

Preservation of normalized units

Example:

1000 kPa
    ↓
10 bar

An incompatible operation such as:

40 bar + 100 °C

must be rejected.

The engine must never guess an engineering unit conversion.

14. Rules Engine

The Formula Engine and Rules Engine are separate.

Formula

Performs mathematical computation.

42 - 40 = 2 bar

Rule

Determines an engineering status.

Actual Pressure > Approved Limit

Example:

Actual = 42 bar
Limit  = 40 bar

42 > 40

Status:
ENGINEERING_REVIEW

A rule can contain:

Rule ID

Rule name

Parameter

Authority

Version

Unit

Limit

Condition

Actual value

Deviation

Status

15. P-102 Demonstration Rule

A prototype P-102 pressure rule is implemented to demonstrate the complete Calculation Engine workflow.

Rule ID:
P102-PRESSURE-LIMIT

Parameter:
Pressure

Limit:
40 bar

Version:
1.0

For:

Actual pressure = 42 bar
Reference limit = 40 bar

the engine produces:

Absolute deviation = +2 bar
Percentage deviation = +5%
Status = ENGINEERING_REVIEW
Verification = VERIFIED

Important: The 40 bar value is a prototype/demo rule used to demonstrate the architecture. It must not be interpreted as an actual MRPL safety limit unless supplied by an authoritative, approved, and versioned source.

16. Statistics Engine

The Calculation Engine supports deterministic statistical analysis.

Supported operations include:

Count

Sum

Mean

Median

Minimum

Maximum

Range

Variance

Standard deviation

Percentiles

Example:

10
20
30

Mean:

(10 + 20 + 30) / 3
= 20

Statistical outputs can preserve dataset scope including:

Dataset reference

Number of rows

Parameter

Asset

Unit

Time range where available

17. Trend Engine

The Trend Engine supports historical analysis.

Supported capabilities include:

Period-to-period changes

Percentage changes

Rolling/moving averages

Example:

2025 = 34 bar
2026 = 42 bar

Absolute change:

42 - 34
= +8 bar

Percentage change:

((42 - 34) / 34) × 100
= 23.53%

Forecasting Principle

Trend analysis is not automatically treated as forecasting.

Forecasting should be a separate capability with its own:

Model

Validation

Uncertainty handling

Output labeling

18. Multi-Parameter Engineering Analysis

The project contains support for multi-parameter engineering analysis.

The system is designed not to hide multiple engineering measurements behind an unexplained single score.

A parameter-level result can contain:

Parameter
Actual
Limit
Deviation
Percentage deviation
Rule result
Source

This makes engineering analysis more transparent.

19. Petroleum and Equipment Calculation Expansion

The calculation architecture includes:

petroleum.py
equipment.py
multi_parameter.py

These provide a foundation for petroleum/refinery and equipment-oriented calculations.

Each additional engineering formula should go through:

Formula validation

Unit definition

Input validation

Engineering reference

Test cases

Versioning

No engineering formula should be added merely because an LLM generated it.

20. Spreadsheet Support

The Calculation Engine supports structured spreadsheet inputs.

Currently supported formats:

CSV
XLSX

Workflow:

CSV / Excel
      ↓
File Parsing
      ↓
Sheet / Column Processing
      ↓
Type Validation
      ↓
Missing Value Validation
      ↓
Structured Dataset
      ↓
Calculation Engine

Example:

period | value | unit
2024   | 34    | bar
2025   | 37    | bar
2026   | 42    | bar

Possible requests:

Calculate the average pressure.

or:

Calculate the percentage change between 2025 and 2026.

21. Spreadsheet Validation

Spreadsheet processing validates:

File existence

File format

Headers

Numeric values

Missing values

Finite numeric values

Dataset structure

Units where available

Source references

CSV and XLSX processing were directly tested.

Example test dataset:

period,value,unit
2024,34,bar
2025,37,bar
2026,42,bar

The statistics engine produced:

Count = 3
Sum = 113
Mean = 37.6667
Median = 37
Minimum = 34
Maximum = 42
Range = 8
Variance ≈ 16.3333
Standard Deviation ≈ 4.0415
P25 = 35.5
P50 = 37
P75 = 39.5

The calculation result was successfully verified.

22. Calculator Tool

The existing calculator tool was enhanced to act as a deterministic wrapper around the Calculation Engine.

Agent
  ↓
Calculator Tool
  ↓
Calculation Engine
  ↓
Verification
  ↓
Structured Result

This prevents the agent from performing engineering calculations solely through uncontrolled LLM reasoning.

23. Agent Integration

The planner was enhanced to detect calculation-related natural-language requests.

Workflow:

User Question
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

The planner can recognize calculation patterns including engineering/petroleum-related requests supported by the implemented modules.

If required inputs are missing, the system should retrieve the required information or report that the input is unavailable rather than inventing a value.

24. Agent Architecture

backend/app/agents/
├── planner.py
├── executor.py
├── orchestrator.py
├── state.py
└── verifier.py

Planner

Responsible for:

Intent detection

Task planning

Tool selection

Calculation detection

Required data identification

Executor

Executes planned tool operations.

Orchestrator

Coordinates:

User request

Agent planning

Tool execution

Retrieved evidence

Calculation results

Verification

Final response generation

The current orchestrator also communicates with the local Ollama service.

State

Maintains information throughout the agent workflow.

Verifier

Provides verification-oriented workflow checking.

25. Local LLM / Ollama

The platform is designed around local open-weight LLM inference.

Ollama provides the local inference runtime.

The LLM is responsible for:

Natural-language understanding

Intent interpretation

Planning assistance

Tool selection

Explanation

Summarization

Response generation

The LLM should not be the authoritative source for:

Engineering calculations

Plant-specific limits

Approved formulas

Safety limits

Final numerical results

Instead:

LLM
 ↓
Structured Request
 ↓
Deterministic Engine
 ↓
Verified Result
 ↓
LLM Explanation

26. RAG / Qdrant

The project contains a RAG subsystem for retrieving confidential industrial knowledge.

backend/app/rag/
├── chunker.py
├── embeddings.py
├── keyword_search.py
├── ocr.py
├── parser.py
├── retriever.py
└── vector_store.py

RAG workflow:

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

RAG can provide:

Equipment information

Historical measurements

Maintenance information

SOP information

Engineering references

Source evidence

The retrieved values can then be passed into the deterministic Calculation Engine.

27. RAG and Local LLM Current Status

The RAG infrastructure is present in the project.

Full RAG + local LLM synthesis depends on the configured Ollama model being installed and available locally.

For example, if the configured model is:

qwen2.5:3b

check:

ollama list

If required:

ollama pull qwen2.5:3b

Test:

ollama run qwen2.5:3b

A missing Ollama model is an environment/configuration issue and does not indicate failure of the deterministic Calculation Engine.

The Calculation Engine can be tested independently through direct engine tests and its APIs.

28. OCR / Document Processing

Industrial information can exist in scanned documents.

The project contains infrastructure for:

PDF parsing

OCR

Text extraction

Chunking

Metadata processing

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
Structured Input
        ↓
Calculation Engine

OCR-derived engineering values should be validated before being used for important decisions.

29. Tool Layer

The tool layer provides controlled capabilities to agents.

backend/app/tools/
├── asset_lookup.py
├── base.py
├── calculator.py
├── code_executor.py
├── coding_agent.py
├── data_analysis.py
├── document_generation_tool.py
├── document_reader.py
├── document_search.py
└── work_order_lookup.py

Tools include:

Asset Lookup

Retrieves asset-related information.

Work Order Lookup

Retrieves maintenance and work-order information.

Document Search

Searches the industrial knowledge base.

Document Reader

Reads document information.

Calculator

Provides deterministic access to the Calculation Engine.

Data Analysis

Supports structured data analysis.

Code Executor

Provides controlled analytical/code execution.

Coding Agent

Supports programming-related tasks.

Document Generation

Generates structured industrial artifacts.

30. Code Execution

The project contains controlled code-execution capabilities for analytical workflows.

Potential use cases include:

Python execution

Dataset processing

Numerical analysis

Data transformation

Analytical workflows

In a sovereign industrial deployment, code execution must remain isolated and controlled.

The system should not provide unrestricted:

Host filesystem access

Network access

System-level access

without explicit authorization and isolation.

31. Document Generation

The workbench contains document-generation capabilities.

Potential artifacts include:

DOCX

XLSX

PPTX

PDF

Workflow:

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

Calculation IDs can be included in generated artifacts to improve traceability.

32. Approval Workflow

Industrial AI systems require human oversight for sensitive decisions.

The intended workflow is:

AI Recommendation
       ↓
Verification
       ↓
Human Review
       ↓
Approval
       ↓
Action / Artifact

The AI system is intended to assist engineers rather than replace qualified engineering responsibility.

33. Frontend

Frontend location:

Replicate Existing Design/

Technology:

React

Vite

TypeScript / JavaScript

HTML

CSS

Development URL:

http://localhost:5173/

34. Backend

Backend location:

backend/

Technology:

Python

FastAPI

Pydantic

SQLAlchemy

Uvicorn

Development URL:

http://127.0.0.1:8000

Swagger documentation:

http://127.0.0.1:8000/docs

35. Calculation APIs

The Calculation Engine API is available under:

/api/calculations

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

36. Calculation Request Model

The Calculation Engine accepts structured requests containing:

operation
inputs
dataset
context

An input can contain:

value
unit
source
source_ref
timestamp
asset_id
dataset_ref

This allows calculations to retain engineering context and provenance.

Example conceptual request:

{
  "operation": "percentage_deviation",
  "inputs": {
    "actual": {
      "value": 42,
      "unit": "bar"
    },
    "reference": {
      "value": 40,
      "unit": "bar"
    }
  }
}

37. Verification

Verification occurs after deterministic execution.

The verifier checks aspects such as:

Inputs
   ↓
Units
   ↓
Formula
   ↓
Execution
   ↓
Result
   ↓
Rule
   ↓
Trace

A successful calculation can return:

verification_status:
VERIFIED

If a verification problem occurs, it should be surfaced rather than silently accepting the result.

38. Calculation Trace / Provenance

Calculations can be assigned unique identifiers.

Example:

Calculation ID:
CAL-35B858B5ED30

Trace ID:
TRACE-3CAB137224A9

A calculation trace may contain:

Input values

Original units

Normalized values

Source references

Asset ID

Dataset reference

Timestamp

Formula

Formula version

Rule

Rule version

Engine version

Result

Verification status

Warnings

Errors

Context

This allows an engineer to answer:

Where did this number come from?

Traceability:

Source
  ↓
Input
  ↓
Normalization
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

39. P-102 End-to-End Demonstration

The P-102 workflow demonstrates the complete deterministic calculation architecture.

Step 1 — User Question

Example:

"Is P-102 operating above its approved pressure limit?"

Step 2 — Retrieved/Provided Inputs

Actual Pressure = 42 bar
Reference Limit = 40 bar

Step 3 — Structured Calculation

Operation:
percentage_deviation

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

42 > 40

Result:

ENGINEERING_REVIEW

Step 6 — Verification

VERIFIED

Step 7 — Trace

Example:

Calculation ID:
CAL-35B858B5ED30

Trace ID:
TRACE-3CAB137224A9

Step 8 — Final Explanation

The LLM can explain the verified result:

P-102 is operating 2 bar above the
40 bar reference limit.

This corresponds to a 5% deviation.

The deterministic Calculation Engine
verified the calculation and classified
the condition as ENGINEERING_REVIEW.

The 40 bar value is a demonstration/prototype rule and is not claimed to be an actual MRPL safety limit.

40. Spreadsheet Test

The Calculation Engine was directly tested using:

period,value,unit
2024,34,bar
2025,37,bar
2026,42,bar

Results included:

Count = 3
Sum = 113
Mean = 37.6667
Median = 37
Minimum = 34
Maximum = 42
Range = 8
Variance ≈ 16.3333
Standard Deviation ≈ 4.0415
P25 = 35.5
P50 = 37
P75 = 39.5

The calculation result returned:

Status = NORMAL
Verification = VERIFIED

for the demonstrated statistics workflow.

41. Complete Architecture

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
                         │  Agent Orchestrator │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
              ┌──────────┐   ┌────────────┐   ┌──────────┐
              │ Planner  │   │ Local LLM  │   │   RAG    │
              │          │   │  Ollama    │   │ Qdrant   │
              └──────────┘   └────────────┘   └────┬─────┘
                                                   │
                         ┌─────────────────────────┼───────────────┐
                         │                         │               │
                         ▼                         ▼               ▼
                 ┌──────────────┐        ┌─────────────┐   ┌────────────┐
                 │ Calculation  │        │ Data        │   │ Document   │
                 │ Engine       │        │ Analysis    │   │ Processing │
                 └──────┬───────┘        └─────────────┘   └────────────┘
                        │
               ┌────────┼────────┐
               ▼        ▼        ▼
           ┌────────┐ ┌──────┐ ┌──────┐
           │Formula │ │Units │ │Rules │
           │Engine  │ │Engine│ │Engine│
           └────────┘ └──────┘ └──────┘
               │        │        │
               └────────┼────────┘
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

42. Project Structure

Smart_India_Hackathon_Sovereign_On_Premise_Agentic_AI_Workbench/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── executor.py
│   │   │   ├── orchestrator.py
│   │   │   ├── planner.py
│   │   │   ├── state.py
│   │   │   └── verifier.py
│   │   │
│   │   ├── api/
│   │   │   └── routes/
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
│   │   │   ├── spreadsheet.py
│   │   │   ├── petroleum.py
│   │   │   ├── equipment.py
│   │   │   └── multi_parameter.py
│   │   │
│   │   ├── core/
│   │   ├── db/
│   │   ├── llm/
│   │   │   ├── model_registry.py
│   │   │   ├── ollama_client.py
│   │   │   └── router.py
│   │   ├── rag/
│   │   │   ├── chunker.py
│   │   │   ├── embeddings.py
│   │   │   ├── keyword_search.py
│   │   │   ├── ocr.py
│   │   │   ├── parser.py
│   │   │   ├── retriever.py
│   │   │   └── vector_store.py
│   │   ├── services/
│   │   └── tools/
│   │
│   ├── data/
│   ├── scripts/
│   ├── tests/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
│
├── ApexPetro_Sovereign_Dataset_v3/
│
├── Replicate Existing Design/
│
├── docs/
│
├── .gitignore
└── README.md

43. API Categories

Main backend API groups include:

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

Swagger:

http://127.0.0.1:8000/docs

44. Error Handling

The Calculation Engine follows explicit error handling.

Missing Input

Example:

Actual pressure is missing.

Result:

ERROR:
Required input is missing.

The engine does not assume zero.

Invalid Numeric Input

Example:

Pressure = "abc"

Result:

Calculation validation error

Division by Zero

10 / 0

Result:

Division by zero is not allowed.

Incompatible Units

40 bar + 100 °C

Result:

Incompatible units.

Unknown Calculation

Unsupported operations produce:

Unknown calculation operation.

Invalid Formula

The engine must reject invalid formulas instead of executing arbitrary expressions.

Stale/Invalid Rule

Rule verification should fail when a rule is not valid for the required context.

45. Testing

Testing is essential for engineering reliability.

45.1 Formula Tests

Addition

Subtraction

Multiplication

Division

Ratio

Absolute deviation

Percentage deviation

Percentage change

45.2 Unit Tests

Valid conversion

Invalid conversion

Compatible units

Incompatible units

45.3 Rule Tests

Below limit

At limit

Above limit

45.4 Statistical Tests

Mean

Median

Minimum

Maximum

Range

Variance

Standard deviation

Percentiles

45.5 Trend Tests

Period change

Percentage change

Moving average

45.6 Error Tests

Missing input

Invalid numeric input

Division by zero

Invalid unit

Unknown operation

Invalid dataset

45.7 Reproducibility

The same:

Inputs
+
Formula Version
+
Rule Version

should produce the same deterministic result.

46. Current Implementation Status

🟢 Implemented

Core Platform

Agent architecture

Planner

Executor

Orchestrator

Agent state

FastAPI backend

React/Vite frontend

Local LLM integration foundation

Ollama communication

Tool layer

Data analysis infrastructure

Document processing infrastructure

RAG/Qdrant infrastructure

Asset lookup

Work-order lookup

Document search

Document reader

Code execution infrastructure

Coding agent

Document generation

Approval workflow

Calculation Engine

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

Trend analysis

Moving averages

Unit validation

Unit conversion architecture

Threshold evaluation

Engineering rules

Verification

Calculation IDs

Trace IDs

Calculation storage

Provenance

Agent integration

Calculator tool integration

Calculation APIs

CSV support

XLSX support

Petroleum calculation architecture

Equipment calculation architecture

Multi-parameter analysis architecture

P-102 demonstration workflow

🟡 Environment / Integration Dependent

Full local LLM synthesis depends on the selected Ollama model being installed.

Full RAG + LLM end-to-end operation depends on local model availability and configured knowledge-base data.

🔵 Future Expansion

Additional petroleum-specific formulas

Expanded engineering calculation registry

More extensive automated tests

Production-grade security hardening

Additional spreadsheet formats

Dedicated forecasting models

Expanded industrial datasets

More advanced multimodal workflows

47. Security and Sovereignty

Security and sovereignty are fundamental design goals.

47.1 On-Premise Processing

Sensitive information can remain inside the organization's controlled environment.

47.2 Local LLM

LLM inference can be performed locally using Ollama.

47.3 Confidential Knowledge Base

Industrial documents and vector data can remain in local infrastructure.

47.4 Controlled Tool Access

Agents should only have access to approved tools.

47.5 Restricted File Access

Agents should not have unrestricted access to the host machine.

47.6 Restricted Network Access

Agents should not have unrestricted outbound network access in confidential deployments.

47.7 Permission-Aware Access

Access should consider:

User
Role
Project
Dataset
Document
Classification
Permission

47.8 Auditability

Important operations and calculations should be traceable.

48. Engineering Safety Principles

Never Invent Safety Limits

Correct:

Approved Source
      ↓
Engineering Rule
      ↓
Calculation Engine

Incorrect:

LLM
 ↓
Invented Safety Limit

Never Guess Missing Inputs

If a required input is missing:

STOP
 ↓
Report Missing Input

Do not assume zero or another arbitrary value.

Never Guess Units

Unknown or incompatible units should be rejected or clarified.

Deterministic Results

When an LLM-generated numerical answer conflicts with the Calculation Engine:

Calculation Engine
       ↓
Verified Result

should be treated as the authoritative numerical computation.

The mismatch should be surfaced rather than hidden.

Version Engineering Rules

Rules should contain:

Rule ID

Authority

Version

Applicable context

Control Formulas

Only approved formulas should be available to the deterministic engine.

Trace Evidence

Important engineering values should retain source references whenever possible.

Forecasting

Forecasts must be explicitly labeled and should not be presented as historical observations.

Human Approval

Sensitive engineering actions should remain subject to qualified human review.

No Unsupported Safety Claims

The AI should not state that equipment is definitely safe unless such a conclusion is explicitly supported by an approved engineering workflow.

49. Team Contribution — Calculation Engine

The major contribution of the Calculation Engine work is the introduction of a:

Deterministic, verifiable and traceable engineering computation layer inside the agentic AI architecture.

Key contributions:

Deterministic calculations

Structured calculation requests

Formula registry

Unit validation and normalization

Engineering Rules Engine

Statistical analysis

Time-series analysis

Verification

Calculation traceability

Petroleum/equipment calculation architecture

Spreadsheet integration

Agent integration

Calculation APIs

P-102 end-to-end demonstration

50. Demo Workflow

Demo 1 — Industrial Question

User
 ↓
Chat
 ↓
Agent
 ↓
Knowledge Retrieval
 ↓
Industrial Evidence
 ↓
Answer

Demo 2 — Engineering Calculation

Question:

Is P-102 above its approved pressure limit?

Workflow:

Actual = 42 bar
Limit  = 40 bar
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

Historical Data
      ↓
Structured Time Series
      ↓
Trend Engine
      ↓
Period Changes
      ↓
Moving Average

Demo 4 — Statistics

Historical Dataset
      ↓
Statistics Engine
      ↓
Mean / Median / Statistics
      ↓
Verification
      ↓
Answer

Demo 5 — Spreadsheet

production_data.xlsx
      ↓
Spreadsheet Parser
      ↓
Structured Dataset
      ↓
Calculation Engine
      ↓
Statistics / Percentage Change
      ↓
Trace
      ↓
Verified Result

51. Limitations

51.1 Petroleum Formula Coverage

Not every petroleum-specific calculation is currently implemented as a production-ready registry entry.

Each additional formula requires:

Formula
 ↓
Engineering Validation
 ↓
Units
 ↓
Input Validation
 ↓
Test Cases
 ↓
Authority
 ↓
Version

51.2 Plant-Specific Limits

Plant-specific limits must come from authoritative sources.

The system should not arbitrarily hard-code safety limits.

51.3 Data Quality

Correct mathematics cannot compensate for incorrect input data.

51.4 LLM Limitations

LLMs can still:

Misunderstand ambiguous questions

Select an inappropriate tool

Misinterpret context

Generate incorrect explanations

51.5 OCR Limitations

OCR may make mistakes with:

Poor image quality

Handwriting

Complex tables

Engineering symbols

Low-resolution scans

51.6 Forecasting

Trend analysis is not forecasting.

A dedicated forecasting model is required.

51.7 Engineering Responsibility

The platform is an AI-assisted engineering workbench.

It does not replace:

Qualified engineers

Approved SOPs

Safety procedures

Engineering authority

52. Key Innovation

The key innovation is not simply adding an LLM to an industrial application.

The platform creates a controlled ecosystem:

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

This architecture combines:

AI flexibility

Engineering determinism

Evidence grounding

Verification

Auditability

Data sovereignty

Human oversight

53. Final System Philosophy

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

The fundamental principle is:

AI should provide intelligence and flexibility, while deterministic software provides numerical reliability and engineering control.

54. Installation

54.1 Prerequisites

Install:

Python 3.12+

Node.js

npm

Git

Ollama

Check installations:

python --version
node --version
npm --version
git --version
ollama --version

55. Clone Repository

git clone https://github.com/riddhimankar-dev/Sovereign_On_Premise_Agentic_AI_Workbench.git

Enter the project:

cd Sovereign_On_Premise_Agentic_AI_Workbench

56. Backend Setup

cd backend

Windows:

.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

57. Frontend Setup

Open another terminal:

cd "Replicate Existing Design"

Install dependencies:

npm install

58. Running the Backend

cd "C:\Users\riddh\OneDrive\Desktop\sih_117\Smart_India_Hackathon_Sovereign_On_Premise_Agentic_AI_Workbench\backend"

.venv\Scripts\activate

python -m uvicorn app.main:app --reload

Backend:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs

59. Running the Frontend

Open another terminal:

cd "C:\Users\riddh\OneDrive\Desktop\sih_117\Smart_India_Hackathon_Sovereign_On_Premise_Agentic_AI_Workbench\Replicate Existing Design"

npm run dev -- --port 5173

Open:

http://localhost:5173/

60. Ollama Setup

Check installed models:

ollama list

If the selected model is not installed:

ollama pull qwen2.5:3b

Test:

ollama run qwen2.5:3b

The full local-LLM workflow requires the selected model to be available locally.

61. Calculation Engine Testing

The Calculation Engine can be tested independently from the LLM.

Recommended tests:

Arithmetic

Addition

Subtraction

Multiplication

Division

Ratio

Deviation

Absolute deviation

Percentage deviation

Percentage change

Units

Valid conversions

Compatible units

Incompatible units

Invalid units

Statistics

Mean

Median

Minimum

Maximum

Range

Variance

Standard deviation

Percentiles

Trends

Period change

Percentage change

Moving average

Rules

Below limit

At limit

Above limit

Errors

Missing input

Invalid numeric input

Division by zero

Invalid unit

Unknown operation

Invalid dataset

62. Example Calculation API Request

Example percentage-deviation request:

{
  "operation": "percentage_deviation",
  "inputs": {
    "actual": {
      "value": 42,
      "unit": "bar"
    },
    "reference": {
      "value": 40,
      "unit": "bar"
    }
  }
}

Expected mathematical result:

5%

A rule evaluation can additionally classify the result as:

ENGINEERING_REVIEW

when the configured rule specifies that actual pressure above the reference limit requires review.

63. Example API Response

A structured calculation response can contain:

{
  "calculation_id": "CAL-EXAMPLE",
  "operation": "percentage_deviation",
  "result": 5,
  "unit": "%",
  "formula": "((actual - reference) / reference) × 100",
  "status": "ENGINEERING_REVIEW",
  "verification_status": "VERIFIED",
  "trace_id": "TRACE-EXAMPLE"
}

Exact IDs are generated by the system for each calculation.

64. Why the Calculation Engine Matters

Industrial AI cannot safely depend only on language-model reasoning for numerical engineering work.

For example, an LLM may explain:

42 bar is above 40 bar.

But the Calculation Engine provides a deterministic computation:

42 - 40 = +2 bar

and:

((42 - 40) / 40) × 100 = 5%

It can then verify and trace the result.

This creates a separation between:

Language Intelligence
        ↓
Engineering Computation
        ↓
Verification

65. Summary

The Sovereign On-Premise Agentic AI Workbench provides a unified platform for confidential industrial AI workflows.

The existing project foundation includes:

Agentic AI

Local LLM infrastructure

Ollama

RAG

Qdrant

OCR infrastructure

Document intelligence

Data analysis

Code execution

Asset lookup

Work-order lookup

Document generation

Approval workflows

The enhanced Calculation Engine adds:

Deterministic engineering calculations

Structured calculation requests

Formula registry

Unit validation

Unit normalization

Unit conversion

Absolute deviation

Percentage deviation

Percentage change

Statistics

Trends

Moving averages

Threshold rules

Verification

Provenance

Calculation traces

Calculation IDs

Trace IDs

Structured APIs

Spreadsheet support

CSV/XLSX processing

Agent integration

Petroleum/equipment calculation architecture

Multi-parameter analysis

P-102 end-to-end demonstration

The resulting architecture provides a foundation for a sovereign industrial AI system where:

LLM
=
Understand + Plan + Explain

RAG
=
Retrieve Evidence

Calculation Engine
=
Deterministic Computation

Rules Engine
=
Engineering Decision Logic

Verification
=
Independent Checking

Trace
=
Provenance + Auditability

Human
=
Final Engineering Responsibility


License

This project is developed as part of the Smart India Hackathon 2026 project and is intended for demonstration and research purposes.
