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

"""Challenge 6: Alaska Department of Snow (ADS) Agentic Operations Prototype.

A multi-agent system designed for winter storm operations:
1. field_dispatch_agent: Grounded in live backend telemetry and plow dispatch via custom MCP server.
2. policy_advisor_agent: Grounded in ADS winter operations manual, avalanche directives, and road closure rules via RAG.
3. weather_intel_agent: Grounded in live external weather and blizzard forecasts via Google Search.
4. root_agent: Router agent coordinating operator requests from Gemini Enterprise.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import google_search, McpToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from mcp import StdioServerParameters
from google.genai import types

from app.tools.rag_tool import search_ads_policy

MODEL = "gemini-2.5-flash"

# Path to the ADS backend MCP server
ADS_MCP_PATH = str(Path(__file__).resolve().parent.parent / "mcp_server" / "ads_server.py")

# 1. MCP Toolset for live backend telemetry & fleet dispatch
ads_backend_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[ADS_MCP_PATH],
        )
    ),
    tool_filter=["get_highway_sensor_status", "dispatch_plow_unit", "get_fleet_readiness"],
)

# Sub-Agent 1: Field Operations & Dispatch Specialist (MCP)
field_dispatch_agent = Agent(
    name="field_dispatch_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Inspects real-time roadside sensor telemetry (pavement temp, wind, snow accumulation) and dispatches plow, blower, and salt spreader units.",
    instruction=(
        "You are the ADS Field Dispatch Specialist.\n"
        "Your role is to monitor highway conditions and dispatch road maintenance equipment.\n"
        "Guidelines:\n"
        "- Use `get_highway_sensor_status` to query live telemetry for corridors (Seward, Richardson/Thompson Pass, Parks, Glenn).\n"
        "- Use `get_fleet_readiness` to check active unit locations and fuel status.\n"
        "- Use `dispatch_plow_unit` to dispatch Alpha V-plows, Bravo rotary blowers, or Charlie chemical spreaders.\n"
        "Always provide structured, clear dispatch logs and status updates."
    ),
    tools=[ads_backend_toolset],
)

# Sub-Agent 2: Safety & Policy Advisor (RAG Grounding)
policy_advisor_agent = Agent(
    name="policy_advisor_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Advises on official ADS winter maintenance standards, pass closure rules, avalanche risk levels, and emergency public broadcast codes.",
    instruction=(
        "You are the ADS Safety & Policy Advisor.\n"
        "Your role is to ensure all storm operations comply with official Alaska Department of Snow regulations.\n"
        "Guidelines:\n"
        "- Always query `search_ads_policy` to retrieve official directives.\n"
        "- Enforce mandatory pass closure thresholds (e.g. Thompson Pass wind >45 mph or extreme avalanche hazard).\n"
        "- Advise on highway corridor priority response times (Priority 1: continuous 24/7; Priority 2: 6 hours; Priority 3: 24 hours).\n"
        "- Recommend public travel broadcast classifications (Green, Amber, Red)."
    ),
    tools=[search_ads_policy],
)

# Sub-Agent 3: Regional Weather Intelligence (Google Search)
weather_intel_agent = Agent(
    name="weather_intel_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Queries live weather forecasts, winter storm warnings, and regional meteorological conditions using Google Search.",
    instruction=(
        "You are the Regional Weather Intelligence Specialist for Alaska.\n"
        "Your role is to fetch live weather forecasts, blizzard warnings, NOAA advisories, and current conditions across Alaska mountain passes.\n"
        "Always use `google_search` to verify external weather predictions and atmospheric conditions."
    ),
    tools=[google_search],
)

# Root Orchestrator & Router Agent
root_agent = Agent(
    name="challenge_6_dept_of_snow",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Central coordination interface for Alaska Department of Snow storm response operations.",
    instruction=(
        "You are the Alaska Department of Snow (ADS) Central Operations Coordinator.\n"
        "Direct user inquiries to the specialized operational sub-agents:\n\n"
        "1. Route to `field_dispatch_agent` when the operator asks to:\n"
        "   - Check roadside sensor telemetry (pavement temperature, wind speeds, snow accumulation)\n"
        "   - Check plow fleet readiness or fuel levels\n"
        "   - Dispatch plows, blowers, or de-icers to specific mileposts\n\n"
        "2. Route to `policy_advisor_agent` when the operator asks about:\n"
        "   - Official road closure thresholds, avalanche safety directives, or maintenance response SLAs\n"
        "   - Public advisory color codes (Green, Amber, Red)\n"
        "   - Equipment deployment protocols (Alpha V-Plow vs Bravo Rotary Blower)\n\n"
        "3. Route to `weather_intel_agent` when the operator asks about:\n"
        "   - Real-time weather forecasts, external storm warnings, or regional satellite radar data\n\n"
        "Always delegate to the specialized sub-agent to ensure responses are grounded in tools and data."
    ),
    sub_agents=[field_dispatch_agent, policy_advisor_agent, weather_intel_agent],
)

app = App(
    root_agent=root_agent,
    name="app",
)
