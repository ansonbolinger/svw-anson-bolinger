# Skills Validation Workshop (SVW) - Anson Bolinger

This repository contains the solutions, multi-agent implementations, and verification artifacts for the **L400: Mission-Ready Agents Skills Validation Workshop**.

---

## Workshop Structure & Index

| Challenge | Directory | Description | Status |
| :--- | :--- | :--- | :--- |
| **Challenge 1** | [`challenge-1-workflows/`](./challenge-1-workflows/) | Multi-Agent Workflow with ADK (Research, Validation, Refinement, Human Review) | Completed |
| **Challenge 2** | *Coming Soon* | Integrating RAG and Google Search into an Agent | Pending |
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
1. **`research_agent`** ([app/agent.py](./challenge-1-workflows/app/agent.py)):
   - **Role:** Research Analyst.
   - **Task:** Analyzes user queries, identifies core concepts, and breaks down topics into structured, factual points.
   - **Session State:** Stores output in `output_key="research_findings"`.

2. **`validation_agent`** ([app/agent.py](./challenge-1-workflows/app/agent.py)):
   - **Role:** Quality & Validation Specialist.
   - **Task:** Reads `{research_findings}`, evaluates factual accuracy, completeness, and clarity, points out ambiguities or missing constraints, and provides constructive critique.
   - **Session State:** Stores output in `output_key="validation_feedback"`.

3. **`refinement_agent`** ([app/agent.py](./challenge-1-workflows/app/agent.py)):
   - **Role:** Synthesis & Polish Specialist.
   - **Task:** Programmatically extracts both `research_findings` and `validation_feedback` from `ctx.state` via `prepare_refinement_instruction(ctx)`, addresses every critique point, and synthesizes a polished final response.
   - **Session State:** Stores output in `output_key="refined_response"`.

4. **`human_review_agent` (Bonus requirement)** ([app/agent.py](./challenge-1-workflows/app/agent.py)):
   - **Role:** Customer Experience Reviewer.
   - **Task:** Presents `{refined_response}` and directly asks the user if the response is adequate or if further adjustments, details, or a different format are needed.

5. **`root_agent` (`SequentialAgent`)**:
   - Manages linear execution, passing state automatically between nodes.

---

### 3. How to Run & Verify

1. **Prerequisites & Setup:**
   ```bash
   cd challenge-1-workflows
   uv sync
   ```

2. **Authentication & Environment:**
   Ensure credentials are authenticated for Google Cloud / Vertex AI platform:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   gcloud config set project <YOUR_PROJECT_ID>
   ```
   Configure `.env` with your project ID:
   ```env
   GOOGLE_GENAI_USE_ENTERPRISE=true
   GOOGLE_CLOUD_PROJECT=<YOUR_PROJECT_ID>
   GOOGLE_CLOUD_LOCATION=global
   ```

3. **Run the Agent Playground:**
   ```bash
   uvx google-agents-cli playground
   ```
   Open the browser interface to test prompts and observe step-by-step agent transitions.

---

### 4. Verification Screenshots

Screenshots demonstrating the multi-agent workflow in the Agent Playground are stored in:
- [`challenge-1-workflows/screenshots/`](./challenge-1-workflows/screenshots/)
  - `1.png` - Input prompt & initial agent dispatch
  - `2.png` - Research agent execution & state capture
  - `3.png` - Validation critique & gap analysis
  - `4.png` - Refinement synthesis incorporating feedback
  - `5.png` - Human adequacy confirmation prompt
