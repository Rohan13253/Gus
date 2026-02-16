"""
Gus System - THE BRAIN (Server)
Entry point for the FastAPI backend server.
Handles initialization, CORS configuration, and router registration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.routers import api_router, websocket_router, hardware_router
from server.database import init_db

# Initialize database on startup
init_db()

# Initialize FastAPI application
app = FastAPI(
    title="Gus IoT Robot Assistant - THE BRAIN",
    description="Backend server for real-time audio processing, AI, and database management",
    version="1.0.0"
)

# Configure CORS for React frontend running on localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router.router, prefix="/api", tags=["api"])
app.include_router(websocket_router.router, prefix="/ws", tags=["websocket"])
app.include_router(hardware_router.router, prefix="", tags=["hardware"])


@app.get("/")
async def root():
    """Root endpoint to verify server is running."""
    return {"message": "Gus System - THE BRAIN is running", "status": "online"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
