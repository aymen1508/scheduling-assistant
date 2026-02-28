# 🚀 Getting Started with Voice Assistant 2.0

Welcome! This guide will help you get the Voice Assistant running locally and deployed to Azure.

## What's New in 2.0

✅ **Modern Frontend**: Next.js 15 with TypeScript & Tailwind CSS  
✅ **Better Architecture**: Organized, maintainable backend code  
✅ **Enhanced Features**: Improved UI, better error handling  
✅ **Production Ready**: Docker, deployment guides included  
✅ **Developer Friendly**: Comprehensive documentation  

## 5-Minute Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Azure CLI (optional, for deployment)

### Run Locally

**Windows:**
```bash
start.bat
```

**macOS/Linux:**
```bash
chmod +x start.sh
./start.sh
```

This will:
1. Create virtual environment
2. Install dependencies
3. Start backend on http://localhost:8000
4. Start frontend on http://localhost:3000

### First Use
1. Allow microphone access in browser
2. Click "Start Recording"
3. Speak to the agent
4. Watch the response stream back

## Project Structure

```
voice-assistant/
├── frontend-next/          # Next.js frontend
│   ├── src/
│   │   ├── app/           # Pages and layouts
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom hooks
│   │   ├── lib/           # Utilities
│   │   └── types/         # TypeScript types
│   └── package.json
│
├── backend/                # FastAPI backend
│   ├── src/
│   │   ├── config/        # Configuration
│   │   ├── services/      # Business logic
│   │   ├── handlers/      # WebSocket handlers
│   │   └── main.py        # FastAPI app
│   └── requirements.txt
│
├── start.bat              # Windows quick start
├── start.sh               # macOS/Linux quick start
├── docker-compose.yml     # Local Docker setup
├── .env.example           # Configuration template
└── README.md              # This file
```

## Configuration

### Backend Setup (.env)

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your Azure credentials
AZURE_VOICELIVE_ENDPOINT=https://your-endpoint.services.ai.azure.com/
AZURE_VOICELIVE_AGENT_ID=your-agent-name:version
AZURE_VOICELIVE_PROJECT_NAME=your-project-name
```

### Frontend Setup (.env.local)

```bash
cd frontend-next
cp .env.example .env.local

# For local development (default works):
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:8000/ws/voice
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development Workflow

### Backend Development

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run with hot reload
python -m uvicorn src.main:app --reload

# Check health
curl http://localhost:8000/health
```

### Frontend Development

```bash
cd frontend-next

# Run dev server
npm run dev

# Type check
npm run type-check

# Build for production
npm run build
npm start
```

## Common Tasks

### Add a New Backend Endpoint

1. Edit `backend/src/main.py`
2. Add new route
3. Restart server (auto-reload active)

### Add a New Frontend Component

1. Create component in `frontend-next/src/components/`
2. Export from parent component
3. Hot reload active (save = update)

### Debug Issues

**Backend logs:**
```bash
# View logs
tail -f backend/logs/voice_assistant.log

# Or set LOG_LEVEL=DEBUG in .env
```

**Frontend console:**
- Open DevTools (F12)
- Check Console tab for errors
- Check Network tab for WebSocket

### View Database/Logs

```bash
# Backend logs
ls -la backend/logs/

# Docker logs
docker-compose logs -f backend
```

## Testing

### Test Backend Health

```bash
curl http://localhost:8000/health
# Response: {"status": "ok", "version": "2.0.0"}
```

### Test WebSocket Connection

```bash
# Install wscat: npm install -g wscat
wscat -c ws://localhost:8000/ws/voice

# Send test audio message:
{"type": "audio", "data": "base64_audio_here"}
```

### Test Frontend

Open http://localhost:3000 in browser:
1. Should connect automatically
2. Click "Start Recording"
3. Speak something
4. Should see responses

## Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Should be 3.9+

# Try clearing and reinstalling
rm -rf backend/venv
python -m venv backend/venv
pip install -r backend/requirements.txt

# Check Azure credentials
az account show
```

### Frontend won't connect

