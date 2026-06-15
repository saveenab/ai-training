import os
import json
import time
import boto3
import numpy as np
import faiss
import psycopg2
from psycopg2.extras import RealDictCursor

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

def get_embedding(text, retries=5):
    for attempt in range(retries):
        try:
            response = bedrock.invoke_model(
                modelId="amazon.titan-embed-text-v1",
                body=json.dumps({"inputText": text[:8000]}),
                contentType="application/json"
            )
            return json.loads(response["body"].read())["embedding"]
        except Exception as e:
            if "Throttling" in str(e) and attempt < retries - 1:
                wait = 10 * (attempt + 1)
                print("Throttled, waiting " + str(wait) + "s...")
                time.sleep(wait)
            else:
                raise

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        dbname=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASS", ""),
        sslmode="require"
    )

def load_and_index_recalls():
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT recall_id, make, model, year, component, description, consequence, remedy FROM recalls")
        records = [dict(r) for r in cur.fetchall()]
    conn.close()
    print("Loaded " + str(len(records)) + " records from RDS")
    chunks = []
    for r in records:
        text = str(r["year"]) + " " + r["make"] + " " + r["model"] + " - " + r["component"] + " - " + r["description"] + " - Consequence: " + r["consequence"] + " - Remedy: " + r["remedy"]
        chunks.append({"text": text, "record": r})
    print("Embedding records with Bedrock Titan...")
    embeddings = []
    for i, chunk in enumerate(chunks):
        emb = get_embedding(chunk["text"])
        embeddings.append(emb)
        time.sleep(2)
        if (i+1) % 25 == 0:
            print("  Embedded " + str(i+1) + "/" + str(len(chunks)))
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    vectors = np.array(embeddings, dtype="float32")
    index.add(vectors)
    print("FAISS index built with " + str(index.ntotal) + " vectors")
    return index, chunks

def semantic_search(index, chunks, query, top_k=5):
    query_emb = np.array([get_embedding(query)], dtype="float32")
    distances, indices = index.search(query_emb, top_k)
    results = []
    for idx in indices[0]:
        if idx != -1:
            results.append(chunks[idx]["record"])
    return results

if __name__ == "__main__":
    index, chunks = load_and_index_recalls()
    results = semantic_search(index, chunks, "Ford F-150 electrical fire recall 2020")
    print("Top results: " + str(len(results)))
    for r in results:
        print("  " + str(r["year"]) + " " + r["make"] + " " + r["model"] + " - " + r["component"])