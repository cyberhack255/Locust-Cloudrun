#!/bin/bash

# Configuration Variables
SERVICE_NAME="locust-test-runner"
IMAGE_URL="gcr.io/booming-primer-479412-g9/locust-cloudrun"
REGION="us-central1"
PLATFORM="managed"
PORT="8089"

# Function to deploy the service
deploy_service() {
    echo "🚀 Deploying $SERVICE_NAME to Cloud Run..."
    gcloud run deploy "$SERVICE_NAME" \
        --image "$IMAGE_URL" \
        --platform "$PLATFORM" \
        --region "$REGION" \
        --port "$PORT" \
        --allow-unauthenticated
}

# Function to delete the service
delete_service() {
    echo "⚠️  Deleting $SERVICE_NAME from Cloud Run..."
    gcloud run services delete "$SERVICE_NAME" \
        --platform "$PLATFORM" \
        --region "$REGION" \
        --quiet
}

# Check for arguments
if [ "$1" == "deploy" ]; then
    deploy_service
elif [ "$1" == "delete" ]; then
    delete_service
else
    echo "Usage: $0 {deploy|delete}"
    echo "  deploy  - Deploys the service to Cloud Run on port $PORT"
    echo "  delete  - Deletes the service from Cloud Run"
    exit 1
fi