```bash
# Check backend is running
curl http://localhost:8000/health

# Check WebSocket URL in .env.local
# Should be ws://localhost:8000/ws/voice (for local)

# View browser console for errors
# View Network tab to see WebSocket connection
```

### Docker won't build

```bash
# Clear cache
docker system prune -a

# Rebuild
docker-compose build --no-cache

# Check Dockerfile
# Ensure correct paths
```

### Audio not working

```bash
# Check browser permissions
# Allow microphone access when prompted

# Check browser console for errors
# Check backend logs for audio processing errors

# Verify sample rate: 24kHz
# Verify format: PCM16
```

## Deployment

### Deploy to Azure

```bash
# See DEPLOYMENT_GUIDE.md for detailed instructions

# Quick: Using Azure Container Instances
bash scripts/deploy-to-aci.sh

# Or: Using Azure App Service
az webapp create --resource-group <rg> --plan <plan> --name <name>
```

### Deploy with Docker

```bash
# Build image
docker build -f Dockerfile.backend -t voice-assistant .

# Run locally
docker run -p 8000:8000 voice-assistant

# Or with docker-compose
docker-compose up --build
```

## Next Steps

1. **Customize the prompt**: Edit `backend/src/config/prompts.py`
2. **Add tools/functions**: Extend VoiceLive agent
3. **Style the UI**: Modify Tailwind config
4. **Deploy**: Follow DEPLOYMENT_GUIDE.md
5. **Monitor**: Set up logging and alerts

## Architecture Overview

```
User Browser
    ↓
Next.js Frontend (React)
    ↓
WebSocket Connection
    ↓
FastAPI Backend (Python)
    ↓
Azure VoiceLive API
    ↓
Process & Respond
    ↓
Stream Back (WebSocket)
    ↓
Display & Play Audio
```

## File Descriptions

### Frontend Key Files

- **src/app/page.tsx** - Main page
- **src/hooks/useVoiceAssistant.ts** - Main hook (WebSocket + audio)
- **src/components/voice/ChatPanel.tsx** - Message display
- **src/lib/audio.ts** - Audio processing utilities

### Backend Key Files

- **src/main.py** - FastAPI app and routes
- **src/services/voicelive.py** - VoiceLive integration
- **src/handlers/voice_session.py** - Session management
- **src/config/settings.py** - Configuration

## Environment Variables Reference

### Backend (.env)

```env
# Azure VoiceLive
AZURE_VOICELIVE_ENDPOINT=https://endpoint.services.ai.azure.com/
AZURE_VOICELIVE_AGENT_ID=agent-name:version
AZURE_VOICELIVE_PROJECT_NAME=project-name

# App Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000
RELOAD=True

# CORS
CORS_ORIGINS=*

# Logging
LOG_LEVEL=INFO
LOG_DIR=logs
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:8000/ws/voice
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Performance Tips

1. **Audio**: Use 2048 sample buffer (power of 2)
2. **Backend**: Deploy to region closer to users
3. **Frontend**: Enable browser caching
4. **Monitoring**: Use Application Insights

## Security Notes

- 🔒 Never commit .env files
- 🔒 Use Azure Key Vault for secrets
- 🔒 Restrict CORS origins in production
- 🔒 Use HTTPS/WSS for production
- 🔒 Implement rate limiting

## Getting Help

1. Check the [README.md](README_REVAMP.md) for architecture details
2. See [Backend README](backend/README.md) for API docs
3. See [Frontend README](frontend-next/README.md) for frontend guide
4. Check logs: `backend/logs/voice_assistant.log`
5. Enable debug mode: `DEBUG=True` in .env

## Support

- 📝 Check documentation in each directory
- 🐛 Review error logs
- 🔍 Inspect browser DevTools
- ⚙️ Verify Azure credentials

---

**Ready to get started?**

```bash
# Clone/download project
cd voice-assistant

# Run quick start
./start.sh  # macOS/Linux
# or
start.bat   # Windows

# Open in browser
open http://localhost:3000
```

**Version**: 2.0.0  
**Status**: Production Ready ✅
