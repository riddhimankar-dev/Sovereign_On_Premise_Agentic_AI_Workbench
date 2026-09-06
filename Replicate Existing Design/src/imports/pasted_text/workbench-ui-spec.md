============================================================
PROJECT
============================================================

Design a complete, high-fidelity, production-quality USER-FACING
web application UI for:

SOVEREIGN AI WORKBENCH

Tagline:
"Private intelligence for confidential industrial work."

This is the employee-facing interface of an on-premise,
air-gapped enterprise AI assistant used by confidential
industrial organizations.

IMPORTANT:

This is NOT an admin dashboard.

This is NOT a generic ChatGPT clone.

This is NOT a cybersecurity dashboard.

This is NOT a developer-only interface.

It is an intelligent employee workbench where an employee can:

- ask questions
- build documents
- analyze confidential files
- work with company knowledge
- execute code safely
- analyze images and scanned documents
- use different local AI models
- run multi-step agentic tasks
- review evidence
- generate real business artifacts
- approve/reject AI-generated recommendations

The application must feel like a serious enterprise product
used by engineers, inspectors, managers and technical staff
inside a refinery or industrial organization.

============================================================
1. PRIMARY USER
============================================================

Design for a technical employee.

Seed user:

Name:
Arjun Mehta

Role:
Inspection Engineer

Company:
ApexPetro Energy Limited

Facility:
Jamnagar Refinery Complex

Department:
Inspection & Integrity

The user belongs to ONLY ONE COMPANY.

IMPORTANT COMPANY ISOLATION RULE:

The user must NEVER see a company switcher.

Do NOT provide:

"Switch Company"

"Company Dropdown"

"Change Organization"

The company context is fixed automatically by authentication.

Show the company subtly in the interface:

ApexPetro Energy Limited
Jamnagar Refinery Complex

The user only has access to:

ApexPetro documents
ApexPetro knowledge
ApexPetro projects
ApexPetro agents
ApexPetro artifacts

The UI should communicate isolation through subtle security
indicators rather than a large company-selection interface.

============================================================
2. DESIGN GOAL
============================================================

The primary experience should be:

OPEN APPLICATION
        ↓
SEE CHAT / WORKBENCH
        ↓
CHOOSE WHAT YOU WANT TO DO
        ↓
ASK / BUILD / CODE / CHANGE MODEL
        ↓
UPLOAD FILES IF NEEDED
        ↓
AI PLANS TASK
        ↓
AI EXECUTES TOOLS
        ↓
USER SEES PROGRESS
        ↓
AI SHOWS ANSWER + EVIDENCE
        ↓
ARTIFACT GENERATED
        ↓
HUMAN APPROVAL IF REQUIRED

The chatbot should be the center of the entire product.

============================================================
3. VISUAL DIRECTION
============================================================

Create a premium dark enterprise interface.

Visual references in spirit:

- modern AI assistant
- enterprise command center
- engineering software
- high-end developer tools
- industrial control-room software

Do NOT copy any existing product.

The interface should feel:

- intelligent
- calm
- trustworthy
- precise
- technical
- sophisticated
- secure
- premium

Avoid:

- cyberpunk
- excessive neon
- gaming UI
- giant glowing AI graphics
- cartoon robots
- excessive gradients
- excessive glassmorphism
- crypto-style dashboards
- generic SaaS templates
- excessive rounded cards

============================================================
4. COLOR SYSTEM
============================================================

Use a dark navy foundation.

Background:
#080D18

Primary surface:
#0F1726

Secondary surface:
#141E2F

Elevated surface:
#182337

Border:
#253248

Primary text:
#F5F7FA

Secondary text:
#9AA6B5

Muted text:
#667386

Primary accent:
#8B5CF6

Secondary accent:
#14B8A6

Information:
#3B82F6

Success:
#22C55E

Warning:
#F59E0B

Critical:
#EF4444

The main interaction accent should be a sophisticated
purple/violet.

Use teal primarily for:

