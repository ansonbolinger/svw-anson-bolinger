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

"""Challenge 5: Deploying an Enterprise Support Agent to Gemini Enterprise.

This agent is configured for deployment to Google Cloud Agent Platform / Reasoning Engine,
exposing customer and employee enterprise operations tools for direct invocation within
the Gemini Enterprise workspace.
"""

from dotenv import load_dotenv
load_dotenv(override=True)

import datetime
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

MODEL = "gemini-2.5-flash"


def check_order_status(order_id: str) -> str:
    """Retrieves real-time fulfillment and tracking status for an enterprise purchase order.

    Args:
        order_id: The order identifier (e.g. ORD-10928, PO-9921).

    Returns:
        Structured shipping and dispatch status.
    """
    clean_id = order_id.strip().upper()
    return (
        f"Order Status for {clean_id}:\n"
        "- Status: IN_TRANSIT (Dispatched from Central Warehouse)\n"
        "- Carrier: FedEx Priority Logistics\n"
        "- Estimated Delivery: Tomorrow by 4:30 PM\n"
        "- Verification: Signed Delivery Required"
    )


def calculate_shipping_tier(weight_lbs: float, destination_zip: str) -> str:
    """Calculates shipping options, carrier transit times, and delivery costs.

    Args:
        weight_lbs: Package weight in pounds.
        destination_zip: 5-digit US delivery zip code.

    Returns:
        Available shipping tiers with estimated costs.
    """
    ground_cost = max(7.99, weight_lbs * 1.25)
    express_cost = max(19.99, weight_lbs * 2.80)
    return (
        f"Shipping Rates to ZIP {destination_zip} for {weight_lbs:.1f} lbs:\n"
        f"1. Standard Ground (3-5 business days): ${ground_cost:.2f}\n"
        f"2. Priority Express (1-2 business days): ${express_cost:.2f}\n"
        "Orders over $50 qualify for free Standard Ground shipping."
    )


def lookup_support_policy(category: str) -> str:
    """Looks up official enterprise warranty, return, and support SLA policies.

    Args:
        category: Policy category (e.g., 'returns', 'warranty', 'cancellation').

    Returns:
        Policy details and service-level agreements.
    """
    cat = category.lower().strip()
    if "return" in cat:
        return (
            "Return Policy: Standard items are eligible for full refund within 30 days of purchase "
            "with receipt. Electronics have a 14-day return window. Final sale items are non-refundable."
        )
    elif "warranty" in cat:
        return (
            "Warranty Policy: Hardware and appliances are covered under a 1-year limited manufacturer "
            "warranty covering parts and defect repair."
        )
    return (
        "Enterprise Support Policy: Standard business hours support available 8 AM - 8 PM EST. "
        "Critical severity tickets have a 1-hour initial response SLA."
    )


root_agent = Agent(
    name="challenge_5_deployment",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""
You are the Enterprise Support Assistant for Gemini Enterprise.
Your mission is to assist employees and enterprise customers with order tracking,
shipping calculations, and official support policy inquiries.

Guidelines:
1. Always use your specialized tools (`check_order_status`, `calculate_shipping_tier`, `lookup_support_policy`)
   to provide factual, up-to-date information.
2. Deliver clear, structured, and professional answers.
3. If an inquiry spans multiple needs (e.g. tracking an order and asking about return policy),
   invoke all relevant tools to provide a complete response.
""",
    tools=[check_order_status, calculate_shipping_tier, lookup_support_policy],
)

app = App(
    root_agent=root_agent,
    name="app",
)
