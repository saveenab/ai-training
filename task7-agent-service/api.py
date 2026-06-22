import os
import json
import time
import logging
import anthropic
import boto3
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from tools import decode_vin, search_recalls
from rag import load_and_index_recalls, semantic_search

# Structured JSON logger
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage()
        }
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        return json.dumps(log_data)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("recall-agent")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# CloudWatch client
cloudwatch = boto3.client("cloudwatch", region_name="us-east-1")

def publish_metrics(latency_ms: int, is_error: bool):
    cloudwatch.put_metric_data(
        Namespace="RecallAgent",
        MetricData=[
            {"MetricName": "RequestCount", "Value": 1, "Unit": "Count"},
            {"MetricName": "Latency", "Value": latency_ms, "Unit": "Milliseconds"},
            {"MetricName": "ErrorCount", "Value": 1 if is_error else 0, "Unit": "Count"}
        ]
    )

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
            text = next((b.text for b in response.content if hasattr(b, "text")), "")
            return text, response.usage.input_tokens, response.usage.output_tokens

        else:
            return "Agent could not complete the request.", 0, 0

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/query", response_model=QueryResponse)
def query_agent(request: QueryRequest):
    start = time.time()
    error_message = None

    try:
        answer, input_tokens, output_tokens = run_agent(request.query)
        is_error = False
    except Exception as e:
        answer = "An error occurred processing your request."
        error_message = str(e)
        input_tokens, output_tokens = 0, 0
        is_error = True

    latency_ms = int((time.time() - start) * 1000)

    logger.info("request", extra={"extra": {
        "query": request.query,
        "latency_ms": latency_ms,
        "model": "claude-sonnet-4-6",
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "error": error_message
    }})

    try:
        publish_metrics(latency_ms, is_error)
    except Exception as e:
        logger.warning("cloudwatch_publish_failed", extra={"extra": {"reason": str(e)}})

    if is_error:
        return JSONResponse(status_code=500, content={"error": error_message})

    return QueryResponse(
        response=answer,
        latency_ms=latency_ms,
        model="claude-sonnet-4-6"
    )