- LOCAL
- VERIFIED
- SECURE
- ACTIVE
- SUCCESS

Use amber for:

- NEEDS REVIEW
- WARNING
- APPROVAL REQUIRED

Use red only for:

- critical
- blocked
- failed

Do not use bright colors everywhere.

============================================================
5. TYPOGRAPHY
============================================================

Use:

Inter

or a similar highly readable modern sans-serif.

Typography should be compact and professional.

Hierarchy:

Page title:
24–28px

Section title:
16–18px

Body:
14–15px

Secondary:
12–13px

Metadata:
11–12px

Chat message:
15px

Code:
JetBrains Mono or similar monospace font.

============================================================
6. APPLICATION LAYOUT
============================================================

Desktop-first.

Primary target:

1440 × 900

Also design:

1600 × 1000

1920 × 1080

Application structure:

---------------------------------------------------------
| Sidebar |             Main Workbench                  |
|         |                                              |
|         |                                              |
|         |                                              |
|         |                                              |
---------------------------------------------------------

On the main chatbot page, use:

LEFT:
Navigation

CENTER:
Chat / Agent workspace

RIGHT:
Context panel that can collapse

The right panel should not always dominate the screen.

============================================================
7. LEFT SIDEBAR
============================================================

Width:
230–250px

Top:

Sovereign AI
WORKBENCH

Use a clean abstract geometric AI logo.

Below:

COMPANY CONTEXT

ApexPetro Energy Ltd.
Jamnagar Refinery

Show:

● Local Environment

Then navigation.

MAIN

Chat
Projects
Files
Knowledge

WORK

Tasks
Artifacts
Approvals

SYSTEM

Models
Security

Bottom:

GPU

NVIDIA GPU
18.4 / 24 GB VRAM

● Local Only

Then:

Arjun Mehta
Inspection Engineer

Avatar.

IMPORTANT:

Do NOT include:

Admin
Company Management
Company Switcher
User Management
Organization Management
Model Administration
System Configuration

Those belong to an administrator interface.

============================================================
8. TOP HEADER
============================================================

Top header should be minimal.

Left:

Breadcrumb or current context.

Example:

Chat
/
P-102 Equipment Integrity Review

Center/right:

Search icon

Notifications

Security status:

● LOCAL ONLY

User avatar

Clicking "LOCAL ONLY" opens a security popover.

============================================================
9. MAIN CHAT SCREEN
============================================================

This is the MOST IMPORTANT SCREEN.

Make it the strongest screen in the entire design.

The first screen should feel simple.

Do not immediately overwhelm the user with execution logs.

Structure:

----------------------------------------------------------
|                                                     |
|                  AI WORKBENCH                       |
|                                                     |
|   "What would you like to work on?"                |
|                                                     |
|      [ Build / Ask ] [ Code ] [ Change Model ]     |
|                                                     |
|                                                     |
|                Conversation area                   |
|                                                     |
|                                                     |
|-----------------------------------------------------|
| + | Type your message...                 | Send     |
|   | [Build / Ask] [Code] [Model]         |          |
----------------------------------------------------------

============================================================
10. CHAT EMPTY STATE
============================================================

When no conversation exists:

Large but subtle title:

"How can I help with your work?"

Subtitle:

"Analyze confidential information, work with company
knowledge, run calculations, write code, or create
business documents — entirely within your local environment."

Below the title show suggested task cards.

Cards:

Analyze a document

"Summarize an inspection report and identify key findings."

Compare documents

"Compare this vendor report with the applicable SOP."

Create a document

"Prepare an approval note from these inspection findings."

Analyze data

"Find abnormal trends in the maintenance history."

Code / Calculate

"Run a calculation securely in the sandbox."

Use company knowledge

"Find the procedure for pressure equipment inspection."

These are clickable prompt starters.

============================================================
11. PRIMARY MODE SELECTOR
============================================================

At the top of the composer, create three prominent controls:

[ ✦ Build / Ask ]

[ </> Code in Sandbox ]

[ ⚙ Change Model ]

