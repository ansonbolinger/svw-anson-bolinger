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

"""Challenge 2: Integrating RAG and Google Search into a Multi-Agent System.

This module implements:
1. rag_search_agent: Answers questions using the proprietary corporate knowledge base
   (Novasphere Dynamics product specs, HR policies, travel reimbursements, IT security).
2. google_search_agent: Answers questions using Google Search for live, external, or up-to-date web knowledge.
3. root_agent: Router agent that determines whether the user inquiry requires internal proprietary RAG
   knowledge or public web search, dispatching to the appropriate specialized sub-agent.
"""

import os
from dotenv import load_dotenv

# Ensure local .env overrides any parent process environment variables
load_dotenv(override=True)

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import google_search, VertexAiSearchTool
from google.genai import types

from app.tools.rag_tool import search_internal_datastore

MODEL = "gemini-2.5-flash"

# Configure RAG tools: checks for optional Vertex AI Search Datastore full resource name,
# and integrates the grounded synthetic knowledge base tool.
rag_tools = [search_internal_datastore]

datastore_id = os.environ.get("VERTEX_AI_SEARCH_DATASTORE_ID")
if datastore_id:
    rag_tools.append(VertexAiSearchTool(data_store_id=datastore_id))


# Sub-Agent 1: Private RAG Knowledge Search Agent
rag_search_agent = Agent(
    name="rag_search_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Answers questions using the private Novasphere Dynamics proprietary datastore and knowledge base.",
    instruction=(
        "You are the internal Novasphere Dynamics RAG Knowledge Assistant.\n"
        "Your role is to accurately answer questions using the private datastore tool.\n"
        "Guidelines:\n"
        "1. Always use the search_internal_datastore tool to retrieve factual knowledge about "
        "Novasphere Dynamics company policies, travel/expense per diems, remote work, IT security, "
        "and proprietary products (like AetherBot v4 and Chronos-Edge Controller).\n"
        "2. Ground your response strictly on the retrieved internal documents.\n"
        "3. If the internal datastore does not contain the answer or the topic is about external web topics, "
        "state that it is not found in the private knowledge base."
    ),
    tools=rag_tools,
)

# Sub-Agent 2: Public Web Google Search Agent
google_search_agent = Agent(
    name="google_search_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Answers questions using live Google Search for current events, public facts, external companies, and general web information.",
    instruction=(
        "You are the Web Intelligence and Google Search Assistant.\n"
        "Your role is to answer questions using live Google Search.\n"
        "Guidelines:\n"
        "1. Use the google_search tool to look up current events, public news, world facts, "
        "external documentation, or general information on the internet.\n"
        "2. Synthesize concise, accurate answers with citations or references where appropriate.\n"
        "3. Do not attempt to answer questions about private Novasphere Dynamics internal policies or unpublished internal products."
    ),
    tools=[google_search],
)

# Root Orchestrator & Router Agent
root_agent = Agent(
    name="challenge_2_rag",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Root coordinator that routes user requests between private RAG search and public Google Search.",
    instruction=(
        "You are the primary Intelligence Router. You direct user questions to the appropriate specialized sub-agent:\n\n"
        "1. Route to 'rag_search_agent' when the user asks about:\n"
        "   - Novasphere Dynamics internal policies, HR rules, remote work, home office stipends\n"
        "   - Travel reimbursements and daily meal per diems\n"
        "   - IT security policies, FIDO2/YubiKey protocols, device requirements\n"
        "   - Proprietary products: AetherBot v4 or Chronos-Edge Controller\n\n"
        "2. Route to 'google_search_agent' when the user asks about:\n"
        "   - Current world news, stock prices, or events\n"
        "   - General technical concepts (e.g., Python, Kubernetes, cloud architectures) not specific to Novasphere internal systems\n"
        "   - Public companies, weather forecasts, or external information\n\n"
        "Always delegate to the specialized sub-agent rather than answering directly."
    ),
    sub_agents=[rag_search_agent, google_search_agent],
)

app = App(
    root_agent=root_agent,
    name="app",
)
