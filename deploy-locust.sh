#!/bin/bash

# Configuration Variables
BASE_SERVICE_NAME="locust-test-runner"
IMAGE_URL="gcr.io/booming-primer-479412-g9/locust-cloudrun"
REGION="us-central1"
PLATFORM="managed"
PORT="8089"
MEMORY="8Gi"
CPU="8"

# Determine the number of instances (Default to 1 if not provided)
COUNT=${2:-1}

# Function to deploy services in parallel
deploy_service() {
    echo "🚀 Starting parallel deployment of $COUNT instance(s)..."
    
    for ((i=1; i<=COUNT; i++)); do
        CURRENT_SERVICE="${BASE_SERVICE_NAME}-${i}"
        echo "   -> Triggering deploy for: $CURRENT_SERVICE"
        
        # The '&' puts this command in the background to run in parallel
        gcloud run deploy "$CURRENT_SERVICE" \
            --image "$IMAGE_URL" \
            --platform "$PLATFORM" \
            --region "$REGION" \
            --port "$PORT" \
            --memory "$MEMORY" \
            --cpu "$CPU" \
            --allow-unauthenticated & \
    done

    # Wait for all background jobs to finish
    wait
    echo "✅ All deployments completed."
}

# Function to delete services in parallel
delete_service() {
    echo "⚠️  Starting parallel deletion of $COUNT instance(s)..."
    
    for ((i=1; i<=COUNT; i++)); do
        CURRENT_SERVICE="${BASE_SERVICE_NAME}-${i}"
        echo "   -> Triggering delete for: $CURRENT_SERVICE"
        
        gcloud run services delete "$CURRENT_SERVICE" \
            --platform "$PLATFORM" \
            --region "$REGION" \
            --quiet &
    done

    wait
    echo "🗑️  All deletions completed."
}

# Check for arguments
if [ "$1" == "deploy" ]; then
    deploy_service
elif [ "$1" == "delete" ]; then
    delete_service
else
    echo "Usage: $0 {deploy|delete} [number_of_instances]"
    echo "Examples:"
    echo "  $0 deploy 5   # Deploys locust-test-runner-1 through locust-test-runner-5"
    echo "  $0 delete 5   # Deletes locust-test-runner-1 through locust-test-runner-5"
    exit 1
fi