The first is active by default.

This is inspired by the provided reference image,
but create a more refined and premium implementation.

Do NOT simply copy the reference.

============================================================
12. BUILD / ASK MODE
============================================================

When:

BUILD / ASK

is selected, the composer should support:

- normal questions
- document analysis
- RAG
- agentic tasks
- artifact generation
- multimodal input

Composer:

----------------------------------------------------------
| Type your message...                                   |
|                                                        |
| 📎  📄  🖼                                             |
|                                                        |
| [Build / Ask] [Code in Sandbox] [Change Model]       |
|                                                [↑]    |
----------------------------------------------------------

Icons:

Attach file
Attach document
Attach image

Send button:

arrow-up

Add subtle sparkle/agent icon but don't overuse AI symbols.

============================================================
13. CODE IN SANDBOX MODE
============================================================

When user clicks:

CODE IN SANDBOX

the interface changes.

Header:

Secure Code Sandbox

Subtitle:

"Run code locally inside an isolated execution environment."

Layout:

LEFT:
File/context panel

CENTER:
Code editor

RIGHT:
Execution / security panel

Code editor should resemble a professional IDE.

Example:

pressure = 42
limit = 40

deviation = pressure - limit

print(f"Deviation: {deviation} bar")

Bottom:

[ Run Code ]

Security panel:

NETWORK
BLOCKED

FILESYSTEM
ISOLATED

CPU
2 CORES

MEMORY
2 GB

TIMEOUT
30 SEC

EXECUTION
LOCAL

Output panel:

Execution Output

Deviation: 2 bar

Execution completed in 0.84s

Add:

"Container destroyed after execution"

============================================================
14. CHANGE MODEL
============================================================

When user clicks:

CHANGE MODEL

open a model selection drawer or popover.

Do NOT make it an admin model-management page.

The user can only select from approved models.

Header:

"Choose AI Model"

Subtext:

"Available models are approved for your workspace."

Model cards:

------------------------------------------------
LOCAL REASONING
Qwen 2.5 32B Instruct

Best for:
Complex reasoning
Document analysis
Technical tasks

Context:
32K

VRAM:
18 GB

Status:
● Ready

[ Select ]
------------------------------------------------

LOCAL VISION
Qwen2.5-VL / Local Vision Model

Best for:
Images
Scanned documents
Drawings

Status:
● Ready

[ Select ]
------------------------------------------------

LOCAL CODING
Local Coding Model

Best for:
Python
Code generation
Debugging

Status:
● Ready

[ Select ]
------------------------------------------------

Also provide:

AUTO

"Let the system select the best available model for the task."

AUTO should be the default.

Show:

✓ Local inference
✓ No external API
✓ Workspace-approved

============================================================
15. CHAT CONVERSATION
============================================================

User messages should be clean.

User:

"Analyze the latest P-102 inspection package and prepare
an approval note for engineering review."

AI should show a task-oriented response.

First:

"Task understood."

Then:

"Preparing an execution plan..."

Show a compact expandable execution card.

============================================================
16. AGENT PLAN CARD
============================================================

Design a beautiful expandable component:

INSPECTION ANALYST
Agent

12 steps

Progress:
7 / 12

Then:

✓ Identify P-102
✓ Read inspection report
✓ Analyze equipment photograph
✓ Read measurement spreadsheet
✓ Retrieve applicable SOP
✓ Retrieve historical records
● Compare readings
○ Calculate deviation
○ Determine risk
○ Verify evidence
○ Request approval
○ Generate approval note

Each step should display:

Status
Tool/model
Duration

Example:

✓ Retrieve applicable SOP
RAG Search
1.2s

Do not show hidden chain-of-thought.

The UI should show only:
- task plan
- actions
- tools used
- results
- evidence

Never expose private model reasoning.

============================================================
17. AGENT ACTIVITY
============================================================

Allow the user to expand:

"Activity"

Then show:

09:42:04
OCR
Inspection Report 2026

09:42:08
Vision
Equipment Photograph

