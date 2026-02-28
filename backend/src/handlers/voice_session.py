"""
VoiceSession handler for managing client connections
"""

import asyncio
import json
from typing import Any, Optional, Dict

from fastapi import WebSocket

from ..services.voicelive import VoiceLiveService
from ..services.geolocation import GeolocationService
from ..handlers.messages import MessageHandler, WebSocketMessage
from ..config.logger import (
    logger,
    log_success,
    log_error,
    log_warning,
    log_info,
    log_chat,
)
from azure.ai.voicelive.models import ServerEventType, ItemType


class VoiceSession:
    """Manages a voice conversation session"""

    def __init__(self, websocket: WebSocket):
        """Initialize voice session"""
        self.websocket = websocket
        self.service: Optional[VoiceLiveService] = None
        self.message_handler = MessageHandler()
        self._event_processor_task: asyncio.Task | None = None
        self._greeting_sent = False
        self.timezone_info: Optional[Dict[str, Any]] = None
        
        log_info("VoiceSession initialized")

    async def start(self) -> None:
        """Start the voice session"""
        try:
            log_info("Starting voice session...")

            # Initialize VoiceLive service (timezone will be set by client)
            self.service = VoiceLiveService(timezone_info=None)

            # Connect to VoiceLive
            await self.service.connect_session()
            await self.service.setup_session()
            
            # Don't inject system prompt yet - wait for timezone from client

            log_success("Voice session started")

            # Send initial status to client
            await self.message_handler.send_status(
                self.websocket,
                "Ready for voice input",
            )

            # Start processing events in background
            self._event_processor_task = asyncio.create_task(
                self._process_events_loop()
            )
            log_info("Waiting for timezone info from client...")

        except Exception as e:
            log_error(f"Failed to start voice session: {e}")
            try:
                await self.message_handler.send_error(
                    self.websocket, f"Failed to initialize voice session: {str(e)}"
                )
            except:
                pass
            raise

        except Exception as e:
            log_error(f"Failed to start voice session: {e}")
            try:
                await self.message_handler.send_error(
                    self.websocket, f"Failed to initialize voice session: {str(e)}"
                )
            except:
                pass
            raise

        except Exception as e:
            log_error(f"Failed to start voice session: {e}")
            try:
                await self.message_handler.send_error(
                    self.websocket, f"Failed to initialize voice session: {str(e)}"
                )
            except:
                pass
            raise

    async def _process_events_loop(self) -> None:
        """Process VoiceLive events continuously"""
        try:
            async for event in self.service.get_events():
                await self._handle_event(event)
        except asyncio.CancelledError:
            log_info("Event processing cancelled")
        except Exception as e:
            log_error(f"Error in event processing loop: {e}")

    async def _handle_event(self, event: Any) -> None:
        """Handle a VoiceLive event"""
        try:
            event_type = event.type

            # SESSION LIFECYCLE
            if event_type == ServerEventType.SESSION_UPDATED:
                if self.service._session_initialized:
                    return
                self.service._session_initialized = True
                log_success("Session initialized")

            # INTERRUPTION HANDLING - Automatic speech detection
            elif event_type == ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED:
                log_info("User started speaking - interrupting playback")
                await self.service.stop_playback()
                # Notify frontend to stop playback
                await self.message_handler.send_interrupt(self.websocket)

            elif event_type == ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED:
                log_info("User stopped speaking - ready for response")

            # TRANSCRIPTION
            elif event_type == ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED:
                transcript = event.get("transcript", "")
                if transcript:
                    log_chat(f"User: {transcript}")
                    await self.message_handler.send_chat(
                        self.websocket, "user", transcript
                    )

            elif event_type == ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DONE:
                transcript = event.get("transcript", "")
                if transcript:
                    log_chat(f"Agent: {transcript}")
                    await self.message_handler.send_chat(
                        self.websocket, "assistant", transcript
                    )

            # RESPONSE LIFECYCLE
            elif event_type == ServerEventType.RESPONSE_CREATED:
                self.service._active_response = True
                self.service._response_api_done = False
                log_info("Response started")

            elif event_type == ServerEventType.RESPONSE_AUDIO_DELTA:
                if event.delta:
                    import base64
                    audio_base64 = base64.b64encode(event.delta).decode("utf-8")
                    await self.message_handler.send_audio(
                        self.websocket, audio_base64
                    )

            elif event_type == ServerEventType.RESPONSE_DONE:
                # Don't hold response - MCP tools execute AFTER response completes
                self.service._active_response = False
                self.service._response_api_done = True
                log_success("Response completed")
                
                # If MCP approval was just sent, create new response to trigger tool execution
                if self.service._mcp_approval_pending:
                    self.service._mcp_approval_pending = False
                    if self.service.connection:
                        try:
                            await self.service.connection.response.create()
                            log_info("New response created to trigger MCP tool execution")
                        except Exception as e:
                            log_error(f"Failed to create response for MCP execution: {e}")
                else:
                    await self.message_handler.send_status(
                        self.websocket,
                        "Awaiting next input",
                    )

            # MCP TOOL LIST EVENTS
            elif event_type == ServerEventType.MCP_LIST_TOOLS_IN_PROGRESS:
                log_info(f"MCP list tools in progress: {event.item_id}")
            elif event_type == ServerEventType.MCP_LIST_TOOLS_COMPLETED:
                log_success(f"MCP list tools completed: {event.item_id}")
            elif event_type == ServerEventType.MCP_LIST_TOOLS_FAILED:
                log_error(f"MCP list tools failed: {event.item_id}")

            # MCP CALL EXECUTION EVENTS
            elif event_type == ServerEventType.RESPONSE_MCP_CALL_IN_PROGRESS:
                self.service._mcp_tools_in_progress.add(event.item_id)
                log_info(f"MCP call in progress: {event.item_id} ({len(self.service._mcp_tools_in_progress)} pending)")
            elif event_type == ServerEventType.RESPONSE_MCP_CALL_COMPLETED:
                self.service._mcp_tools_in_progress.discard(event.item_id)
                log_success(f"MCP call completed: {event.item_id} ({len(self.service._mcp_tools_in_progress)} remaining)")
                # Note: Azure automatically processes MCP output within the same response
                # No need to create a new response - the agent will speak the result automatically
                    
            elif event_type == ServerEventType.RESPONSE_MCP_CALL_FAILED:
                self.service._mcp_tools_in_progress.discard(event.item_id)
                log_error(f"MCP call failed: {event.item_id} ({len(self.service._mcp_tools_in_progress)} remaining)")

            # CONVERSATION ITEM EVENTS
            elif event_type == ServerEventType.CONVERSATION_ITEM_CREATED:
                item_type = getattr(event.item, "type", None)
                
                if item_type == ItemType.MCP_LIST_TOOLS:
                    server_label = getattr(event.item, "server_label", "unknown")
                    log_info(f"MCP list tools: server={server_label}")
                    
                elif item_type == ItemType.MCP_CALL:
                    server_label = getattr(event.item, "server_label", "unknown")
                    function_name = getattr(event.item, "name", "unknown")
                    log_info(f"MCP call: server={server_label}, function={function_name}")
                    # Send tool call notification to UI
                    await self.message_handler.send_tool(
                        self.websocket,
                        function_name,
                        server_label,
                        f"Executing {function_name}..."
                    )
                    
                elif item_type == ItemType.MCP_APPROVAL_REQUEST:
                    await self.service.handle_mcp_approval(event)

            # ERROR HANDLING
            elif event_type == ServerEventType.ERROR:
                if event.error:
                    message = str(event.error.message)
                    ignored_error_fragments = [
                        "Cancellation failed",
                        "buffer too small",
                    ]
                    if any(fragment in message for fragment in ignored_error_fragments):
                        log_info(f"Ignoring non-critical VoiceLive error: {message}")
                        return

                    log_error(f"VoiceLive error: {message}")
                    await self.message_handler.send_error(
                        self.websocket, message
                    )

        except Exception as e:
            log_error(f"Error handling event: {e}")

    async def handle_new_conversation(self) -> None:
        """Handle new conversation start - send greeting"""
        try:
            if not self.service.connection:
                log_warning("Connection not ready for new conversation")
                return
            
            # Reset greeting flag and send greeting
            self._greeting_sent = False
            await self.service.send_greeting()
            self._greeting_sent = True
            log_success("New conversation started with greeting")
        except Exception as e:
            log_error(f"Failed to start new conversation: {e}")

    async def set_timezone(self, timezone_name: str) -> None:
        """Set user's timezone and inject system prompt once"""
        try:
            if timezone_name:
                log_info(f"Setting timezone to: {timezone_name}")
                self.timezone_info = await GeolocationService.get_timezone_info(timezone_name)
                log_success(f"Timezone set: {self.timezone_info.get('timezone', 'UTC')}")
                
                # Update service with timezone info
                if self.service:
                    self.service.timezone_info = self.timezone_info
                    
                    # Inject system prompt with timezone (only once)
                    if self.service.connection:
                        try:
                            await self.service.inject_system_prompt()
                            log_success("System prompt injected with timezone info")
                        except Exception as e:
                            log_warning(f"Failed to inject system prompt: {e}")
            else:
                log_info("No timezone provided by client")
        except Exception as e:
            log_error(f"Failed to set timezone: {e}")

    async def handle_audio(self, audio_base64: str) -> None:
        """Handle incoming audio from client"""
        try:
            # Send greeting on first audio
            if not self._greeting_sent:
                log_info("Sending greeting...")
                await self.service.send_greeting()
                self._greeting_sent = True

            await self.service.push_audio(audio_base64)
        except Exception as e:
            log_error(f"Failed to handle audio: {e}")

    async def end_turn(self) -> None:
        """Finalize user's spoken turn and request assistant response"""
        try:
            await self.service.finalize_user_turn()
        except Exception as e:
            log_error(f"Failed to end turn: {e}")
            await self.message_handler.send_error(
                self.websocket, "Failed to process audio turn"
            )

    async def close(self) -> None:
        """Close the session"""
        try:
            if self._event_processor_task:
                self._event_processor_task.cancel()
                try:
                    await self._event_processor_task
                except asyncio.CancelledError:
                    pass

            await self.service.close()
            log_info("Voice session closed")
        except Exception as e:
            log_error(f"Error closing session: {e}")
