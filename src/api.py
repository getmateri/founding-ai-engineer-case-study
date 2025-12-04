"""
FastAPI Server

REST API for the term sheet generation agent.
"""

import os
import uuid
import logging
import traceback
from datetime import datetime
from typing import Optional
from pathlib import Path

# Load .env file before other imports
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .schema import SessionState, AgentState, UserDecision
from .agent import Agent
from .rendering import render_term_sheet
from .outputs import save_all_outputs

# =============================================================================
# LOGGING SETUP
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("api")

# Silence noisy libraries
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)


# =============================================================================
# APP SETUP
# =============================================================================

app = FastAPI(
    title="Document Agent API",
    description="AI-powered document generation with human-in-the-loop",
    version="0.2.0"
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage
sessions: dict[str, SessionState] = {}
agents: dict[str, Agent] = {}


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions and log them"""
    error_id = str(uuid.uuid4())[:8]
    logger.error(f"[{error_id}] Unhandled exception on {request.method} {request.url.path}")
    logger.error(f"[{error_id}] Exception type: {type(exc).__name__}")
    logger.error(f"[{error_id}] Exception message: {str(exc)}")
    logger.error(f"[{error_id}] Traceback:\n{traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Internal server error (id: {error_id}). Check server logs.",
            "error_id": error_id,
            "error_type": type(exc).__name__,
            "error_message": str(exc)
        }
    )


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class DataSourceInfo(BaseModel):
    name: str
    type: str  # "excel", "markdown", "zip", "pdf", "docx"
    size: int
    path: str


class DataDirectoryResponse(BaseModel):
    sources: list[DataSourceInfo]
    document_types: list[str]


class StartGenerationRequest(BaseModel):
    document_type: str = "term_sheet"


class StartGenerationResponse(BaseModel):
    session_id: str
    status: str


class GenerationStatusResponse(BaseModel):
    session_id: str
    status: str  # "loading", "extracting", "complete", "error"
    progress: str  # Human-readable progress message
    current_section: Optional[str] = None
    sections_complete: int = 0
    sections_total: int = 7
    term_sheet: Optional[dict] = None
    preview_markdown: Optional[str] = None
    error: Optional[str] = None


class UpdateFieldRequest(BaseModel):
    session_id: str
    section: str
    field: str
    value: str
    reason: Optional[str] = None


class UpdateFieldResponse(BaseModel):
    success: bool
    message: str
    term_sheet: Optional[dict] = None
    preview_markdown: Optional[str] = None


class FinalizeRequest(BaseModel):
    session_id: str


class FinalizeResponse(BaseModel):
    success: bool
    message: str
    markdown: Optional[str] = None
    outputs: Optional[dict[str, str]] = None


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Log startup info"""
    logger.info("=" * 60)
    logger.info("Document Agent API starting up")
    logger.info("=" * 60)
    
    # Check environment
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        logger.info(f"✓ OPENAI_API_KEY is set (length={len(api_key)})")
    else:
        logger.warning("✗ OPENAI_API_KEY is NOT set!")
    
    # Check data directory
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    if os.path.exists(data_dir):
        logger.info(f"✓ Data directory found: {data_dir}")
        for item in os.listdir(data_dir):
            logger.info(f"  - {item}")
    else:
        logger.warning(f"✗ Data directory not found: {data_dir}")
    
    logger.info("=" * 60)


@app.get("/")
async def root():
    return {"status": "ok", "service": "document-agent"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/data-sources", response_model=DataDirectoryResponse)
async def get_data_sources():
    """Get available data sources from /data directory"""
    logger.info("GET /api/data-sources")
    
    data_dir = Path(__file__).parent.parent / "data"
    sources = []
    
    if data_dir.exists():
        for item in data_dir.iterdir():
            if item.is_file():
                # Determine type
                ext = item.suffix.lower()
                if ext == ".xlsx":
                    file_type = "excel"
                elif ext == ".md":
                    file_type = "markdown"
                elif ext == ".zip":
                    file_type = "zip"
                elif ext == ".pdf":
                    file_type = "pdf"
                elif ext in [".doc", ".docx"]:
                    file_type = "docx"
                else:
                    file_type = "unknown"
                
                sources.append(DataSourceInfo(
                    name=item.name,
                    type=file_type,
                    size=item.stat().st_size,
                    path=str(item)
                ))
    
    return DataDirectoryResponse(
        sources=sources,
        document_types=["term_sheet"]  # Only term sheet for now
    )


@app.post("/api/generate/start", response_model=StartGenerationResponse)
async def start_generation(request: StartGenerationRequest):
    """Start document generation - creates session and begins async extraction"""
    logger.info(f"POST /api/generate/start (type={request.document_type})")
    
    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY not set"
        )
    
    # Create session
    session_id = str(uuid.uuid4())
    session = SessionState(session_id=session_id)
    session.agent_state = AgentState.INIT
    sessions[session_id] = session
    
    # Create agent
    agent = Agent()
    agents[session_id] = agent
    
    logger.info(f"Created session {session_id}")
    
    return StartGenerationResponse(
        session_id=session_id,
        status="created"
    )


@app.post("/api/generate/run/{session_id}", response_model=GenerationStatusResponse)
async def run_generation(session_id: str):
    """Run the generation process - call this after start"""
    logger.info(f"POST /api/generate/run/{session_id}")
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    agent = agents[session_id]
    
    try:
        # Run full extraction
        session.agent_state = AgentState.EXTRACTING
        response = agent.process_message(session, "generate")
        
        # Build response
        term_sheet_dict = _term_sheet_to_dict(session.term_sheet)
        preview_markdown = render_term_sheet(session.term_sheet)
        
        return GenerationStatusResponse(
            session_id=session_id,
            status="complete",
            progress="Extraction complete. Ready for review.",
            sections_complete=7,
            sections_total=7,
            term_sheet=term_sheet_dict,
            preview_markdown=preview_markdown
        )
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        logger.error(traceback.format_exc())
        return GenerationStatusResponse(
            session_id=session_id,
            status="error",
            progress="Generation failed",
            error=str(e)
        )


@app.get("/api/generate/status/{session_id}", response_model=GenerationStatusResponse)
async def get_generation_status(session_id: str):
    """Get current generation status"""
    logger.debug(f"GET /api/generate/status/{session_id}")
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Build response based on state
    if session.agent_state == AgentState.INIT:
        return GenerationStatusResponse(
            session_id=session_id,
            status="loading",
            progress="Initializing...",
            sections_complete=0,
            sections_total=7
        )
    elif session.agent_state == AgentState.EXTRACTING:
        return GenerationStatusResponse(
            session_id=session_id,
            status="extracting",
            progress="Extracting data from sources...",
            sections_complete=0,
            sections_total=7
        )
    elif session.agent_state in [AgentState.REVIEWING, AgentState.COMPLETE]:
        term_sheet_dict = _term_sheet_to_dict(session.term_sheet)
        preview_markdown = render_term_sheet(session.term_sheet)
        return GenerationStatusResponse(
            session_id=session_id,
            status="complete",
            progress="Ready for review",
            sections_complete=7,
            sections_total=7,
            term_sheet=term_sheet_dict,
            preview_markdown=preview_markdown
        )
    else:
        return GenerationStatusResponse(
            session_id=session_id,
            status="unknown",
            progress=f"State: {session.agent_state.value}"
        )


@app.post("/api/update-field", response_model=UpdateFieldResponse)
async def update_field(request: UpdateFieldRequest):
    """Update a specific field in the term sheet"""
    logger.info(f"POST /api/update-field: {request.section}.{request.field}")
    
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[request.session_id]
    agent = agents.get(request.session_id)
    
    if not agent:
        agent = Agent()
        agents[request.session_id] = agent
    
    try:
        success = agent.update_field(
            session,
            request.section,
            request.field,
            request.value,
            request.reason
        )
    except Exception as e:
        logger.error(f"Field update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    if success:
        # Re-render and save
        preview_markdown = render_term_sheet(session.term_sheet)
        
        from .outputs import save_extracted_data, save_conflicts, save_term_sheet
        save_extracted_data(session)
        save_conflicts(session)
        save_term_sheet(session)
        
        return UpdateFieldResponse(
            success=True,
            message=f"Updated {request.section}.{request.field}",
            term_sheet=_term_sheet_to_dict(session.term_sheet),
            preview_markdown=preview_markdown
        )
    else:
        return UpdateFieldResponse(
            success=False,
            message=f"Failed to update {request.section}.{request.field}"
        )


@app.post("/api/finalize", response_model=FinalizeResponse)
async def finalize(request: FinalizeRequest):
    """Finalize and generate all outputs - only allowed when all fields have confidence=1"""
    logger.info(f"POST /api/finalize: {request.session_id}")
    
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[request.session_id]
    agent = agents.get(request.session_id)
    
    # Check all fields have confidence = 1.0
    low_confidence_fields = []
    for section_name in ["parties", "deal_economics", "liquidation_terms", 
                         "governance", "founder_terms", "transaction_terms", "signatures"]:
        section = getattr(session.term_sheet, section_name)
        for field_name, field in section:
            if field.confidence < 1.0:
                low_confidence_fields.append(f"{section_name}.{field_name}")
    
    if low_confidence_fields:
        return FinalizeResponse(
            success=False,
            message=f"Cannot finalize: {len(low_confidence_fields)} fields need review",
        )
    
    # Generate final outputs
    session.agent_state = AgentState.COMPLETE
    markdown = render_term_sheet(session.term_sheet)
    
    # Get LLM calls from agent
    llm_calls = agent.get_llm_calls() if agent else []
    
    outputs = save_all_outputs(
        session,
        llm_calls=llm_calls
    )
    
    return FinalizeResponse(
        success=True,
        message="Document finalized successfully",
        markdown=markdown,
        outputs=outputs
    )


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get current session state"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    return {
        "session_id": session.session_id,
        "agent_state": session.agent_state.value,
        "term_sheet": _term_sheet_to_dict(session.term_sheet) if session.term_sheet else None,
        "conflicts": session.term_sheet.get_all_conflicts() if session.term_sheet else [],
        "user_decisions": [d.model_dump() for d in session.user_decisions],
        "preview_markdown": render_term_sheet(session.term_sheet) if session.term_sheet else None
    }


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    if session_id in sessions:
        del sessions[session_id]
    if session_id in agents:
        del agents[session_id]
    
    return {"success": True}


# =============================================================================
# HELPERS
# =============================================================================

def _term_sheet_to_dict(term_sheet) -> dict:
    """Convert TermSheetData to dict for JSON response"""
    result = {
        "document_type": term_sheet.document_type,
        "extracted_at": term_sheet.extracted_at.isoformat(),
        "sections": {}
    }
    
    for section_name in ["parties", "deal_economics", "liquidation_terms", 
                         "governance", "founder_terms", "transaction_terms", "signatures"]:
        section = getattr(term_sheet, section_name)
        section_dict = {}
        
        for field_name, field in section:
            section_dict[field_name] = {
                "value": field.value,
                "source": field.source.model_dump() if field.source else None,
                "confidence": field.confidence,
                "conflicts": [c.model_dump() for c in field.conflicts],
                "found": field.found,
                "derived_from_policy": field.derived_from_policy,
                "user_edited": field.user_edited,
                "reasoning": field.reasoning,
            }
        
        result["sections"][section_name] = section_dict
    
    return result
