# Skills Validation Workshop (SVW) - Anson Bolinger

This repository contains the solutions, multi-agent implementations, evaluation frameworks, and verification artifacts for the **L400: Mission-Ready Agents Skills Validation Workshop**.

---

## Workshop Structure & Index

| Challenge | Directory | Description | Status |
| :--- | :--- | :--- | :--- |
| **Challenge 1** | [`challenge-1-workflows/`](./challenge-1-workflows/) | Multi-Agent Workflow with ADK (Research, Validation, Refinement, Human Review) | Completed |
| **Challenge 2** | [`challenge-2-rag/`](./challenge-2-rag/) | Integrating RAG and Google Search into a Multi-Agent System | Completed |
| **Challenge 3** | [`challenge-3-mcp/`](./challenge-3-mcp/) | Connecting Agents to External Systems with Custom & Google MCP Servers | Completed |
| **Challenge 4** | [`challenge-4-evaluation/`](./challenge-4-evaluation/) | Evaluating Agent Performance with the Agent Evaluation API & Test Suites | Completed |
| **Challenge 5** | [`challenge-5-deployment/`](./challenge-5-deployment/) | Deploying an Enterprise Support Agent to Gemini Enterprise | Completed |
| *Challenge 6* | *TBD* | Case Study: Agentic Field Operations for Alaska Dept of Snow | Pending |

---

## Challenge 1: Building a Multi-Agent Workflow with ADK

### 1. Overview
The goal of Challenge 1 is to build a multi-agent system composed of specialized sub-agents where each owns a distinct stage in a business workflow. The system processes a user request, explores it, validates it against quality criteria, refines it using feedback, and confirms satisfaction with the user.

### 2. Architecture & Agents Design

The workflow is orchestrated using ADK's `SequentialAgent` and manages shared conversation state across 4 specialized stages:

```
[User Request]
       │
       ▼
┌─────────────────────────┐
│     research_agent      │  ──▶ Writes finding to state: "research_findings"
└─────────────────────────┘
       │
       ▼
┌─────────────────────────┐
│    validation_agent     │  ──▶ Reads "research_findings" from state
└─────────────────────────┘  ──▶ Writes critique to state: "validation_feedback"
       │
       ▼
┌─────────────────────────┐
│    refinement_agent     │  ──▶ Reads findings + critique via callback: prepare_refinement_instruction()
└─────────────────────────┘  ──▶ Writes polished output to state: "refined_response"
       │
       ▼
┌─────────────────────────┐
│   human_review_agent    │  ──▶ Presents final answer and prompts user for adequacy confirmation
└─────────────────────────┘
```

#### Specialized Sub-Agents:
1. **`research_agent`** ([challenge-1-workflows/app/agent.py](./challenge-1-workflows/app/agent.py)):
   - **Role:** Research Analyst.
   - **Task:** Analyzes user queries, identifies core concepts, and breaks down topics into structured, factual points.
   - **Session State:** Stores output in `output_key="research_findings"`.

2. **`validation_agent`** ([challenge-1-workflows/app/agent.py](./challenge-1-workflows/app/agent.py)):
   - **Role:** Quality & Validation Specialist.
   - **Task:** Reads `{research_findings}`, evaluates factual accuracy, completeness, and clarity, points out ambiguities or missing constraints, and provides constructive critique.
   - **Session State:** Stores output in `output_key="validation_feedback"`.

3. **`refinement_agent`** ([challenge-1-workflows/app/agent.py](./challenge-1-workflows/app/agent.py)):
   - **Role:** Synthesis & Polish Specialist.
   - **Task:** Programmatically extracts both `research_findings` and `validation_feedback` from `ctx.state` via `prepare_refinement_instruction(ctx)`, addresses every critique point, and synthesizes a polished final response.
   - **Session State:** Stores output in `output_key="refined_response"`.

4. **`human_review_agent` (Bonus requirement)** ([challenge-1-workflows/app/agent.py](./challenge-1-workflows/app/agent.py)):
   - **Role:** Customer Experience Reviewer.
   - **Task:** Presents `{refined_response}` and directly asks the user if the response is adequate or if further adjustments, details, or a different format are needed.

5. **`root_agent` (`SequentialAgent`)**:
   - Manages linear execution, passing state automatically between nodes.

### 3. How to Run & Verify Challenge 1
```bash
cd challenge-1-workflows
uv sync
uvx google-agents-cli playground
```
Screenshots demonstrating the multi-agent workflow are stored in:
- [`challenge-1-workflows/screenshots/`](./challenge-1-workflows/screenshots/)

---

