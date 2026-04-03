"""
Pydantic models for request/response validation and SQLAlchemy models for database.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


# ===== Menu Models =====
class MenuItem(BaseModel):
    """A single menu item."""

    name: str
    description: str
    price: float = Field(gt=0, description="Price must be positive")


class MenuCategory(BaseModel):
    """Menu items organized by category."""

    starters: list[MenuItem]
    mains: list[MenuItem]
    desserts: list[MenuItem]
    drinks: list[MenuItem]


# ===== Chat Models =====
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(..., min_length=1, max_length=500, description="Customer message")
    session_id: Optional[str] = Field(None, description="Session identifier")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str
    session_id: str
    restaurant: str


# ===== Health Check =====
class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    environment: str
    database: str
    version: str = "1.0.0"


# ===== Database Models (SQLAlchemy) =====
class DBSession(Base):
    """Database model for conversation sessions."""

    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True)  # UUID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to messages
    messages = relationship("DBMessage", back_populates="session", cascade="all, delete-orphan")


class DBMessage(Base):
    """Database model for conversation messages."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    role = Column(String(10), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationship to session
    session = relationship("DBSession", back_populates="messages")