09:42:13
Knowledge Search
Pump Inspection SOP

09:42:17
Knowledge Search
Inspection Report 2025

09:42:21
Excel Analyzer
Measurements.xlsx

09:42:24
Python Sandbox
Risk calculation

This is not chain-of-thought.

It is an execution log.

============================================================
18. FINAL AI RESPONSE
============================================================

After task completion:

Create a structured response.

Title:

P-102 Integrity Assessment

Risk:

HIGH

Use three finding cards:

PRESSURE

42 bar

Limit:
40 bar

Deviation:
+2 bar

CORROSION

3.8 mm

Assessment:
Engineering review

VIBRATION

7.2 mm/s

Assessment:
High concern

Then:

Historical Trend

2024
34 bar

2025
37 bar

2026
42 bar

Display a clean line chart.

============================================================
19. RECOMMENDATION
============================================================

Create a highlighted recommendation section.

"Recommended Action"

Engineering integrity review is recommended before
continued operation under current conditions.

Below:

"AI-generated recommendation"

"This recommendation requires authorized human review."

Use amber rather than red.

============================================================
20. SOURCES / EVIDENCE
============================================================

Every important answer should have evidence.

Create:

"Sources (6)"

Each source card:

01
P-102 Inspection Report 2026

Page 7

CONFIDENTIAL

02
Pump Inspection SOP v3.2

Section 7.2

CONFIDENTIAL

03
P-102 Inspection Report 2025

Page 4

CONFIDENTIAL

04
P-102 Maintenance History

2025-10-12

INTERNAL

Each should have:

View source
Open document

Show small relevance indicators.

============================================================
21. RIGHT CONTEXT PANEL
============================================================

On desktop, the right panel can show:

ACTIVE MODEL

Qwen 2.5 32B Instruct

● Ready

Local Reasoning Model

Then:

CONTEXT

Project:
P-102 Equipment Integrity Review

Asset:
P-102

Unit:
CDU-4

Classification:
CONFIDENTIAL

Then:

SOURCES

6 sources

Then:

ARTIFACTS

Approval Note
Risk Assessment

Then:

SECURITY

● Local Only

Internet:
Blocked

External APIs:
Blocked

Cloud AI:
Disabled

Local inference:
Active

The panel should be collapsible.

============================================================
22. FILE ATTACHMENT UX
============================================================

User should be able to drag/drop files directly into chat.

Supported:

PDF
DOCX
XLSX
PPTX
PNG
JPG
TIFF

When attached:

------------------------------------------------
P-102_Inspection_Report_2026.pdf
CONFIDENTIAL
12 pages
● Ready
------------------------------------------------

For image:

P-102_Equipment_Photo.jpg
CONFIDENTIAL
Image
● Ready

For spreadsheet:

P-102_Measurements.xlsx
INTERNAL
5 sheets
● Ready

============================================================
23. FILE PROCESSING
============================================================

After upload, show a subtle processing state.

Example:

Processing document...

✓ File received
✓ Security classification
✓ OCR
● Extracting content
○ Indexing knowledge

Progress:

68%

Do not make this look like a technical installation process.

Keep it understandable to an employee.

============================================================
24. DOCUMENT PREVIEW
============================================================

When user clicks a document:

Open a document viewer.

Layout:

LEFT:
Page thumbnails

CENTER:
Document

RIGHT:
AI information

Right panel:

Document Information

Title:
P-102 Inspection Report 2026

Type:
Inspection Report

Classification:
CONFIDENTIAL

Asset:
P-102

Department:
Inspection & Integrity

Status:
Indexed

AI Extracted Data:

Pressure:
42 bar

Temperature:
190°C

Corrosion:
3.8 mm

Vibration:
7.2 mm/s

Button:

"Ask AI about this document"

============================================================
25. KNOWLEDGE SEARCH
============================================================

The user should be able to explicitly search company knowledge.

Page:

"Company Knowledge"

Search:

"Search your organization's knowledge..."

Filters:

