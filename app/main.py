"""
Restaurant AI - FastAPI Application
Main application with all endpoints, logging, and error handling.
"""

import logging
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session as ORMSession

from .config import settings
from .models import ChatRequest, ChatResponse, HealthResponse, DBSession, DBMessage
from .tobi_ai import get_ai_response_with_context
from .menu_data import MENU_DATA
from .database import get_db, init_db

# ===== Logging Configuration =====
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(settings.log_file), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

# ===== FastAPI Application =====
app = FastAPI(
    title="Restaurant AI",
    description="The Common House - AI-powered restaurant ordering system",
    version="1.0.0",
    docs_url="/api/docs" if settings.is_development else None,
    redoc_url="/api/redoc" if settings.is_development else None,
)

# ===== CORS Middleware =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Static Files =====
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ===== Startup/Shutdown Events =====
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting Restaurant AI v1.0.0")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Restaurant: {settings.restaurant_name}")
    logger.info(f"CORS Origins: {settings.allowed_origins_list}")

    # Initialize database
    init_db()
    logger.info("Database initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down Restaurant AI")


# ===== API Endpoints =====


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with basic info."""
    return {
        "status": "running",
        "restaurant": settings.restaurant_name,
        "message": "Tobi is ready to serve you!",
        "version": "1.0.0",
        "docs": "/api/docs" if settings.is_development else None,
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    Used by Docker, Kubernetes, load balancers, etc.
    """
    return HealthResponse(status="healthy", environment=settings.environment, database="n/a", version="1.0.0")


@app.get("/menu", tags=["Menu"])
async def get_menu():
    """Get the full restaurant menu."""
    logger.debug("Menu requested")
    return MENU_DATA


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest, db: ORMSession = Depends(get_db)):
    """
    Chat with Tobi, the AI assistant with conversation history persistence.

    - **message**: Customer's message (1-500 characters)
    - **session_id**: Optional session identifier
    """
    try:
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        session = db.query(DBSession).filter(DBSession.id == session_id).first()

        if not session:
            session = DBSession(id=session_id)
            db.add(session)
            db.commit()
            logger.info(f"Created new session: {session_id}")
        else:
            session.updated_at = datetime.utcnow()
            db.commit()

        # Store user message
        user_message = DBMessage(
            session_id=session.id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        db.commit()

        # Get AI response with conversation history context
        ai_response = await get_ai_response_with_context(
            request.message,
            session.id,
            db
        )

        # Store assistant response
        assistant_message = DBMessage(
            session_id=session.id,
            role="assistant",
            content=ai_response
        )
        db.add(assistant_message)
        db.commit()

        logger.info(f"Chat - Session: {session.id[:8]}..., User: {request.message[:50]}, Response: {ai_response[:50]}")

        return ChatResponse(
            response=ai_response,
            session_id=session.id,
            restaurant=settings.restaurant_name,
        )

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@app.get("/chat/history/{session_id}", tags=["Chat"])
async def get_chat_history(session_id: str, db: ORMSession = Depends(get_db)):
    """
    Get conversation history for a session.

    - **session_id**: Session identifier to retrieve history for
    """
    try:
        messages = db.query(DBMessage).filter(
            DBMessage.session_id == session_id
        ).order_by(DBMessage.timestamp).all()

        if not messages:
            logger.info(f"No history found for session: {session_id[:8]}...")
            return []

        logger.info(f"Retrieved {len(messages)} messages for session: {session_id[:8]}...")

        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]

    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chat history: {str(e)}")


# ===== Main Entry Point =====
if __name__ == "__main__":
    import uvicorn

    logger.info("=" * 60)
    logger.info("Starting Tobi's Restaurant AI...")
    logger.info(f"Server: http://{settings.host}:{settings.port}")
    logger.info(f"Environment: {settings.environment}")
    logger.info("=" * 60)

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
