"""ADS Storm Response LLM-as-a-judge metric."""

import os
import threading
from pydantic import BaseModel
from google import genai
from google.genai import types

PROJECT_ID = "qwiklabs-gcp-02-709a6796d69a"
LOCATION = "global"

os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_GENAI_USE_ENTERPRISE"] = "true"

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
    """Grades ADS storm response agent accuracy, policy compliance, and dispatch logic."""
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
        "Grade the Alaska Department of Snow (ADS) agent response on a 1-5 scale:\n"
        "5 - Completely accurate, correctly executes or reflects telemetry/policy, highly operational and precise.\n"
        "4 - Mostly accurate with minor phrasing omission.\n"
        "3 - Partially correct, misses specific telemetry figures or policy thresholds.\n"
        "2 - Inaccurate or conflicting telemetry/policy stated.\n"
        "1 - Completely wrong, failed to route or hallucinated numbers."
    )

    prompt = (
        f"You are an expert evaluator grading Alaska Department of Snow storm operations.\n{rubric}\n\n"
        f"Operator Prompt: {prompt_val}\n"
        f"Agent Response: {response_val}\n"
        f"Expected Reference: {reference_val}\n"
        f"Agent Trace: {agent_data_val}\n"
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
        return {"score": 3, "explanation": f"Evaluation fallback: {e}"}