## Challenge 2: Integrating RAG and Google Search into an Agent

### 1. Overview
The goal of Challenge 2 is to build a multi-agent system equipped with two grounding mechanisms:
1. **A private RAG datastore** containing proprietary synthetic corporate knowledge (Novasphere Dynamics company policies, travel per diems, remote work, IT security protocols, and proprietary robotics specs).
2. **Live Google Search** to retrieve up-to-date, public information when the local corpus is insufficient.
3. **A root router agent** that evaluates incoming questions and dynamically routes them to the appropriate specialized sub-agent.

### 2. Architecture & Agents Design

The routing architecture uses an intelligent ADK router agent with dynamic agent transfer:

```
                      [User Inquiry]
                            │
                            ▼
               ┌─────────────────────────┐
               │    challenge_2_rag      │  (Root Router Agent)
               │    Evaluates intent     │
               └────────────┬────────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
            ▼                               ▼
┌─────────────────────────┐   ┌─────────────────────────┐
│    rag_search_agent     │   │   google_search_agent   │
│  (Private Datastore)    │   │      (Web Search)       │
└───────────┬─────────────┘   └─────────────┬───────────┘
            │                               │
            ▼                               ▼
┌─────────────────────────┐   ┌─────────────────────────┐
│ Novasphere Knowledge    │   │  Live Google Search     │
│ Base (specs, policies)  │   │  Grounding Tool         │
└─────────────────────────┘   └─────────────────────────┘
```

#### Specialized Sub-Agents:
1. **`rag_search_agent`** ([challenge-2-rag/app/agent.py](./challenge-2-rag/app/agent.py)):
   - **Role:** Internal Knowledge Assistant.
   - **Grounding Tool:** `search_internal_datastore` ([challenge-2-rag/app/tools/rag_tool.py](./challenge-2-rag/app/tools/rag_tool.py)) backed by the synthetic Novasphere Dynamics corpus ([challenge-2-rag/data/novasphere_knowledge_base.md](./challenge-2-rag/data/novasphere_knowledge_base.md)), plus optional `VertexAiSearchTool` integration.
   - **Scope:** Answers questions on proprietary products (e.g., AetherBot v4, Chronos-Edge Controller), employee travel per diems (\$85/day domestic, \$120 high-cost), WFA policies (45 days remote), and YubiKey security policies.

2. **`google_search_agent`** ([challenge-2-rag/app/agent.py](./challenge-2-rag/app/agent.py)):
   - **Role:** Public Web Intelligence Assistant.
   - **Grounding Tool:** ADK's native `google_search` grounding tool.
   - **Scope:** Answers questions on live external facts, world news, sports results, public company information, and current events.

3. **`root_agent` (`challenge_2_rag`)**:
   - Analyzes user queries and dispatches via ADK `sub_agents` to `rag_search_agent` or `google_search_agent`.

### 3. How to Run & Verify Challenge 2
```bash
cd challenge-2-rag
uv sync
uvx google-agents-cli playground
```
Screenshots demonstrating the RAG and Google search multi-agent system are stored in:
- [`challenge-2-rag/screenshots/`](./challenge-2-rag/screenshots/)

---

## Challenge 3: Connecting Agents to External Systems with MCP

### 1. Overview
The goal of Challenge 3 is to build and connect external tools to ADK agents using the **Model Context Protocol (MCP)** standard. The system integrates:
1. A **custom FastMCP server** exposing local Python functions as callable tools.
2. A **Google-provided MCP server** (`@google-cloud/gcloud-mcp`) connecting agents to Google Cloud tools.
3. A **root router agent** directing inquiries to the appropriate MCP-powered specialist.

### 2. Architecture & Agents Design

```
                      [User Inquiry]
                            │
                            ▼
               ┌─────────────────────────┐
               │    challenge_3_mcp      │  (Root Router Agent)
               │    Evaluates intent     │
               └────────────┬────────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
            ▼                               ▼
┌─────────────────────────┐   ┌─────────────────────────┐
│    custom_mcp_agent     │   │    google_mcp_agent     │
│   (McpToolset: Custom)  │   │  (McpToolset: Google)   │
└───────────┬─────────────┘   └─────────────┬───────────┘
            │                               │
            ▼                               ▼
┌─────────────────────────┐   ┌─────────────────────────┐
│ Custom FastMCP Server   │   │ Google Cloud MCP Server │
│ - System Diagnostics    │   │ - @google-cloud/        │
│ - Cluster Budget Calc   │   │   gcloud-mcp            │
│ - Text Transformations  │   │                         │
└─────────────────────────┘   └─────────────────────────┘
```

