#!/bin/bash
gcloud builds submit --tag gcr.io/booming-primer-479412-g9/locust-cloudrun
echo "Successfully build"