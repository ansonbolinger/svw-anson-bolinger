# Alaska Department of Snow (ADS) - Challenge 6 Evaluation Report

**Case Study:** Agentic Field Operations for Alaska Department of Snow (ADS)  
**Evaluation Framework:** Google ADK Evaluation API (`agents-cli eval run`)  
**Judge Model:** `gemini-2.5-flash` (Domain-grounded LLM-as-a-judge)  
**Overall Performance:** **Mean Score: 4.40 / 5.00** | Pass Rate: **100%**

---

## 1. Executive Summary

This report assesses the performance of the ADS Multi-Agent Operations System across 5 representative winter storm scenarios spanning:
- Live roadside telemetry retrieval via MCP backend tools
- Critical pass closure threshold policy enforcement via RAG
- Heavy rotary snow blower dispatch logic via MCP
- Highway priority clearing SLAs (Priority 1: 24/7 continuous service)
- Public safety travel advisory broadcast color codes (Green, Amber, Red)

---

## 2. Detailed Test Case Evaluation Breakdown

| Case ID | Scenario / Operator Query | Score (1-5) | Result & Evaluation Rationale |
| :--- | :--- | :---: | :--- |
| **`sensor-telemetry-thompson-pass`** | Query wind, snow accumulation, and road status on Thompson Pass | **4.0 / 5.0** | Accurately routed to `field_dispatch_agent`, called `get_highway_sensor_status`, and reported 52 mph winds, 24 in accumulation, and RED_CLOSED status. |
| **`policy-closure-wind-threshold`** | Wind and visibility thresholds for mandatory Thompson Pass closure | **5.0 / 5.0** | Grounded in RAG policy: cited 45+ mph sustained winds, <50 ft visibility, and EXTREME avalanche index. |
| **`dispatch-avalanche-blower`** | Dispatch rotary snow blower to Turnagain Pass MP 63 | **4.0 / 5.0** | Successfully dispatched `BLOWER-BRAVO-05` to Turnagain Pass with operational action `AVALANCHE_CLEAR`. |
| **`corridor-priority-sla`** | Service standard and priority level for Parks Highway (AK-3) | **5.0 / 5.0** | Accurately stated Priority 1 Critical Corridor status with continuous 24/7 clearing and 1.5-inch trigger. |
| **`public-travel-advisory-codes`** | Explanation of RED public travel advisory code | **4.0 / 5.0** | Clearly explained hazardous/closed conditions, travel prohibitions, and emergency convoy exceptions. |

---

## 3. Evaluation Artifacts Reference
- Evaluation Traces: `artifacts/traces/traces_20261120_113403.json`
- Graded Results JSON: `eval_results.json/results_20261120_113446.json`
- Rendered HTML Report: `eval_results.json/results_20261120_113446.html`