SOP
Manual
Policy
Inspection
Maintenance
Asset
Historical
Vendor

Example query:

"What is the maximum operating pressure for P-102?"

Results:

Pump Inspection SOP
Section 7.2

P-102 Equipment Datasheet

P-102 Inspection 2025

Each result shows:

title
document type
section
classification
date

============================================================
26. PROJECTS
============================================================

User-facing project page.

Projects:

P-102 Equipment Integrity Review
CDU-4 Maintenance Analysis
Vendor Report Comparison
Annual Inspection Planning

Cards should show:

Progress
Status
Last activity
Files
Artifacts

Do NOT show administration controls.

============================================================
27. PROJECT DETAIL
============================================================

Example:

P-102 Equipment Integrity Review

Top:

ApexPetro Energy Limited
Jamnagar Refinery Complex
CDU-4
P-102

Status:
Awaiting Approval

Risk:
HIGH

Tabs:

Overview
Files
AI Tasks
Sources
Artifacts
Approvals

Do not expose system administration.

============================================================
28. TASKS
============================================================

Create a user task page.

Title:

"My Tasks"

Cards:

P-102 Inspection Analysis
Awaiting Approval

Vendor Report Comparison
Completed

Maintenance Trend Analysis
Running

Each task should show:

status
created time
agent
risk
progress

============================================================
29. ARTIFACTS
============================================================

Create a clean artifact library.

Title:

"Artifacts"

Tabs:

All
Documents
Spreadsheets
Presentations
Code
Reports

Example:

Approval_Note_P-102_2026.docx

Status:
Awaiting Approval

Created by:
Inspection Analyst

Classification:
CONFIDENTIAL

Actions:

Preview
Open
Download

Another:

Risk_Assessment_P-102.xlsx

Status:
Verified

============================================================
30. APPROVAL UI
============================================================

When AI produces a high-risk recommendation:

Show an approval request.

Do NOT hide this inside chat.

Example:

------------------------------------------------
HUMAN REVIEW REQUIRED

P-102 Equipment Integrity Review

Risk:
HIGH

Recommendation:
Engineering integrity review required.

Evidence:
6 sources

Verification:
PASSED

Generated artifact:
Approval_Note_P-102_2026.docx

[ Review Evidence ]

[ Reject ]     [ Approve ]
------------------------------------------------

The user should understand:

AI recommends.

Human decides.

============================================================
31. SECURITY PANEL
============================================================

Create a lightweight security page accessible from sidebar.

Title:

"Your Secure Environment"

Large status:

● LOCAL ONLY

Text:

"Your organization's AI environment operates entirely
within its controlled infrastructure."

Show:

Internet
BLOCKED

External AI APIs
BLOCKED

Cloud AI
DISABLED

Local Models
ACTIVE

Local Storage
ACTIVE

Sandbox Network
BLOCKED

Audit Logging
ACTIVE

Important:

Do not claim real network isolation unless it is actually
verified by the backend.

============================================================
32. SECURITY POPOVER
============================================================

Clicking:

● LOCAL ONLY

opens a compact popover.

Title:

Secure Environment

✓ Local inference
✓ Company-isolated data
✓ External APIs blocked
✓ Sandbox isolated

"View security details →"

This should be visible but not annoying.

============================================================
33. MODELS PAGE
============================================================

This is USER-facing model information.

Do not allow model installation.

Show approved models:

AUTO
Recommended

Reasoning Model
Ready

Vision Model
Ready

Coding Model
Ready

Each:

Purpose
Status
Context
Approximate latency
VRAM

The user can select a model for a conversation.

============================================================
34. PROFILE
============================================================

User profile:

Arjun Mehta

Inspection Engineer

Inspection & Integrity

ApexPetro Energy Limited

Jamnagar Refinery Complex

Settings:

Appearance
Notifications
Keyboard shortcuts

Do NOT show company switching.

============================================================
35. SEARCH
============================================================

Global search:

Ctrl + K

Search:

Chats
Projects
Documents
Knowledge
Tasks
Artifacts

Example:

