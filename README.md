# Gus System - IoT Robot Assistant

A production-ready full-stack IoT system for the Gus robot assistant, consisting of a Python FastAPI backend (THE BRAIN) and a React + Vite frontend (THE FACE).

## Project Structure

```
Gus_System/
├── server/              # THE BRAIN - Python FastAPI backend
│   ├── main.py         # Entry point, FastAPI app initialization
│   ├── database.py     # SQLite database configuration
│   ├── models.py       # Database models (SystemState, InteractionLogs, Reminders)
│   ├── routers/        # API and WebSocket routers
│   ├── services/       # AI engine and audio processing services
│   └── requirements.txt
├── client/             # THE FACE - React + Vite frontend
│   ├── src/
│   │   ├── components/ # React components (StatusCard, LiveLogs, ControlPanel)
│   │   ├── hooks/      # Custom hooks (useGusSocket)
│   │   ├── api/        # API endpoint functions
│   │   └── App.jsx
│   └── package.json
└── shared/             # Shared resources
    └── gus.db          # SQLite database (created on first run)
```

## Quick Start

### Backend Setup (THE BRAIN)

**Option 1: Using the startup script (Recommended)**
```bash
./start_backend.sh
```

**Option 2: Manual setup**

1. From the project root directory, create a virtual environment:
```bash
cd server
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variable for Groq API:
```bash
export GROQ_API_KEY="your-groq-api-key-here"
```

4. Run the server (from project root):
```bash
# From project root:
cd ..
uvicorn server.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python module:
python -m server.main
```

The backend will be available at `http://localhost:8000`

### Frontend Setup (THE FACE)

**Option 1: Using the startup script (Recommended)**
```bash
./start_frontend.sh
```

**Option 2: Manual setup**

1. Navigate to the client directory:
```bash
cd client
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Features

### Backend (THE BRAIN)
- FastAPI REST API with CORS configured for frontend
- WebSocket endpoint (`/ws/audio`) for real-time audio streaming from ESP32
- SQLite database with SQLAlchemy ORM
- Groq AI integration for LLM processing
- Audio processing service for PCM byte streams

### Frontend (THE FACE)
- React + Vite for fast development
- Tailwind CSS + DaisyUI for beautiful UI components
- Real-time WebSocket connection to backend
- Control panel for robot commands
- Matrix-style live logs display
- System status monitoring

## API Endpoints

### HTTP Endpoints
- `GET /api/status` - Get current system status
- `POST /api/command` - Send command to robot (study_mode, privacy_mode, trigger_alarm, set_volume, normal_mode)

### WebSocket Endpoints
- `WS /ws/audio` - Real-time audio stream from ESP32

## Database Models

- **SystemState**: Current mode, volume, battery level
- **InteractionLogs**: Timestamped user-robot interactions
- **Reminders**: Scheduled tasks and reminders

## Development Notes

- The database file (`gus.db`) will be automatically created in the `shared/` folder on first run
- Ensure the backend is running before starting the frontend
- WebSocket connections will automatically reconnect if disconnected
- CORS is configured to allow requests from `localhost:5173`

## Environment Variables

- `GROQ_API_KEY`: Required for AI processing (get from https://console.groq.com/)

## License

MIT
