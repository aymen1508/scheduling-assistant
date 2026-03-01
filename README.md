# Vikara Voice Scheduling Assistant

A real-time voice-enabled scheduling assistant that listens to users, understands their scheduling needs in natural conversation, and automatically books meetings on their Google Calendar.

---

## Deployed URL & How to Test

**Live URL:** https://mango-bush-03d547203.2.azurestaticapps.net

**To test:**
1. Open the URL in your browser
2. Click "Start Recording" to begin speaking
3. Speak naturally, for example:
   - "Book a meeting for tomorrow at 2 PM"
   - "Schedule a standup on Friday at 10 AM"
   - "I need a meeting titled Project Review next Monday at 3 PM"
4. The assistant will:
   - Transcribe your speech in real-time
   - Confirm the meeting details with you
   - Automatically book the event on the calendar
5. Click "Stop Recording" when you're done speaking

The assistant works best with natural conversational language. You can speak at normal volume or even whisper and it will pick it up.

---

## Calendar Integration

The assistant uses **MCP (Model Context Protocol)** tools to integrate with Google Calendar and handle timezone conversions.

### Available MCP Tools

**Google Calendar MCP:**
- `Create_an_event()` - Books new meetings on your Google Calendar
- `Update_an_event()` - Modifies existing calendar events
- `List_the_events_on_a_calendar()` - Retrieves scheduled events to check availability and prevent double-booking

**Time MCP:**
- `Convert_time()` - Converts times between different timezones for accurate scheduling

### How It Works

1. **User speaks** their scheduling request (e.g., "Book a meeting tomorrow at 2 PM")
2. **Azure VoiceLive** transcribes the speech in real-time
3. **Assistant processes** the request and extracts meeting details (date, time, title)
4. **Time MCP tool** converts timezone if needed
5. **Google Calendar MCP** checks availability using `List_the_events_on_a_calendar()`
6. **Google Calendar MCP** books the meeting using `Create_an_event()`
7. **Assistant confirms** the booking back to the user via voice

### Authentication

The assistant uses application-level permissions to access and modify the calendar - no user login required. In production, it uses Azure Managed Identity for secure authentication.

### Features

- Automatic timezone detection from browser
- Prevents double-booking by checking existing events
- Handles natural language date/time references (tomorrow, next Friday, etc.)
- Auto-suggests sensible meeting titles if not specified
- Confirms all details before booking

## Logs and Demo

