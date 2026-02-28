# Backend Deployment Guide

## Prerequisites

1. **Docker installed** - [Download Docker Desktop](https://www.docker.com/products/docker-desktop)
2. **Azure CLI installed** - [Download Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
3. **Azure subscription** with credits
4. **GitHub repo** (optional, for CI/CD later)

## Step 1: Create Azure Container Registry

```bash
# Login to Azure
az login

# Create resource group
az group create --name vikara-rg --location eastus

# Create container registry
az acr create \
  --resource-group vikara-rg \
  --name vikararegistry \
  --sku Basic
```

**Save the registry name** - you'll use it in the build script.

## Step 2: Build and Push Docker Image

### Option A: Using Windows Batch File
```bash
# Edit build-and-push.bat - change REGISTRY_NAME to your registry
build-and-push.bat
```

### Option B: Using Linux/Mac Shell Script
```bash
# Edit build-and-push.sh - change REGISTRY_NAME to your registry
chmod +x build-and-push.sh
./build-and-push.sh
```

### Option C: Manual Commands
```bash
# Login to your registry
az acr login --name vikararegistry

# Build image locally
docker build -t vikara-backend:latest -f Dockerfile .

# Tag for Azure
docker tag vikara-backend:latest vikararegistry.azurecr.io/vikara-backend:latest

# Push to Azure
docker push vikararegistry.azurecr.io/vikara-backend:latest
```

**Expected output:**
```
latest: digest: sha256:abc123... size: 5000
```

## Step 3: Deploy to Azure Container Instances

```bash
# Set environment variables for your Azure setup
# First, create the container from the image

az container create \
  --resource-group vikara-rg \
  --name vikara-backend \
  --image vikararegistry.azurecr.io/vikara-backend:latest \
  --registry-login-server vikararegistry.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --ports 8000 \
  --environment-variables \
    AZURE_VOICELIVE_ENDPOINT="your-endpoint" \
    AZURE_VOICELIVE_AGENT_ID="your-agent-id" \
    AZURE_VOICELIVE_PROJECT_NAME="your-project" \
    DEBUG="False" \
    LOG_LEVEL="INFO" \
  --cpu 1 \
  --memory 1 \
  --dns-name-label vikara-backend
```

**Get the public URL:**
```bash
az container show \
  --resource-group vikara-rg \
  --name vikara-backend \
  --query ipAddress.fqdn
```

Output: `vikara-backend.eastus.azurecontainerinstances.io`

## Step 4: Verify Backend is Running

```bash
# Test health endpoint
curl https://vikara-backend.eastus.azurecontainerinstances.io/health
```

Should return:
```json
{"status": "ok", "version": "2.0.0"}
```

## Step 5: Update Frontend with Backend URL

In `frontend-next/.env.production`:
```env
NEXT_PUBLIC_WEBSOCKET_URL=wss://vikara-backend.eastus.azurecontainerinstances.io/ws/voice
```

**Note:** Change `http://` to `wss://` (WebSocket Secure)

## Step 6: IP Whitelisting (Development Only)

Get your public IP:
```powershell
(Invoke-WebRequest -Uri "https://api.ipify.org?format=json").Content | ConvertFrom-Json
```

Add firewall rule:
```bash
az container update \
  --resource-group vikara-rg \
  --name vikara-backend \
  --set ipAddress.ipAddressType=Private \
  # Or use NSG for more control
```

Alternative: Use Azure NSG for more granular control.

## Updating the Backend

Every time you update the backend code:

```bash
# Rebuild
docker build -t vikara-backend:v2 -f Dockerfile .

# Retag and push
docker tag vikara-backend:v2 vikararegistry.azurecr.io/vikara-backend:v2
docker push vikararegistry.azurecr.io/vikara-backend:v2

# Redeploy
az container create \
  --resource-group vikara-rg \
  --name vikara-backend \
  --image vikararegistry.azurecr.io/vikara-backend:v2 \
  --registry-login-server vikararegistry.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  ... (other options)
```

## Environment Variables Reference

| Variable | Required | Example |
|----------|----------|---------|
| `AZURE_VOICELIVE_ENDPOINT` | Yes | `https://your-endpoint.services.ai.azure.com/` |
| `AZURE_VOICELIVE_AGENT_ID` | Yes | `your-agent:version` |
| `AZURE_VOICELIVE_PROJECT_NAME` | Yes | `your-project` |
| `DEBUG` | No | `False` |
| `LOG_LEVEL` | No | `INFO` |

## Monitoring & Logs

```bash
# View logs
az container logs \
  --resource-group vikara-rg \
  --name vikara-backend \
  --follow

# View container details
az container show \
  --resource-group vikara-rg \
  --name vikara-backend
```

## Cost Estimation

- **Container Registry**: ~$5/month (Basic tier)
- **Container Instances**: ~$0.0015/second (1 CPU, 1GB RAM)
  - 24/7 running: ~$38/month
  - Dev usage (5hrs/day): ~$8/month

## Troubleshooting

### Image won't push
```bash
# Verify you're logged in
az acr login --name vikararegistry

# Check image exists locally
docker images | grep vikara-backend
```

### Container won't start
```bash
# Check logs
az container logs --resource-group vikara-rg --name vikara-backend

# Common issue: Missing environment variables
# Make sure all AZURE_VOICELIVE_* vars are set
```

### WebSocket connection fails
- Ensure backend URL is `wss://` not `ws://`
- Check firewall/NSG rules allow port 443
- Verify CORS allows frontend origin

## Next Steps

1. ✅ Get this backend running on ACI
2. Deploy frontend to Static Web Apps
3. Add IP whitelisting
4. Test full flow end-to-end
5. Add shared demo token auth (later)
