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
The recall database only contains 19 vehicle models across 5 years (2020-2024). Queries for vehicles outside this set return no results even if NHTSA has recall data for them. The 2021 Toyota Camry and 2022 Honda Civic queries both returned empty results because those specific combinations had no matching records in the database.

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

5. **Implement RAG with Bedrock embeddings** — the current implementation uses direct SQL queries. A proper RAG pipeline with Bedrock embeddings would allow semantic search across recall descriptions, enabling queries like "recalls related to airbag issues" without knowing the exact vehicle.

6. **Add error handling for invalid VINs** — the agent should gracefully handle malformed or fake VINs rather than returning a confusing empty result.

---

## Test Query Results Summary

| Query | Tools Called | Recalls Found | Notes |
|---|---|---|---|
| 2020 Ford F-150 | search_recalls | 5 | All accurate, well formatted |
| VIN 1FTFW1ET5DFC10312 | decode_vin + search_recalls | 0 | 2013 F-150 not in DB range |
| 2021 Toyota Camry | search_recalls | 0 | In DB but no recalls scraped |
| 2022 Honda Civic | search_recalls | 0 | In DB but no recalls scraped |
| 2023 Tesla Model 3 | search_recalls | 1 | Found airbag recall accurately |

---

*Reflection prepared by Saveena Boga | June 2026*
