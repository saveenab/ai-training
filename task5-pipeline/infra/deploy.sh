#!/bin/bash
set -e

FUNCTION_NAME="nhtsa-recall-pipeline"
REGION="us-east-1"
ZIP_FILE="lambda_package.zip"
LAMBDA_DIR="lambda"

echo "=== Building Lambda package ==="

# Clean up old zip
rm -f $ZIP_FILE

# Install dependencies into a temp folder
pip install -r $LAMBDA_DIR/requirements.txt --target ./package --quiet --python-version 3.12 --platform manylinux2014_aarch64 --only-binary=:all:

# Copy lambda code into package
cp $LAMBDA_DIR/*.py ./package/

# Zip everything
cd package
zip -r ../$ZIP_FILE . --quiet
cd ..

# Clean up temp folder
rm -rf package

echo "=== Deploying to AWS Lambda ==="

# Check if function exists — update if yes, create if no
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION > /dev/null 2>&1; then
    echo "Function exists — updating code..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://$ZIP_FILE \
        --region $REGION
else
    echo "Function does not exist — creating..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.12 \
        --role arn:aws:iam::676945141118:role/lambda_execution_role \
        --handler fetch_recalls.handler \
        --zip-file fileb://$ZIP_FILE \
        --timeout 300 \
        --memory-size 256 \
        --region $REGION
fi

echo "=== Done ==="
