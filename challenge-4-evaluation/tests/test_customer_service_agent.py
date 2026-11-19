"""Unit and Integration Tests for Cymbal Retail Customer Service Agent."""

import pytest
from app.agent import root_agent, OPTIMIZED_INSTRUCTION, MODEL
from google.adk.models.llm_request import LlmRequest
from google.genai import types


def test_agent_initialization():
    """Unit Test: Verify root agent configuration, naming, and model."""
    assert root_agent.name == "challenge_4_evaluation"
    assert root_agent.model.model == MODEL
    assert "Cymbal Retail" in OPTIMIZED_INSTRUCTION
    assert "14-DAY LIMIT" in OPTIMIZED_INSTRUCTION
    assert "$50.00" in OPTIMIZED_INSTRUCTION


def test_instruction_policy_coverage():
    """Unit Test: Verify all key policy rules are present in system instructions."""
    policies = [
        "Standard Returns Policy",
        "Electronics & Smart Devices Exception",
        "Final Sale and Clearance Items",
        "Returns Without a Receipt",
        "Shipping Rates & Thresholds",
        "Warranty Coverage",
    ]
    for policy in policies:
        assert policy in OPTIMIZED_INSTRUCTION, f"Missing {policy} in instructions"


@pytest.mark.asyncio
async def test_agent_response_contains_grounded_policy():
    """Integration Test: Verify live agent execution against customer inquiry."""
    # Prompt testing the 14-day electronic boundary check
    req = LlmRequest(
        model=MODEL,
        contents=[
            types.Content(role="user", parts=[types.Part.from_text(text="I bought wireless headphones 20 days ago. Can I return them?")])
        ],
        system_instruction=types.Content(parts=[types.Part.from_text(text=OPTIMIZED_INSTRUCTION)])
    )
    
    text = ""
    async for chunk in root_agent.model.generate_content_async(req):
        if chunk.content and chunk.content.parts:
            for p in chunk.content.parts:
                if p.text:
                    text += p.text
    
    # Assert policy boundary is enforced (headphones ineligible past 14 days)
    assert any(term in text.lower() for term in ["14 day", "14-day", "ineligible", "cannot return", "outside", "past", "not eligible"])
