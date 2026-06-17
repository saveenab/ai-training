import os
import json
import time
import anthropic
from fastapi import FastAPI
from pydantic import BaseModel
from tools import decode_vin, search_recalls
from rag import load_and_index_recalls, semantic_search

app = FastAPI(title="VIN Recall Agent API")

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

print("Loading and indexing recall data with Bedrock embeddings...")
rag_index, rag_chunks = load_and_index_recalls()
print("RAG index ready. API is starting up.")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str
    latency_ms: int
    model: str

tools = [
    {
        "name": "decode_vin",
        "description": "Decodes a 17-character VIN and returns the make, model, and year.",
        "input_schema": {
            "type": "object",
            "properties": {"vin": {"type": "string"}},
            "required": ["vin"]
        }
    },
    {
        "name": "search_recalls",
        "description": "Searches the recall database using semantic search to find relevant recall notices for a vehicle.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural language search query"}
            },
            "required": ["query"]
        }
    }
]

def run_tool(name, tool_input):
    if name == "decode_vin":
        return decode_vin(tool_input["vin"])
    if name == "search_recalls":
        return semantic_search(rag_index, rag_chunks, tool_input["query"])
    return {"error": "unknown tool"}

def run_agent(user_query):
    messages = [{"role": "user", "content": user_query}]
    system = "You are a vehicle recall assistant. Use your tools to find recall information and provide a clear structured summary with recommended next steps. Do not use emojis."

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = run_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result, default=str)
                    })
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            return next((b.text for b in response.content if hasattr(b, "text")), "")

        else:
            return "Agent could not complete the request."

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/query", response_model=QueryResponse)
def query_agent(request: QueryRequest):
    start = time.time()
    answer = run_agent(request.query)
    latency_ms = int((time.time() - start) * 1000)
    return QueryResponse(
        response=answer,
        latency_ms=latency_ms,
        model="claude-sonnet-4-6"
    )
