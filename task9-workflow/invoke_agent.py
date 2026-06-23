import json
import boto3
import urllib.request

ALB_ENDPOINT = "http://recall-agent-alb-1269439320.us-east-1.elb.amazonaws.com/query"

def lambda_handler(event, context):
    bucket = event["bucket"]
    key = event["key"]
    
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket, Key=key)
    body = json.loads(response["Body"].read().decode("utf-8"))
    
    query = body["query"]
    
    payload = json.dumps({"query": query}).encode("utf-8")
    req = urllib.request.Request(
        ALB_ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    with urllib.request.urlopen(req, timeout=60) as res:
        result = json.loads(res.read().decode("utf-8"))
    
    return {
        "query": query,
        "response": result["response"],
        "latency_ms": result["latency_ms"]
    }