# Demo
You can view the demo using this [Canva demo link](https://www.canva.com/design/DAHCvRa9b9A/fAwDHGSQiRuWwhfwNzWsAw/watch?utm_content=DAHCvRa9b9A&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=hcf31d6414e).

# Logs

Backend Logs:
```pwsh
INFO:     Started server process [33328]
INFO:     Waiting for application startup.
2026-03-01 21:48:28,718 - voice_assistant - INFO - [SUCCESS] Application started on 0.0.0.0:8000
INFO:     Application startup complete.
INFO:     ('127.0.0.1', 54964) - "WebSocket /ws/voice" [accepted]
2026-03-01 21:48:34,757 - voice_assistant - INFO - [SUCCESS] WebSocket connection accepted
2026-03-01 21:48:34,757 - voice_assistant - INFO - [INFO] VoiceSession initialized
2026-03-01 21:48:34,757 - voice_assistant - INFO - [INFO] Starting voice session...
INFO:     connection open
2026-03-01 21:48:37,616 - voice_assistant - INFO - [SUCCESS] Connected to VoiceLive API
2026-03-01 21:48:37,617 - voice_assistant - INFO - [SUCCESS] Session configured
2026-03-01 21:48:37,618 - voice_assistant - INFO - [SUCCESS] Voice session started
2026-03-01 21:48:37,618 - voice_assistant - INFO - [INFO] Waiting for timezone info from client...
2026-03-01 21:48:37,619 - voice_assistant - INFO - [INFO] Received timezone from client: Africa/Tunis
2026-03-01 21:48:37,619 - voice_assistant - INFO - [INFO] Setting timezone to: Africa/Tunis
2026-03-01 21:48:37,665 - voice_assistant - INFO - [SUCCESS] Timezone set: Africa/Tunis
2026-03-01 21:48:37,666 - voice_assistant - INFO - [SUCCESS] System prompt injected
2026-03-01 21:48:37,667 - voice_assistant - INFO - [SUCCESS] System prompt injected with timezone info
2026-03-01 21:48:37,667 - voice_assistant - INFO - [INFO] Sending greeting...
2026-03-01 21:48:37,667 - voice_assistant - INFO - [SUCCESS] Initial response requested
2026-03-01 21:48:38,088 - voice_assistant - INFO - [SUCCESS] Session initialized
2026-03-01 21:48:38,400 - voice_assistant - INFO - [INFO] Response started
2026-03-01 21:48:38,947 - voice_assistant - INFO - [INFO] MCP list tools: server=googleCalendarMCP
2026-03-01 21:48:38,948 - voice_assistant - INFO - [INFO] MCP list tools in progress: mcpl_004f9d00ce48a6bb0069a4a62665d08190ba4e4cb723e9e38e
2026-03-01 21:48:38,948 - voice_assistant - INFO - [INFO] MCP list tools: server=timeMCP
2026-03-01 21:48:38,949 - voice_assistant - INFO - [INFO] MCP list tools in progress: mcpl_004f9d00ce48a6bb0069a4a62667088190b1643484da3aebf2
2026-03-01 21:48:40,939 - voice_assistant - INFO - [SUCCESS] MCP list tools completed: mcpl_004f9d00ce48a6bb0069a4a62667088190b1643484da3aebf2
2026-03-01 21:48:40,939 - voice_assistant - INFO - [SUCCESS] MCP list tools completed: mcpl_004f9d00ce48a6bb0069a4a62665d08190ba4e4cb723e9e38e
2026-03-01 21:48:48,789 - voice_assistant - INFO - [CHAT] Agent: Hello! I’m your scheduling assistant. Could you please tell me your name, the date and time you’d like to book the meeting, and if you have a meeting title in mind? If not, I’ll pick one for you!
2026-03-01 21:48:48,791 - voice_assistant - INFO - [SUCCESS] Response completed
2026-03-01 21:48:59,226 - voice_assistant - INFO - [INFO] User started speaking - interrupting playback
2026-03-01 21:48:59,227 - voice_assistant - INFO - [INFO] Response playback stopped for interruption
2026-03-01 21:48:59,331 - voice_assistant - INFO - [INFO] Ignoring non-critical VoiceLive error: Cancellation failed: no active response found.
2026-03-01 21:49:02,871 - voice_assistant - INFO - [INFO] User stopped speaking - ready for response
2026-03-01 21:49:03,258 - voice_assistant - INFO - [CHAT] User: Hey, this is John and I will book a meeting on Monday at 2:00 PM.
2026-03-01 21:49:03,281 - voice_assistant - INFO - [INFO] Response started
2026-03-01 21:49:06,808 - voice_assistant - INFO - [CHAT] Agent: Thanks, John! Just to confirm, you’d like to book a meeting this coming Monday at 2:00 PM. Would you like to specify a meeting title, or should I choose a default one for you?
2026-03-01 21:49:06,813 - voice_assistant - INFO - [SUCCESS] Response completed
2026-03-01 21:49:14,413 - voice_assistant - INFO - [INFO] User started speaking - interrupting playback
2026-03-01 21:49:14,413 - voice_assistant - INFO - [INFO] Response playback stopped for interruption
2026-03-01 21:49:14,732 - voice_assistant - INFO - [INFO] Ignoring non-critical VoiceLive error: Cancellation failed: no active response found.
2026-03-01 21:49:14,961 - voice_assistant - INFO - [INFO] User stopped speaking - ready for response
2026-03-01 21:49:15,118 - voice_assistant - INFO - [CHAT] User: Go ahead.
2026-03-01 21:49:15,119 - voice_assistant - INFO - [INFO] Response started
2026-03-01 21:49:16,247 - voice_assistant - INFO - [INFO] MCP call: server=googleCalendarMCP, function=List_the_events_on_a_calendar
2026-03-01 21:49:16,249 - voice_assistant - INFO - [INFO] Auto-approving MCP tool: List_the_events_on_a_calendar from googleCalendarMCP with args: {"calendarId":"primary","timeMin":"2026-03-02T00:00:00.000+01:00","timeMax":"2026-03-02T23:59:59.000+01:00"}
2026-03-01 21:49:16,251 - voice_assistant - INFO - [SUCCESS] MCP approval sent: List_the_events_on_a_calendar
2026-03-01 21:49:16,400 - voice_assistant - INFO - [SUCCESS] Response completed
2026-03-01 21:49:16,400 - voice_assistant - INFO - [INFO] New response created to trigger MCP tool execution
2026-03-01 21:49:16,777 - voice_assistant - INFO - [INFO] Response started
2026-03-01 21:49:17,197 - voice_assistant - INFO - [INFO] MCP call in progress: mcp_eIbwdOhvTpCfua5deqcIt (1 pending)
2026-03-01 21:49:19,280 - voice_assistant - INFO - [SUCCESS] MCP call completed: mcp_eIbwdOhvTpCfua5deqcIt (0 remaining)
2026-03-01 21:49:23,254 - voice_assistant - INFO - [CHAT] Agent: John, the calendar already has meetings booked from 2:00 PM to 4:00 PM on Monday. However, there’s availability right before, from 1:00 PM to 2:00 PM, or after 4:00 PM. Would you like to book your meeting at 1:00 PM or 4:00 PM instead?
2026-03-01 21:49:23,255 - voice_assistant - INFO - [SUCCESS] Response completed
2026-03-01 21:49:45,517 - voice_assistant - INFO - [INFO] Received close message from client
2026-03-01 21:49:45,517 - voice_assistant - INFO - [INFO] Event processing cancelled
2026-03-01 21:49:45,519 - voice_assistant - INFO - [INFO] VoiceLive connection closed
2026-03-01 21:49:45,519 - voice_assistant - INFO - [INFO] Voice session closed
```