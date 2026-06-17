import json
from agent import run_agent

queries = [
    "What recalls exist for a 2020 Ford F-150?",
    "Can you check recall notices for VIN 1FTFW1ET5DFC10312?",
    "Are there any recalls for a 2021 Toyota Camry?",
    "Check recalls for a 2022 Honda Civic",
    "What safety issues should I know about for a 2023 Tesla Model 3?"
]

results = []
for i, query in enumerate(queries, 1):
    print("Query " + str(i) + " of 5: " + query)
    response = run_agent(query)
    results.append({"query": query, "response": response})

with open("test_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print("All 5 queries complete. Results saved to test_results.json")
