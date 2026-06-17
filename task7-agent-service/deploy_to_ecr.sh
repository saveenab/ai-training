#!/bin/bash
# ECR deployment script for the VIN Recall Agent
# Builds the Docker image, tags it for ECR, and pushes it manually.
# Note: GitHub Actions (.github/workflows/deploy.yml) automates this on every push to main.

set -e

AWS_ACCOUNT_ID="676945141118"
AWS_REGION="us-east-1"
ECR_REPOSITORY="recall-agent"
IMAGE_TAG="latest"
ECR_REGISTRY="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

echo "Authenticating Docker with ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

echo "Building Docker image..."
docker build -t $ECR_REPOSITORY:$IMAGE_TAG .

echo "Tagging image for ECR..."
docker tag $ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG

echo "Pushing image to ECR..."
docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG

echo "Verifying image landed in ECR..."
aws ecr describe-images --repository-name $ECR_REPOSITORY --region $AWS_REGION

echo "Done. Image pushed to: $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG"
