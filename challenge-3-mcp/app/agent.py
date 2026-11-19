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

"""Challenge 3: Connecting Agents to External Systems with MCP.

This module implements a multi-agent system utilizing:
1. custom_mcp_agent: Connected to our custom FastMCP server exposing local Python tools
   (system diagnostics, cluster resource budget calculation, identifier transformation).
2. google_mcp_agent: Connected to an official Google-provided MCP server
   (@google-cloud/gcloud-mcp) providing Google Cloud CLI integration tools.
3. root_agent: Router agent that directs user inquiries to either the custom local MCP tools
   or the Google Cloud platform MCP tools.
"""

import sys
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Ensure local .env overrides any parent process environment variables
load_dotenv(override=True)

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import McpToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from mcp import StdioServerParameters
from google.genai import types

MODEL = "gemini-2.5-flash"

# Path to the custom FastMCP server script
MCP_SERVER_PATH = str(Path(__file__).resolve().parent.parent / "mcp_server" / "server.py")

# 1. Custom FastMCP Toolset
custom_mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[MCP_SERVER_PATH],
        )
    ),
    tool_filter=["get_system_diagnostics", "calculate_resource_budget", "transform_identifier"],
)

# 2. Google Cloud MCP Toolset
# Use npx.cmd on Windows, or fallback to npx
npx_cmd = shutil.which("npx.cmd") or shutil.which("npx") or "npx"

google_cloud_mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=npx_cmd,
            args=["-y", "@google-cloud/gcloud-mcp"],
        )
    ),
)


# Sub-Agent 1: Custom Diagnostics & Utility Agent (Custom MCP)
custom_mcp_agent = Agent(
    name="custom_mcp_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Uses custom FastMCP tools to perform system diagnostics, calculate cluster budgets, and transform identifiers.",
    instruction=(
        "You are the Custom Diagnostics & Operations Specialist.\n"
        "You have access to a custom FastMCP toolset:\n"
        "- get_system_diagnostics: Check host OS, architecture, status, and UTC timestamp.\n"
        "- calculate_resource_budget: Calculate compute vCPUs, RAM, and estimated monthly cost for a cluster.\n"
        "- transform_identifier: Convert phrases into kebab-case, snake_case, or camelCase identifiers.\n\n"
        "Always use your MCP tools to execute user requests and return structured, informative responses."
    ),
    tools=[custom_mcp_toolset],
)


# Sub-Agent 2: Google Cloud Platform Specialist (Google-provided MCP)
google_mcp_agent = Agent(
    name="google_mcp_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Uses Google-provided @google-cloud/gcloud-mcp tools to inspect Google Cloud resources and configurations.",
    instruction=(
        "You are the Google Cloud Platform Specialist.\n"
        "You utilize the official Google Cloud MCP server (@google-cloud/gcloud-mcp) to inspect GCP configurations, "
        "active projects, services, or run gcloud CLI operations.\n"
        "Use your MCP tools to assist the user with Google Cloud questions."
    ),
    tools=[google_cloud_mcp_toolset],
)


# Root Orchestrator & Router Agent
root_agent = Agent(
    name="challenge_3_mcp",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Root coordinator that routes user requests to either the Custom MCP Agent or the Google Cloud MCP Agent.",
    instruction=(
        "You are the central Operations Router for external system integrations via MCP.\n"
        "Direct requests to the appropriate specialized sub-agent:\n\n"
        "1. Route to 'custom_mcp_agent' when the request is for:\n"
        "   - System diagnostics, platform info, OS specs, or local runtime status\n"
        "   - Cluster compute calculations, RAM estimations, or monthly cloud infrastructure budget estimations\n"
        "   - String/identifier formatting (kebab-case, snake_case, camelCase)\n\n"
        "2. Route to 'google_mcp_agent' when the request is for:\n"
        "   - Google Cloud Platform (GCP) configurations, projects, regions, or gcloud inspection commands\n\n"
        "Always delegate execution to the specialized sub-agent."
    ),
    sub_agents=[custom_mcp_agent, google_mcp_agent],
)

app = App(
    root_agent=root_agent,
    name="app",
)
