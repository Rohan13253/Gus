"""
API Router for HTTP endpoints.
Handles requests from React frontend (GET /status, POST /command).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from server.database import get_db
from server.models import SystemState, InteractionLogs, Reminders
from server.services.hardware_bridge import execute_frontend_command
from server.services.ai_engine import get_ai_engine

router = APIRouter()


@router.get("/status")
async def get_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get current system status.
    Returns mode, volume, battery_level, and recent interaction count.
    """
    # Get system state (assume single row)
    state = db.query(SystemState).first()
    if not state:
        # Initialize default state if none exists
        state = SystemState()
        db.add(state)
        db.commit()
        db.refresh(state)

    # Get recent interaction count (last 24 hours)
    from datetime import datetime, timedelta
    recent_count = db.query(InteractionLogs).filter(
        InteractionLogs.timestamp >= datetime.utcnow() - timedelta(days=1)
    ).count()

    return {
        "mode": state.mode,
        "volume": state.volume,
        "battery_level": state.battery_level,
        "recent_interactions": recent_count,
        "status": "online"
    }


@router.post("/command")
async def send_command(
    command: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Process commands from the frontend.
    Expected commands: "study_mode", "privacy_mode", "trigger_alarm", "set_volume"
    """
    cmd_type = command.get("type")
    value = command.get("value")

    state = db.query(SystemState).first()
    if not state:
        state = SystemState()
        db.add(state)

    if cmd_type == "study_mode":
        state.mode = "study"
        db.commit()
        await execute_frontend_command("study_mode")
        get_ai_engine().set_mode("study")
        return {"status": "success", "message": "Study mode activated"}

    elif cmd_type == "privacy_mode":
        state.mode = "privacy"
        db.commit()
        await execute_frontend_command("privacy_mode")
        get_ai_engine().set_mode("privacy")
        return {"status": "success", "message": "Privacy mode activated"}

    elif cmd_type == "trigger_alarm":
        state.mode = "alarm"
        db.commit()
        await execute_frontend_command("trigger_alarm")
        get_ai_engine().set_mode("alarm")
        return {"status": "success", "message": "Alarm triggered"}

    elif cmd_type == "set_volume" and value is not None:
        state.volume = max(0.0, min(1.0, float(value)))
        db.commit()
        await execute_frontend_command("set_volume", str(state.volume))
        return {"status": "success", "message": f"Volume set to {state.volume}"}

    elif cmd_type == "normal_mode":
        state.mode = "normal"
        db.commit()
        await execute_frontend_command("normal_mode")
        get_ai_engine().set_mode("normal")
        return {"status": "success", "message": "Normal mode activated"}

    else:
        raise HTTPException(status_code=400, detail=f"Unknown command: {cmd_type}")
