"""
WebSocket message types and handlers
"""

from typing import Any, Callable, Optional
from dataclasses import dataclass
from ..config.logger import log_error


@dataclass
class WebSocketMessage:
    """Represents a WebSocket message"""

    type: str
    data: Any


class MessageHandler:
    """Handles different types of WebSocket messages"""

    def __init__(self):
        self.handlers: dict[str, Callable] = {}

    def register(self, message_type: str, handler: Callable) -> None:
        """Register a handler for a message type"""
        self.handlers[message_type] = handler

    async def handle(self, message: WebSocketMessage) -> None:
        """Handle a message by calling the registered handler"""
        handler = self.handlers.get(message.type)
        if handler:
            await handler(message.data)

    async def send_status(self, websocket: Any, status: str) -> None:
        """Send status message to client"""
        try:
            await websocket.send_json({"type": "status", "data": status})
        except RuntimeError as e:
            if "close message has been sent" in str(e):
                log_error(f"WebSocket already closed: {e}")
            else:
                raise

    async def send_chat(self, websocket: Any, role: str, content: str) -> None:
        """Send chat message to client"""
        try:
            await websocket.send_json({"type": "chat", "data": {"role": role, "content": content}})
        except RuntimeError as e:
            if "close message has been sent" in str(e):
                log_error(f"WebSocket already closed: {e}")
            else:
                raise

    async def send_audio(self, websocket: Any, audio_base64: str) -> None:
        """Send audio chunk to client"""
        try:
            await websocket.send_json({"type": "audio", "data": audio_base64})
        except RuntimeError as e:
            if "close message has been sent" in str(e):
                log_error(f"WebSocket already closed: {e}")
            else:
                raise

    async def send_error(self, websocket: Any, error: str) -> None:
        """Send error message to client"""
        try:
            await websocket.send_json({"type": "error", "data": error})
        except RuntimeError as e:
            if "close message has been sent" in str(e):
                log_error(f"WebSocket already closed: {e}")
            else:
                raise

    async def send_interrupt(self, websocket: Any) -> None:
        """Send interrupt message to client (user started speaking)"""
        try:
            await websocket.send_json({"type": "interrupt"})
        except RuntimeError as e:
            if "close message has been sent" in str(e):
                log_error(f"WebSocket already closed: {e}")
            else:
                raise

    async def send_tool(self, websocket: Any, tool_name: str, tool_server: str, result: str) -> None:
        """Send tool execution result to client"""
        try:
            await websocket.send_json({
                "type": "tool",
                "data": {
                    "toolName": tool_name,
                    "toolServer": tool_server,
                    "result": result
                }
            })
        except RuntimeError as e:
            if "close message has been sent" in str(e):
                log_error(f"WebSocket already closed: {e}")
            else:
                raise
