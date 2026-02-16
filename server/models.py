"""
Database models for Gus System.
Defines all SQLAlchemy table schemas.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from server.database import Base


class SystemState(Base):
    """
    Stores current system state: mode, volume, battery level.
    Only one row should exist (singleton pattern).
    """
    __tablename__ = "system_state"

    id = Column(Integer, primary_key=True, index=True)
    mode = Column(String(50), default="normal")  # normal, study, privacy, alarm
    volume = Column(Float, default=0.5)  # 0.0 to 1.0
    battery_level = Column(Float, default=100.0)  # 0.0 to 100.0
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class InteractionLogs(Base):
    """
    Logs all user-robot interactions (voice commands and responses).
    Timestamped for historical tracking.
    """
    __tablename__ = "interaction_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    user_text = Column(Text, nullable=False)  # Transcribed user speech
    robot_response = Column(Text, nullable=True)  # AI-generated response
    audio_duration = Column(Float, nullable=True)  # Duration in seconds


class Reminders(Base):
    """
    Stores scheduled reminders/tasks for the robot.
    """
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    time = Column(DateTime(timezone=True), nullable=False, index=True)  # Scheduled time
    task_name = Column(String(255), nullable=False)  # Reminder description
    status = Column(String(50), default="pending")  # pending, completed, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
