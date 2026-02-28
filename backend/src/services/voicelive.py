"""
VoiceLive service for Azure AI integration
"""

import asyncio
import base64
from typing import Any, Optional, AsyncGenerator, Dict

from azure.identity.aio import AzureCliCredential
from azure.ai.voicelive.aio import AgentSessionConfig, connect
from azure.ai.voicelive.models import (
    InputAudioFormat,
    Modality,
    OutputAudioFormat,
    RequestSession,
    ServerEventType,
    ItemType,
    MessageItem,
    InputTextContentPart,
    MCPApprovalResponseRequestItem,
    ResponseMCPApprovalRequestItem,
    ServerEventConversationItemCreated,
)

from ..config.settings import AzureVoiceLiveConfig
from ..config.logger import (
    logger,
    log_success,
    log_error,
    log_info,
    log_audio,
    log_chat,
)
from ..config.prompts import get_system_prompt, get_greeting


class VoiceLiveService:
    """Service for managing VoiceLive connections and operations"""

    def __init__(self, timezone_info: Optional[Dict[str, Any]] = None):
        """Initialize VoiceLive service
        
        Args:
            timezone_info: Dictionary with timezone info from geolocation service
        """
        self.connection: Optional[Any] = None
        self.connection_context: Optional[Any] = None
        self.credential: Optional[AzureCliCredential] = None
        self.timezone_info = timezone_info
        self._active_response = False
        self._response_api_done = False
        self._session_initialized = False
        self._audio_buffer_samples = 0  # Track audio buffer size
        self._mcp_tools_in_progress: set[str] = set()  # Track MCP tool execution IDs
        self._mcp_approval_pending = False  # Track if approval was just sent

    async def connect_session(self) -> None:
        """Establish connection to VoiceLive API"""
        try:
            self.credential = AzureCliCredential()

            agent_config: AgentSessionConfig = {  # type: ignore
                "agent_name": AzureVoiceLiveConfig.AGENT_ID,
                "agent_version": (
                    AzureVoiceLiveConfig.AGENT_VERSION
                    if AzureVoiceLiveConfig.AGENT_VERSION
                    else None
                ),
                "project_name": AzureVoiceLiveConfig.PROJECT_NAME,
                "conversation_id": (
                    AzureVoiceLiveConfig.CONVERSATION_ID
                    if AzureVoiceLiveConfig.CONVERSATION_ID
                    else None
                ),
                "foundry_resource_override": (
                    AzureVoiceLiveConfig.FOUNDRY_RESOURCE_OVERRIDE
                    if AzureVoiceLiveConfig.FOUNDRY_RESOURCE_OVERRIDE
                    else None
                ),
                "authentication_identity_client_id": (
                    AzureVoiceLiveConfig.AUTH_IDENTITY_CLIENT_ID
                    if (
                        AzureVoiceLiveConfig.AUTH_IDENTITY_CLIENT_ID
                        and AzureVoiceLiveConfig.FOUNDRY_RESOURCE_OVERRIDE
                    )
                    else None
                ),
            }

            # Create the context manager
            self.connection_context = connect(
                endpoint=AzureVoiceLiveConfig.ENDPOINT,
                credential=self.credential,
                api_version=AzureVoiceLiveConfig.API_VERSION,
                agent_config=agent_config,
            )
            
            # Enter the context and keep it open
            self.connection = await self.connection_context.__aenter__()

            log_success("Connected to VoiceLive API")
        except Exception as e:
            log_error(f"Failed to connect to VoiceLive: {e}")
            raise

    async def setup_session(self) -> None:
        """Configure the session"""
        if not self.connection:
            raise RuntimeError("Connection not established")

        try:
            session_config = RequestSession(
                modalities=[Modality.TEXT, Modality.AUDIO],
                input_audio_format=InputAudioFormat.PCM16,
                output_audio_format=OutputAudioFormat.PCM16,
            )
            await self.connection.session.update(session=session_config)
            log_success("Session configured")
        except Exception as e:
            log_error(f"Failed to setup session: {e}")
            raise

    async def inject_system_prompt(self) -> None:
        """Inject the system prompt"""
        if not self.connection:
            raise RuntimeError("Connection not established")

        try:
            await self.connection.conversation.item.create(
                item=MessageItem(
                    role="system",
                    content=[InputTextContentPart(text=get_system_prompt(self.timezone_info))],
                )
            )
            log_success("System prompt injected")
        except Exception as e:
            log_error(f"Failed to inject system prompt: {e}")
            raise

    async def send_greeting(self) -> None:
        """Send initial greeting"""
        if not self.connection:
            raise RuntimeError("Connection not established")

        try:
            await self.connection.conversation.item.create(
                item=MessageItem(
                    role="system",
                    content=[InputTextContentPart(text=get_greeting())],
                )
            )
            await self.connection.response.create()
            log_success("Initial response requested")
        except Exception as e:
            log_error(f"Failed to send greeting: {e}")
            raise

    async def push_audio(self, audio_base64: str) -> None:
        """Push audio chunk to VoiceLive"""
        if not self.connection:
            log_error("Connection not established")
            return

        try:
            # Track approximate audio buffer size (base64 is ~4/3 of binary, int16 is 2 bytes)
            # Each base64 char ≈ 0.75 bytes → 2 samples at 24kHz
            decoded_size = len(audio_base64) * 3 / 4  # Base64 to bytes
            samples = int(decoded_size / 2)  # int16 is 2 bytes
            self._audio_buffer_samples += samples
            
            await self.connection.input_audio_buffer.append(audio=audio_base64)
        except Exception as e:
            log_error(f"Failed to push audio: {e}")

    async def finalize_user_turn(self) -> None:
        """Commit buffered user audio and request assistant response"""
        if not self.connection:
            log_error("Connection not established for finalize_user_turn")
            return

        # Prevent multiple response.create() calls while one is active
        if self._active_response:
            log_info("Response already active, skipping new response request")
            return

        try:
            # Check if we have meaningful audio (at least 200ms @ 24kHz = 4800 samples)
            if self._audio_buffer_samples < 4800:
                log_info(f"Insufficient audio: {self._audio_buffer_samples} samples (< 4800), skipping turn")
                self._audio_buffer_samples = 0
                return

            # Try to commit audio
            try:
                await self.connection.input_audio_buffer.commit()
            except Exception as commit_err:
                # SDK might reject if buffer is still too small internally
                log_info(f"Commit skipped: {commit_err}")
                self._audio_buffer_samples = 0
                return

            self._audio_buffer_samples = 0
            
            # Request new response (will set _active_response via RESPONSE_CREATED event)
            await self.connection.response.create()
            log_success("User turn finalized and response requested")
            
        except Exception as e:
            self._audio_buffer_samples = 0
            log_error(f"Error in finalize_user_turn: {e}")

    async def stop_playback(self) -> None:
        """Stop current response playback (for interruption handling)"""
        if not self.connection:
            return

        try:
            # Cancel any active response to stop playback
            await self.connection.response.cancel()
            self._active_response = False
            log_info("Response playback stopped for interruption")
        except Exception as e:
            # It's okay if cancel fails (no active response)
            log_info(f"Playback cancel: {e}")

    async def start_playback(self) -> None:
        """Resume playback system (no-op in WebSocket architecture)"""
        log_info("Playback system ready for response streaming")

    async def get_events(self) -> AsyncGenerator[Any, None]:
        """Stream events from VoiceLive connection"""
        if not self.connection:
            raise RuntimeError("Connection not established")

        try:
            async for event in self.connection:
                yield event
        except Exception as e:
            log_error(f"Error processing events: {e}")
            raise

    async def handle_mcp_approval(self, event: Any) -> None:
        """Auto-approve MCP tool calls"""
        if not self.connection:
            return

        try:
            if not isinstance(event, ServerEventConversationItemCreated):
                return
            if not isinstance(event.item, ResponseMCPApprovalRequestItem):
                return

            approval_request = event.item
            request_id = approval_request.id
            if not request_id:
                return

            tool_name = getattr(approval_request, "name", "unknown")
            server_label = getattr(approval_request, "server_label", "unknown")
            
            log_info(f"Auto-approving MCP tool: {tool_name} from {server_label}")

            try:
                # Create and send approval response
                approval_response = MCPApprovalResponseRequestItem(
                    approval_request_id=request_id,
                    approve=True
                )
                await asyncio.wait_for(
                    self.connection.conversation.item.create(item=approval_response),
                    timeout=5.0
                )
                log_success(f"MCP approval sent: {tool_name}")
                
                # Set flag so RESPONSE_DONE handler knows to create new response
                self._mcp_approval_pending = True
                
            except asyncio.TimeoutError:
                log_error(f"MCP approval timeout for {tool_name}")
            except Exception as e:
                log_error(f"Error approving MCP tool {tool_name}: {e}")
                
        except Exception as e:
            log_error(f"Error handling MCP approval: {e}")

    async def close(self) -> None:
        """Close the connection"""
        try:
            if self.connection_context:
                await self.connection_context.__aexit__(None, None, None)
            if self.credential:
                await self.credential.close()
        except Exception as e:
            log_error(f"Error closing VoiceLive connection: {e}")
        log_info("VoiceLive connection closed")
