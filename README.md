# Skills Validation Workshop (SVW) - Anson Bolinger

This repository contains the solutions, multi-agent implementations, and verification artifacts for the **L400: Mission-Ready Agents Skills Validation Workshop**.

---

## Workshop Structure & Index

| Challenge | Directory | Description | Status |
| :--- | :--- | :--- | :--- |
| **Challenge 1** | [`challenge-1-workflows/`](./challenge-1-workflows/) | Multi-Agent Workflow with ADK (Research, Validation, Refinement, Human Review) | Completed |
| **Challenge 2** | [`challenge-2-rag/`](./challenge-2-rag/) | Integrating RAG and Google Search into a Multi-Agent System | Completed |
| *Future Challenges* | *TBD* | Additional mission-ready agent challenges | Pending |

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

1. **Setup & Dependencies:**
   ```bash
   cd challenge-2-rag
   uv sync
   ```

2. **Environment Configuration:**
   Verify `.env` has your active Google Cloud project:
   ```env
   GOOGLE_GENAI_USE_ENTERPRISE=true
   GOOGLE_CLOUD_PROJECT=qwiklabs-gcp-02-184746eee247
   GOOGLE_CLOUD_LOCATION=global
   ```

3. **Run the Agent Playground:**
   ```bash
   uvx google-agents-cli playground
   ```

4. **Sample Test Prompts:**
   - **Internal RAG Prompt:** `"What is the payload capacity of Novasphere's AetherBot v4?"`  
     *Result:* Routes to `rag_search_agent`, calls internal datastore, returns 1,250 kg (2,755 lbs).
   - **Internal Policy Prompt:** `"What is Novasphere's daily meal per diem for domestic travel?"`  
     *Result:* Routes to `rag_search_agent`, returns \$85/day (\$20 breakfast, \$25 lunch, \$40 dinner).
   - **Google Search Prompt:** `"Who won the men's 2024 ICC T20 World Cup?"`  
     *Result:* Routes to `google_search_agent`, queries Google Search, returns India with match details.
