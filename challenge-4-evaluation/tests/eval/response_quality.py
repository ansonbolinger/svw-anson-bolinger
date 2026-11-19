"""Policy-grounded LLM-as-judge for Cymbal Retail Customer Service."""

import os
import threading
from pydantic import BaseModel
from google import genai
from google.genai import types

PROJECT_ID = "qwiklabs-gcp-02-184746eee247"
LOCATION = "global"

os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_GENAI_USE_ENTERPRISE"] = "true"

CYMBAL_POLICY = """
Cymbal Retail Official Policies:
1. Standard Returns: Items may be returned within 30 days of purchase with receipt for a full refund to the original payment method.
2. Electronics & Smart Devices Exception: Must be returned within 14 days of purchase in original packaging. After 14 days, items are strictly NOT eligible for return or refund.
3. Final Sale & Clearance: Items explicitly designated 'Final Sale' or 'Clearance' cannot be returned, exchanged, or refunded under any circumstances.
4. No-Receipt Returns: Eligible ONLY for merchandise store credit at the lowest recent selling price with photo ID. Cash refunds require an original receipt.
5. Shipping: Free standard shipping on orders over $50. Orders under $50 have a flat $5.99 shipping fee.
6. Warranties: Small appliances and home goods carry a 1-year limited warranty against manufacturer defects.
"""

_local = threading.local()


class _Verdict(BaseModel):
    score: int  # 1-5
    explanation: str


def _client() -> genai.Client:
    client = getattr(_local, "client", None)
    if client is None:
        client = _local.client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    return client


def evaluate(instance):
    """Grades agent response quality against Cymbal retail policies."""
    # Handle dict or object
    if hasattr(instance, "get"):
        prompt_val = instance.get("prompt", "")
        response_val = instance.get("response", "")
        reference_val = instance.get("reference", "")
        agent_data_val = instance.get("agent_data", "")
    else:
        prompt_val = getattr(instance, "prompt", "")
        response_val = getattr(instance, "response", "")
        reference_val = getattr(instance, "reference", "")
        agent_data_val = getattr(instance, "agent_data", "")

    rubric = (
        "Grade the agent's customer service response on a 1-5 scale against the official Cymbal Retail policies:\n"
        f"{CYMBAL_POLICY}\n"
        "Scoring criteria:\n"
        "5 - Completely accurate, strictly complies with policy details and deadlines, highly professional.\n"
        "4 - Mostly accurate, correct policy application with minor omissions in non-critical phrasing.\n"
        "3 - Partially correct, but misses specific policy limits (e.g., forgets 14-day electronic window or fee amounts).\n"
        "2 - Inaccurate policy stated (e.g. allowing return after expiration or promising cash without receipt).\n"
        "1 - Completely wrong, hallucinated policies, or directly contradicts policy rules."
    )

    prompt = (
        f"You are an expert evaluator grading customer service policy compliance.\n{rubric}\n\n"
        f"Customer Inquiry: {prompt_val}\n"
        f"Agent Response: {response_val}\n"
        f"Expected Reference Answer: {reference_val}\n"
        f"Agent Data / Trace: {agent_data_val}\n"
    )

    try:
        response = _client().models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_schema=_Verdict,
            ),
        )
        verdict = response.parsed
        if verdict is None:
            return {"score": 3, "explanation": response.text or "Unable to parse verdict."}
        return {"score": max(1, min(5, verdict.score)), "explanation": verdict.explanation}
    except Exception as e:
        return {"score": 3, "explanation": f"Evaluation error: {e}"}