P-102

Results grouped by category.

============================================================
36. COMMAND PALETTE
============================================================

Ctrl + K

Commands:

New Chat
Upload File
Search Knowledge
Open Projects
Open Artifacts
Run Sandbox
Change Model
View Approvals
Open Security

============================================================
37. NOTIFICATIONS
============================================================

Examples:

Approval required for P-102

Document indexing completed

Risk assessment verified

Artifact generated

Sandbox execution completed

Document processing failed

============================================================
38. EMPTY STATES
============================================================

Design beautiful empty states.

No conversations:

"Start a new task"

"No conversation yet."

No projects:

"No active projects"

No artifacts:

"Generated deliverables will appear here."

No approvals:

"You're all caught up."

No search results:

"No matching company knowledge found."

============================================================
39. ERROR STATES
============================================================

Model unavailable:

"Local model unavailable"

"The selected model is currently unavailable."

Buttons:

Retry
Switch Model

Document processing:

"Unable to process document"

Buttons:

Retry
View details

Sandbox:

"Execution failed"

Show safe error output.

============================================================
40. LOADING STATES
============================================================

Create skeleton states for:

Chat
Project
Documents
Knowledge
Artifacts
Approvals
Model selector

For AI generation:

Show:

"Analyzing..."

"Searching company knowledge..."

"Reviewing attached documents..."

"Running calculation..."

"Preparing deliverable..."

Do NOT show fake internal thoughts.

============================================================
41. MAIN CHAT COMPOSER
============================================================

The composer is the signature component.

Design it beautifully.

Large rounded rectangle but not excessively rounded.

Example:

----------------------------------------------------------
| Type a message, attach files, or describe a task...    |
|                                                        |
| 📎 Attach   📄 Knowledge   🖼 Image                    |
|                                                        |
| [ ✦ Build / Ask ] [ </> Code ] [ ⚙ Model ]     [ ↑ ] |
----------------------------------------------------------

When a file is attached, show chips above the input.

Example:

[P-102_Report.pdf ×]
[P-102_Photo.jpg ×]

============================================================
42. BUILD / ASK SUBMODES
============================================================

Build / Ask can intelligently support:

Ask
Analyze
Create
Compare
Summarize
Extract
Calculate

But do NOT clutter the composer with seven buttons.

Instead provide:

Build / Ask ▾

Dropdown:

Ask
Analyze
Create
Compare
Summarize

Default:
Ask

============================================================
43. ARTIFACT CREATION
============================================================

When user says:

"Create an approval note"

Show:

"Preparing document..."

Then artifact preview.

Document card:

Approval Note

P-102 Equipment Integrity Review

DOCX

CONFIDENTIAL

VERIFIED

[Preview]

[Open]

[Download]

============================================================
44. MULTIMODAL EXPERIENCE
============================================================

Support:

PDF
Scanned PDF
Images
Photos
Excel
Word
PowerPoint

Example:

User uploads:

Inspection_Report.pdf
Equipment_Photo.jpg
Measurements.xlsx

Chat displays:

3 attachments

Then:

"Ready for analysis."

The agent automatically decides whether it needs:

OCR
Vision
Excel
RAG
Reasoning
Sandbox

============================================================
45. AGENT TRANSPARENCY
============================================================

Important:

Do NOT expose hidden chain-of-thought.

Instead expose:

Plan
Actions
Tools
Sources
Results
Verification
Approval

Example:

"Agent activity"

✓ Retrieved SOP
✓ Analyzed image
✓ Compared historical data
✓ Calculated deviation
✓ Verified evidence

This gives transparency without exposing private reasoning.

============================================================
46. MOBILE / TABLET
============================================================

Desktop is primary.

For tablet:

- sidebar collapses
- right context becomes drawer

For mobile:

- bottom navigation
- right context becomes modal/drawer
- composer remains primary

But do NOT sacrifice desktop experience.

============================================================
47. COMPONENT LIBRARY
============================================================

Create reusable Figma components.

Components:

