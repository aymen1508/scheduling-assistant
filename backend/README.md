# Backend - Voice Assistant (FastAPI + Python)

## Quick Start

### Installation
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Development
```bash
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Environment Variables

Create a `.env` file in the project root:

```env
# Azure VoiceLive Configuration
AZURE_VOICELIVE_ENDPOINT=https://your-endpoint.services.ai.azure.com/
AZURE_VOICELIVE_AGENT_ID=your-agent-name:version
AZURE_VOICELIVE_PROJECT_NAME=your-project-name
AZURE_VOICELIVE_CONVERSATION_ID=optional-conversation-id
AZURE_VOICELIVE_FOUNDRY_RESOURCE_OVERRIDE=optional
AZURE_VOICELIVE_AUTH_IDENTITY_CLIENT_ID=optional

# Application Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000
RELOAD=True

# Logging
LOG_LEVEL=INFO
LOG_DIR=logs

# CORS
CORS_ORIGINS=*
```

## Project Structure

```
backend/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py      # Configuration management
│   │   ├── logger.py        # Logging utilities
│   │   └── prompts.py       # System prompts
│   ├── services/
│   │   ├── __init__.py
│   │   └── voicelive.py     # VoiceLive API integration
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── messages.py      # WebSocket message handling
│   │   └── voice_session.py # Session management
│   ├── utils/
│   │   └── __init__.py
│   ├── __init__.py
│   └── main.py              # FastAPI application
├── requirements.txt
└── README.md
```

## API Endpoints

### Health Check
```
GET /health
Response: {"status": "ok", "version": "2.0.0"}
```

### WebSocket Connection
```
WS /ws/voice
```

#### Message Types

**Audio Input**
```json
{
  "type": "audio",
  "data": "base64_encoded_pcm16_audio"
}
```

**Close Connection**
```json
{
  "type": "close"
}
```

#### Response Messages

**Status**
```json
{
  "type": "status",
  "data": "Connected. Listening for voice input..."
}
```

**Chat**
```json
{
  "type": "chat",
  "data": {
    "role": "assistant",
    "content": "Hello! How can I help?"
  }
}
```

**Audio Output**
```json
{
  "type": "audio",
  "data": "base64_encoded_pcm16_audio"
}
```

**Error**
```json
{
  "type": "error",
  "data": "Error description"
}
```

## Audio Format

- **Format**: PCM16 (Signed 16-bit PCM)
- **Sample Rate**: 24000 Hz
- **Channels**: 1 (Mono)
- **Encoding**: Base64 when transmitted over WebSocket

## Features

✅ Real-time bidirectional audio streaming
✅ Azure VoiceLive integration
✅ Automatic MCP tool approval
✅ Robust error handling
✅ Comprehensive logging
✅ WebSocket connection management
✅ Audio buffer management
✅ CORS support

## Technologies

- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Azure AI VoiceLive** - Voice conversation API
- **WebSocket** - Real-time bidirectional communication
- **Python 3.9+** - Programming language

## Troubleshooting

### Connection Issues
1. Verify .env file has correct Azure credentials
2. Check if Azure CLI is authenticated: `az account show`
3. Ensure backend is running: Check logs for startup errors

### Audio Issues
1. Frontend audio buffer size must be power of 2 (2048 recommended)
2. Sample rate must match: 24000 Hz
3. Check audio format is PCM16

### CORS Errors
1. Ensure `CORS_ORIGINS` includes frontend URL
2. For development, set `CORS_ORIGINS=*` (not for production)

## Deployment

See [DEPLOYMENT.md](../DEPLOYMENT.md) for Azure deployment instructions.
