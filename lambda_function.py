import boto3

def lambda_handler(event, context):
    bucket = event["bucket"]
    key = event["key"]
    
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read().decode("utf-8")
    
    word_count = len(content.split())
    
    return {
        "statusCode": 200,
        "bucket": bucket,
        "key": key,
        "word_count": word_count
    }
