# Frontend - Voice Assistant (Next.js)

## Quick Start

### Installation
```bash
cd frontend-next
npm install
```

### Development
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000)

### Production Build
```bash
npm run build
npm start
```

### Type Checking
```bash
npm run type-check
```

### Linting
```bash
npm run lint
```

## Environment Variables

Create a `.env.local` file:
```env
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:8000/ws/voice
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production:
```env
NEXT_PUBLIC_WEBSOCKET_URL=wss://your-domain.com/ws/voice
NEXT_PUBLIC_API_URL=https://your-domain.com/api
```

## Project Structure

```
src/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Main page
│   └── globals.css        # Global styles
├── components/
│   └── voice/
│       ├── ChatPanel.tsx      # Chat display component
│       ├── RecordButton.tsx   # Record button with states
│       ├── ClearButton.tsx    # Clear chat button
│       └── StatusIndicator.tsx # Connection status
├── hooks/
│   └── useVoiceAssistant.ts  # Main hook for WebSocket and audio
├── lib/
│   ├── audio.ts            # Audio processing utilities
│   └── logger.ts           # Logging utilities
└── types/
    └── index.ts            # TypeScript interfaces
```

## Features

✅ Real-time audio streaming
✅ WebSocket connection with auto-reconnect
✅ PCM16 audio format support
✅ Sequential audio playback
✅ Chat message display with timestamps
✅ Connection status indicator
✅ Error handling and display
✅ Responsive mobile-friendly UI
✅ Dark mode support via Tailwind

## Technologies

- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Web Audio API** - Audio handling
- **WebSocket** - Real-time communication
