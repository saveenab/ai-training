import os
import json
import anthropic
from tools import decode_vin, search_recalls

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

tools = [
    {"name": "decode_vin", "description": "Decodes a VIN and returns make, model, year.", "input_schema": {"type": "object", "properties": {"vin": {"type": "string"}}, "required": ["vin"]}},
    {"name": "search_recalls", "description": "Searches recall database for a vehicle.", "input_schema": {"type": "object", "properties": {"make": {"type": "string"}, "model": {"type": "string"}, "year": {"type": "string"}}, "required": ["make", "model", "year"]}}
]

def run_tool(name, inp):
    if name == "decode_vin": return decode_vin(inp["vin"])
    if name == "search_recalls": return search_recalls(inp["make"], inp["model"], inp["year"])
    return {"error": "unknown tool"}

def run_agent(query):
    print(f"User: {query}")
    messages = [{"role": "user", "content": query}]
    system = "You are a vehicle recall assistant. Use tools to find recall information and summarise it clearly."
    while True:
        r = client.messages.create(model="claude-sonnet-4-6", max_tokens=1024, system=system, tools=tools, messages=messages)
        if r.stop_reason == "tool_use":
            results = []
            for b in r.content:
                if b.type == "tool_use":
                    print(f"Tool: {b.name} {b.input}")
                    res = run_tool(b.name, b.input)
                    results.append({"type": "tool_result", "tool_use_id": b.id, "content": json.dumps(res, default=str)})
            messages.append({"role": "assistant", "content": r.content})
            messages.append({"role": "user", "content": results})
        elif r.stop_reason == "end_turn":
            print(next((b.text for b in r.content if hasattr(b, "text")), ""))
            return
        else:
            break

if __name__ == "__main__":
    run_agent("What recalls exist for a 2020 Ford F-150?")