#### Specialized Sub-Agents:
1. **`custom_mcp_agent`** ([challenge-3-mcp/app/agent.py](./challenge-3-mcp/app/agent.py)):
   - **Connected Server:** Custom FastMCP Server ([challenge-3-mcp/mcp_server/server.py](./challenge-3-mcp/mcp_server/server.py)) via stdio protocol.
   - **Exposed MCP Tools:**
     - `get_system_diagnostics`: Reads OS platform, architecture, status, and UTC timestamp.
     - `calculate_resource_budget`: Computes total vCPUs, RAM, and hourly/monthly USD cloud budget based on cluster sizing.
     - `transform_identifier`: Converts strings into code identifiers (`kebab-case`, `snake_case`, `camelCase`).

2. **`google_mcp_agent`** ([challenge-3-mcp/app/agent.py](./challenge-3-mcp/app/agent.py)):
   - **Connected Server:** Official Google-provided `@google-cloud/gcloud-mcp` via stdio connection.
   - **Scope:** Google Cloud resource inspection, projects, active configurations, and CLI operations.

3. **`root_agent` (`challenge_3_mcp`)**:
   - Routes between custom operational MCP tools and Google Cloud platform tools.

### 3. How to Run & Verify Challenge 3
```bash
cd challenge-3-mcp
uv sync
uvx google-agents-cli playground
```
Screenshots demonstrating the custom and Google-provided MCP tools are stored in:
- [`challenge-3-mcp/screenshots/`](./challenge-3-mcp/screenshots/)

---

## Challenge 4: Evaluating Agent Performance with the Agent Evaluation API

### 1. Overview
The goal of Challenge 4 is to use the **ADK Agent Evaluation API** (`agents-cli eval`) to systematically test, benchmark, and optimize a customer service agent answering retail return, warranty, shipping, and refund policy questions (Cymbal Retail).

### 2. Evaluation Findings Summary

| Phase | System Prompt | Mean Score (1-5) | Pass Rate | Key Findings |
| :--- | :--- | :---: | :---: | :--- |
| **Baseline** | Generic instructions | **3.50 / 5.0** | 50% | Hallucinated return deadlines for electronics; asked user for shipping thresholds; missed photo ID requirements. |
| **Optimized** | Explicit policy grounding | **5.00 / 5.0** | **100%** | Strict 14-day electronic return enforcement, calculated shipping differences, enforced photo ID checks. |

*Full comparative report available in:* [`challenge-4-evaluation/EVALUATION_REPORT.md`](./challenge-4-evaluation/EVALUATION_REPORT.md)

### 3. How to Run Evaluations and Tests
```bash
cd challenge-4-evaluation
uv sync
uvx google-agents-cli eval run --dataset tests/eval/datasets/customer-service-eval.json --output eval_results.json
uv run pytest tests/test_customer_service_agent.py
```

---

## Challenge 5: Deploying an Enterprise Support Agent to Gemini Enterprise

### 1. Overview
The goal of Challenge 5 is to deploy an ADK agent to Google Cloud Agent Platform / Reasoning Engine, register it with Gemini Enterprise, and interact with the agent directly through the Gemini Enterprise workspace.

### 2. Agent Tools & Capabilities ([challenge-5-deployment/app/agent.py](./challenge-5-deployment/app/agent.py))
- `check_order_status`: Queries enterprise POs/orders (e.g., `ORD-10928`) returning real-time carrier tracking and estimated delivery times.
- `calculate_shipping_tier`: Computes shipping costs (Standard Ground vs. Priority Express) and transit times by weight and destination ZIP code.
- `lookup_support_policy`: Details return windows, warranty terms, and enterprise SLA policies.

### 3. Deployed Cloud Resource Details
- **Reasoning Engine Resource ID:** `projects/28485185593/locations/us-east1/reasoningEngines/4295509355232493568`
- **Target:** Google Cloud Agent Platform (Agent Runtime)
- **Region:** `us-east1`
- **A2A Agent Card:** Registered in Google Cloud Agent Registry

### 4. Verification Screenshots
Screenshots demonstrating the agent deployed in Google Cloud Console and operating inside the Gemini Enterprise workspace are stored in:
- [`challenge-5-deployment/screenshots/`](./challenge-5-deployment/screenshots/)
  - `1.png` - Cloud Console Reasoning Engine / Agent Runtime deployment view
  - `2.png` - Gemini Enterprise workspace registration & configuration
  - `3.png` - Agent answering enterprise support questions in Gemini Enterprise
  - `4.png` - Live tool invocation and structured tracking output in Gemini Enterprise
