#!/bin/bash

# Configuration
REGISTRY_NAME="vikararegistry"  # Change to your registry name
RESOURCE_GROUP="vikara-rg"      # Change to your resource group
IMAGE_NAME="vikara-backend"
IMAGE_TAG="latest"

echo "=== Building Docker Image ==="
docker build -t $IMAGE_NAME:$IMAGE_TAG -f Dockerfile .

if [ $? -eq 0 ]; then
    echo "✓ Image built successfully"
else
    echo "✗ Build failed"
    exit 1
fi

echo ""
echo "=== Tagging Image for Azure ==="
docker tag $IMAGE_NAME:$IMAGE_TAG $REGISTRY_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG

echo ""
echo "=== Pushing to Azure Container Registry ==="
echo "Make sure you're logged in: az acr login --name $REGISTRY_NAME"
docker push $REGISTRY_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG

if [ $? -eq 0 ]; then
    echo "✓ Image pushed successfully"
    echo ""
    echo "Image URI: $REGISTRY_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG"
else
    echo "✗ Push failed"
    exit 1
fi