AppShell
Sidebar
TopBar
CompanyContext
SecurityBadge
UserAvatar

Chat
ChatMessage
AIMessage
UserMessage
ChatComposer
ModeSelector
AttachmentChip
SuggestionCard

Agent
AgentPlan
AgentStep
AgentActivity
AgentStatus

Models
ModelSelector
ModelCard
ModelStatus

Documents
DocumentCard
DocumentRow
DocumentViewer
DocumentMetadata
UploadArea
ProcessingStatus

Knowledge
KnowledgeSearch
SourceCard
EvidenceCard
Citation

Artifacts
ArtifactCard
ArtifactPreview

Approvals
ApprovalCard
ApprovalDialog

Sandbox
CodeEditor
ExecutionOutput
SandboxSecurityPanel

System
Toast
Modal
Drawer
Tooltip
Dropdown
Tabs
CommandPalette
LoadingState
EmptyState
ErrorState

============================================================
48. DESIGN SYSTEM
============================================================

Create Figma variables/tokens for:

Colors
Typography
Spacing
Radius
Shadows
Borders
Icons

Spacing:

4
8
12
16
20
24
32
40
48

Border radius:

6
8
10
12
16

Do not make everything pill-shaped.

Buttons:

Primary
Secondary
Ghost
Danger

Status:

Success
Warning
Critical
Neutral

============================================================
49. INTERACTION DESIGN
============================================================

Create prototype interactions for:

Chat mode selection

Build / Ask
→ active state

Code
→ opens sandbox mode

Change Model
→ opens model drawer

Upload
→ opens file picker state

Send
→ creates user message

AI response
→ shows execution plan

Execution plan
→ expand/collapse

Source
→ opens evidence drawer

Artifact
→ opens preview

Approval
→ opens approval dialog

Security badge
→ opens security popover

Sidebar
→ navigation

Command palette
→ Ctrl + K

============================================================
50. IMPORTANT SCREEN STATES
============================================================

Create the following high-fidelity screens:

SCREEN 01
Login

SCREEN 02
Empty Chat

SCREEN 03
Chat with Build / Ask selected

SCREEN 04
Chat with uploaded documents

SCREEN 05
Agent executing

SCREEN 06
Agent completed

SCREEN 07
Evidence drawer

SCREEN 08
Artifact generated

SCREEN 09
Human approval required

SCREEN 10
Code Sandbox

SCREEN 11
Change Model drawer

SCREEN 12
Projects

SCREEN 13
Project Detail

SCREEN 14
Documents

SCREEN 15
Document Viewer

SCREEN 16
Knowledge Search

SCREEN 17
Artifacts

SCREEN 18
Approvals

SCREEN 19
Security

SCREEN 20
Models

SCREEN 21
Tasks

SCREEN 22
Profile

SCREEN 23
Search / Command Palette

SCREEN 24
Error State

SCREEN 25
Empty State

============================================================
51. PRIMARY DEMO SCREEN
============================================================

The most polished screen must be the main chatbot.

Seed it with:

User:

"Analyze the latest P-102 inspection package. Compare
the current readings with the applicable ApexPetro SOP
and previous inspection history, review the equipment
photograph, calculate the deviation from operating limits,
determine the risk level, and prepare an approval note
for engineering review."

Show:

TASK UNDERSTOOD

Inspection Analyst

Execution plan:

✓ Identify P-102
✓ OCR inspection report
✓ Analyze equipment photograph
✓ Read measurements
✓ Retrieve applicable SOP
✓ Retrieve historical reports
✓ Compare readings
✓ Calculate deviation
✓ Determine risk
✓ Verify evidence
→ Human approval required
○ Generate approval note

Final result:

P-102 Integrity Assessment

HIGH RISK

Pressure:
42 bar

Limit:
40 bar

Deviation:
+2 bar

Corrosion:
3.8 mm

Vibration:
7.2 mm/s

Historical pressure:

2024 → 34
2025 → 37
2026 → 42

Recommendation:

Engineering integrity review is recommended.

