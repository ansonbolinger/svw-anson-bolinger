# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Challenge 1: Multi-Agent Workflow with ADK.

This module implements a multi-agent system with:
1. research_agent: Explores and structures detailed findings for the user query, saving to state.
2. validation_agent: Analyzes research quality, facts, gaps, and constraints, saving feedback to state.
3. refinement_agent: Synthesizes findings and feedback into a polished, comprehensive response.
4. human_review_agent: (Bonus) Prompts the user to review adequacy and offer feedback.
"""

from google.adk.agents import Agent, SequentialAgent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types
from dotenv import load_dotenv

# Ensure local .env file overrides any inherited process environment variables
load_dotenv(override=True)

MODEL = "gemini-2.5-flash"


def prepare_refinement_instruction(ctx) -> str:
    """Dynamically generates refinement instructions using session state."""
    research_findings = ctx.state.get("research_findings", "No research findings available.")
    validation_feedback = ctx.state.get("validation_feedback", "No validation feedback available.")

    return (
        "You are an expert refinement and synthesis agent.\n\n"
        "Your task is to take the preliminary research findings and the critique/validation feedback "
        "below, address all identified gaps or caveats, and produce a high-quality, structured, "
        "and polished final response for the user.\n\n"
        f"=== RESEARCH FINDINGS ===\n{research_findings}\n\n"
        f"=== VALIDATION & CRITIQUE ===\n{validation_feedback}\n\n"
        "Provide a well-structured, clear, and comprehensive final answer."
    )


# Agent 1: Research Agent
research_agent = Agent(
    name="research_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are a specialized Research Analyst. When given a user request or query:\n"
        "1. Identify the core intent, key concepts, and requirements.\n"
        "2. Break down the topic into factual components, key points, and actionable background.\n"
        "3. Provide a clear, thorough, structured summary of findings.\n"
        "Keep your output factual, objective, and detailed."
    ),
    output_key="research_findings",
)

# Agent 2: Validation Agent
validation_agent = Agent(
    name="validation_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are a rigorous Quality and Validation Specialist.\n"
        "Review the preliminary research findings stored in session state:\n"
        "Research findings:\n"
        "{research_findings}\n\n"
        "Your job is to:\n"
        "1. Verify factual accuracy, completeness, and clarity.\n"
        "2. Identify any missing perspectives, potential inaccuracies, edge cases, or ambiguities.\n"
        "3. Provide constructive, bulleted critique and actionable recommendations for the refinement stage.\n"
        "Be concise, critical, and constructive."
    ),
    output_key="validation_feedback",
)

# Agent 3: Refinement Agent
refinement_agent = Agent(
    name="refinement_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=prepare_refinement_instruction,
    output_key="refined_response",
)

# Agent 4 (Bonus): Human Feedback / Adequacy Check Agent
human_review_agent = Agent(
    name="human_review_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the customer experience reviewer.\n"
        "Present the refined response to the user:\n"
        "{refined_response}\n\n"
        "At the end of the response, ask the user whether this response fully satisfies their request "
        "or if they would like further adjustments, additional details, or a different format."
    ),
)

# Root Workflow: Sequential orchestration of the specialized agents
root_agent = SequentialAgent(
    name="challenge_1_workflows",
    sub_agents=[
        research_agent,
        validation_agent,
        refinement_agent,
        human_review_agent,
    ],
    description="Multi-agent workflow that researches, validates, refines user requests, and asks for user adequacy confirmation.",
)

app = App(
    root_agent=root_agent,
    name="app",
)
