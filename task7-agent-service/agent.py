import os
import json
import anthropic
from tools import decode_vin, search_recalls
from rag import load_and_index_recalls, semantic_search

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

print("Loading and indexing recall data with Bedrock embeddings...")
rag_index, rag_chunks = load_and_index_recalls()
print("RAG index ready.")

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
                "query": {"type": "string", "description": "Natural language search query e.g. 2020 Ford F-150 electrical recall"}
            },
            "required": ["query"]
        }
    }
]

def run_tool(name, inp):
    if name == "decode_vin":
        return decode_vin(inp["vin"])
    if name == "search_recalls":
        results = semantic_search(rag_index, rag_chunks, inp["query"])
        return results
    return {"error": "unknown tool"}

def run_agent(query):
    print("User: " + query)
    print("-" * 50)
    messages = [{"role": "user", "content": query}]
    system = "You are a vehicle recall assistant. Use your tools to find recall information and provide a clear structured summary with recommended next steps. Do not use emojis."
    while True:
        r = client.messages.create(model="claude-sonnet-4-6", max_tokens=1024, system=system, tools=tools, messages=messages)
        if r.stop_reason == "tool_use":
            results = []
            for b in r.content:
                if b.type == "tool_use":
                    print("Tool: " + b.name + " " + str(b.input))
                    res = run_tool(b.name, b.input)
                    results.append({"type": "tool_result", "tool_use_id": b.id, "content": json.dumps(res, default=str)})
            messages.append({"role": "assistant", "content": r.content})
            messages.append({"role": "user", "content": results})
        elif r.stop_reason == "end_turn":
            response = next((b.text for b in r.content if hasattr(b, "text")), "")
            print("Agent: " + response)
            return response
        else:
            break
    return "Agent could not complete the request."

if __name__ == "__main__":
    run_agent("What recalls exist for a 2020 Ford F-150?")