Then:

6 Sources

Then:

Approval Note
DOCX
Awaiting Approval

============================================================
52. USER'S COMPANY CONTEXT
============================================================

Use this information consistently:

Company:
ApexPetro Energy Limited

Facility:
Jamnagar Refinery Complex

Department:
Inspection & Integrity

Unit:
CDU-4

Asset:
P-102

Asset Type:
Centrifugal Process Pump

Service:
Crude Transfer

Criticality:
HIGH

Classification:
CONFIDENTIAL

============================================================
53. APEXPETRO DATA
============================================================

P-102:

Design pressure:
50 bar

Maximum operating pressure:
40 bar

Normal operating pressure:
35 bar

Temperature:
190°C

Historical:

2024:
Pressure 34 bar
Corrosion 1.2 mm
Vibration 4.1 mm/s

2025:
Pressure 37 bar
Corrosion 2.4 mm
Vibration 5.3 mm/s

2026:
Pressure 42 bar
Corrosion 3.8 mm
Vibration 7.2 mm/s

SOP:

Above 40 bar:
Engineering review required

Above 45 bar:
Immediate operational escalation

Vibration:

<4 mm/s
Normal

4–7 mm/s
Monitoring

>7 mm/s
High concern

Corrosion:

<2 mm
Normal

2–3 mm
Increased monitoring

3–4 mm
Engineering assessment

>4 mm
Immediate integrity review

============================================================
54. SAMPLE DOCUMENTS
============================================================

Use these in the UI:

P-102_Inspection_Report_2026.pdf
P-102_Equipment_Photo.jpg
P-102_Measurements.xlsx
Vendor_Inspection_Report_2026.pdf
P-102_Inspection_Report_2025.pdf
P-102_Inspection_Report_2024.pdf
P-102_Equipment_Datasheet.pdf
Pump_Inspection_SOP.pdf
Corrosion_Assessment_SOP.pdf
Risk_Assessment_SOP.pdf
P-102_Maintenance_History.xlsx

============================================================
55. SECURITY UX
============================================================

The security message should be:

"Your work stays inside your organization's controlled
environment."

Use:

● LOCAL ONLY

Do not repeatedly say:

"100% secure"

"Impossible to hack"

"Guaranteed secure"

Security UI must communicate architecture rather than
making unsupported claims.

============================================================
56. FINAL PRODUCT FEEL
============================================================

When a user opens the application, their first impression
should be:

"This is my company's private AI assistant."

NOT:

"This is an AI administration platform."

The interface should prioritize:

1. Chat
2. Task creation
3. File interaction
4. Agent activity
5. Evidence
6. Artifacts
7. Approvals

Everything else should remain secondary.

The user should be able to perform their work without
understanding AI infrastructure.

The complexity should be available when needed,
not forced onto the user.

============================================================
57. FINAL VISUAL REQUIREMENT
============================================================

The final design should resemble a premium enterprise AI
workbench with:

- dark navy background
- purple primary interaction accent
- teal local/security indicators
- excellent typography
- thin borders
- subtle depth
- compact cards
- sophisticated icons
- clean data visualization
- high-quality chat experience
- professional file handling
- beautiful agent execution states

Use the provided reference image as inspiration for the
composer mode selector:

[ Build / Ask ]
[ Code in Sandbox ]
[ Change Model ]

But improve the hierarchy, spacing, typography,
interaction states and enterprise polish.

============================================================
58. Figma DELIVERABLE
============================================================

Create:

1. Complete desktop design
2. Complete tablet adaptation
3. Component library
4. Design tokens
5. All interaction states
6. Prototype connections
7. Hover states
8. Active states
9. Loading states
10. Error states
11. Empty states
12. Modal states
13. Drawer states
14. Agent execution states
15. Approval states

Use Auto Layout throughout.

Use reusable components and variants.

Use Figma Variables for colors, spacing and typography.

Do not create every screen as independent disconnected
elements.

The final Figma file should be organized so developers can
inspect components and implement the UI directly.