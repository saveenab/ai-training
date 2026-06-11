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
pip install -r $LAMBDA_DIR/requirements.txt --target ./package --quiet

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
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION >