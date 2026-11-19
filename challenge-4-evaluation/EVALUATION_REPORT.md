# Challenge 4: Agent Evaluation Report

**Agent:** Cymbal Retail Customer Support Assistant  
**Evaluation Framework:** Google ADK Evaluation API (`agents-cli eval`)  
**Judge Model:** `gemini-2.5-flash` (LLM-as-a-judge with policy grounding)  
**Dataset:** 6 Multi-Domain Customer Scenarios (`customer-service-eval.json`)

---

## 1. Executive Summary

| Phase | System Prompt Configuration | Mean Score (1-5) | Pass Rate | Key Deficiencies Identified |
| :--- | :--- | :---: | :---: | :--- |
| **Baseline (Initial)** | Generic instructions without explicit policy rules or constraints | **3.50 / 5.0** | 50% | Hallucinated return deadlines for electronics, asked user for shipping thresholds, omitted photo ID rules. |
| **Optimized (Revised)** | Explicit policy grounding, 14-day electronic return limits, shipping math rules, and ID verification | **5.00 / 5.0** | **100%** | All 6 test scenarios scored 5/5 with zero policy violations. |

**Net Performance Improvement:** **+1.50 Mean Score (+42.8% gain)**

---

## 2. Test Case Breakdown & Comparative Results

| Case ID | User Inquiry | Baseline Score | Optimized Score | Explanation & Impact of Prompt Revision |
| :--- | :--- | :---: | :---: | :--- |
| **`return-standard-within-30-days`** | Return coffee maker 18 days after purchase with receipt. | **5.0** | **5.0** | Both agents correctly applied the standard 30-day return window with receipt. |
| **`return-electronics-exceeded-14-days`** | Return wireless headphones 22 days after purchase. | **2.0** | **5.0** | **Critical Fix:** Baseline wrongly allowed return under 30 days. Revised prompt strictly enforced the 14-day limit for electronics. |
| **`return-final-sale-clearance`** | Return/exchange a jacket marked 'Final Sale Clearance'. | **5.0** | **5.0** | Both correctly stated final sale merchandise is non-refundable. |
| **`return-missing-receipt`** | Gift return without receipt asking for cash. | **3.0** | **5.0** | **Policy Compliance Fix:** Baseline offered store credit but missed the mandatory government photo ID requirement and lowest recent price limit. Revised prompt included all required conditions. |
| **`shipping-free-tier-threshold`** | Cart is \$42; how much more needed for free shipping? | **1.0** | **5.0** | **Math & Grounding Fix:** Baseline asked the user what the free shipping minimum was. Revised prompt computed \$50 - \$42 = \$8.00 exactly. |
| **`warranty-coverage-window`** | Blender stopped working after 8 months. | **5.0** | **5.0** | Accurately confirmed coverage under the 1-year small appliance warranty. |

---

## 3. Evaluation Artifacts & Test Results

1. **Evaluation Traces & Scores:**
   - Baseline Results: `baseline_results.json/results_20261119_154333.json` (Mean: 3.50)
   - Optimized Results: `optimized_eval_results.json/results_20261119_154928.json` (Mean: 5.00)

2. **Automated Unit & Integration Tests (Bonus):**
   - Implemented in `tests/test_customer_service_agent.py`
   - Verification suite passed with 100% success:
     ```
     tests/test_customer_service_agent.py::test_agent_initialization PASSED
     tests/test_customer_service_agent.py::test_instruction_policy_coverage PASSED
     tests/test_customer_service_agent.py::test_agent_response_contains_grounded_policy PASSED
     3 passed in 102.27s
     ```
