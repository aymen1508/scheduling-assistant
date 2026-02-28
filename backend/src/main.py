"""
Main application entry point
"""

import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .config.settings import AppConfig
from .config.logger import logger, log_success, log_error, log_info
from .handlers.voice_session import VoiceSession


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handlers"""
    log_success(f"Application started on {AppConfig.HOST}:{AppConfig.PORT}")
    yield
    log_info("Application shutting down")

# Create FastAPI app
app = FastAPI(
    title="Voice Assistant API",
    description="Real-time voice streaming backend for scheduling assistant",
    version="2.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=AppConfig.CORS_ORIGINS,
    allow_credentials=AppConfig.CORS_ALLOW_CREDENTIALS,
    allow_methods=AppConfig.CORS_ALLOW_METHODS,
    allow_headers=AppConfig.CORS_ALLOW_HEADERS,
)

@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint"""
    return {"status": "ok", "version": "2.0.0"}


@app.get("/")
async def root() -> dict:
    """Root endpoint"""
    return {
        "name": "Voice Assistant API",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "websocket": "/ws/voice",
        },
    }


@app.websocket("/ws/voice")
async def websocket_voice(websocket: WebSocket) -> None:
    """WebSocket endpoint for voice streaming"""
    await websocket.accept()
    log_success("WebSocket connection accepted")

    session = VoiceSession(websocket)

    try:
        # Start the voice session
        await session.start()

        # Listen for incoming messages from client
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                message_type = message.get("type")

                if message_type == "audio":
                    audio_data = message.get("data", "")
                    await session.handle_audio(audio_data)

                elif message_type == "end_turn":
                    await session.end_turn()

                elif message_type == "new_conversation":
                    log_info("Received new_conversation message from client")
                    await session.handle_new_conversation()

                elif message_type == "timezone_info":
                    timezone = message.get("timezone", "")
                    log_info(f"Received timezone from client: {timezone}")
                    await session.set_timezone(timezone)

                elif message_type == "close":
                    log_info("Received close message from client")
                    break

                else:
                    log_info(f"Unknown message type: {message_type}")

            except json.JSONDecodeError as e:
                log_error(f"Failed to parse message: {e}")

    except WebSocketDisconnect:
        log_info("Client disconnected")
    except Exception as e:
        log_error(f"WebSocket error: {e}")
    finally:
        await session.close()


# Entry point for development
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=AppConfig.HOST,
        port=AppConfig.PORT,
        reload=AppConfig.RELOAD,
    )
