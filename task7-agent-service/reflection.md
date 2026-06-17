# Task 6 — Agent Reflection Document
## Saveena Boga | Computing Concepts Inc. | June 2026

---

## Agent Purpose
The agent takes a vehicle VIN or natural language query, decodes the VIN to identify make/model/year using the NHTSA VIN decoder API, searches the RDS recall database for matching records, and returns a structured summary of open recalls with recommended next steps.

---

## What Worked

**Tool calling worked correctly every time.**
Claude consistently identified which tool to call and in what order. For VIN queries, it always called decode_vin first, then search_recalls with the decoded vehicle info. For natural language queries, it called search_recalls directly. No manual orchestration was needed.

**Real data returned accurate results.**
The 2020 Ford F-150 query returned 5 real NHTSA recall records from RDS with accurate recall IDs, component names, consequences, and remedies. The data matched what is publicly available on NHTSA.gov.

**Two-tool pipeline worked end to end.**
The agent successfully chained decode_vin and search_recalls in a single conversation turn, passing the output of one tool as input to the next without any issues.

**Response quality was high for matched vehicles.**
When recalls were found, the agent produced clear, structured summaries that a non-technical vehicle owner could understand and act on.

---

## What Did Not Work / Limitations

**Limited database coverage.**
The recall database only contains 19 vehicle models across 5 years (2020-2024). While the RAG pipeline's semantic search significantly improved recall discovery — finding results for the Toyota Camry, Honda Civic, and Tesla Model 3 that direct SQL queries missed — vehicles completely outside the scraped dataset still return no results. A user with a 2019 Mazda CX-5, for example, would get nothing despite NHTSA having recall data for it.

**No fallback to live NHTSA API.**
When no records are found in RDS, the agent tells the user there are no recalls rather than falling back to query the live NHTSA API. This could mislead users into thinking their vehicle is recall-free when the database simply does not cover it.

**Emojis in responses.**
Claude added emojis to responses which is not appropriate for a production automotive safety tool. The system prompt should explicitly prohibit this.

**No hallucination detected but risk exists.**
The agent did not hallucinate recall data in any of the 5 test queries. However, the risk exists if the user asks about a vehicle not in the database and the agent attempts to generate recall information from memory rather than returning an honest empty result.

**Year field mismatch.**
The database stores year as an integer but the VIN decoder returns it as a string. This required careful type handling and could cause silent failures if not managed correctly.

---

## What I Would Change Before Production

1. **Expand the database** to cover more makes, models, and years. Ideally scrape all NHTSA recall data, not just 19 models.

2. **Add a live NHTSA API fallback** — if no records are found in RDS, query the live NHTSA API before telling the user there are no recalls.

3. **Remove emojis from system prompt** and enforce a professional, plain-text response format appropriate for a safety tool.

4. **Add a confidence disclaimer** — the agent should always tell users to verify on NHTSA.gov regardless of what the database returns, since recalls can be issued at any time.

5. **Save the FAISS index to disk** — currently the RAG pipeline re-embeds all 272 records every time the agent starts, taking approximately 10 minutes. In production, the index should be saved to S3 after the first build and loaded on startup instead of rebuilding from scratch.

6. **Add error handling for invalid VINs** — the agent should gracefully handle malformed or fake VINs rather than returning a confusing empty result.

7. **Add Comprehensive Unit Tests** — complete more than 5 tests that cover invalid VINs, empty results, API failures, and timeouts because a production system would need significantly more coverage before running unsupervised every 24 hours.

    **Missing Tests Include:**
    - Integration tests that hit the real database and API against a test environment
    - Edge case tests for empty VINs, malformed API responses, missing fields, and duplicate records
    - Performance tests to verify the pipeline completes within the Lambda timeout (configured timeout)
    - Data quality tests to validate all required fields are present and dates are correctly formatted

---

## Test Query Results Summary

| Query | Tools Called | Recalls Found | Notes |
|---|---|---|---|
| 2020 Ford F-150 | search_recalls | 5 | All accurate, well formatted |
| VIN 1FTFW1ET5DFC10312 | decode_vin + search_recalls | 0 | 2013 F-150 not in DB date range |
| 2021 Toyota Camry | search_recalls | 1 | Airbag recall found via semantic search |
| 2022 Honda Civic | search_recalls | 2 | Two steering recalls found |
| 2023 Tesla Model 3 | search_recalls | 2 | Battery and Autosteer recalls found |

