"""
Agent Logic

Handles document extraction and field updates.
"""

import logging
from datetime import datetime
from typing import Optional
from openai import OpenAI

from .schema import (
    SessionState, AgentState, UserDecision,
    ExtractedField, SourceReference
)
from .extraction import load_source_files, extract_all_sections
from .outputs import save_extracted_data, save_conflicts, save_term_sheet

logger = logging.getLogger("agent")


class Agent:
    """Term sheet generation agent"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        import os
        logger.info("Initializing Agent...")
        api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.error("OpenAI API key not found")
            raise ValueError("OpenAI API key required")
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"
        self.sources: Optional[dict[str, str]] = None
        self.llm_calls: list[dict] = []  # Track LLM calls with token usage
        logger.info(f"Agent initialized (model={self.model})")
    
    def process_message(self, session: SessionState, user_message: str) -> str:
        """Process a user message and return agent response"""
        logger.info(f"Processing message (state={session.agent_state.value})")
        
        # Handle based on current state
        if session.agent_state == AgentState.INIT:
            return self._run_extraction(session)
        elif session.agent_state == AgentState.EXTRACTING:
            return self._run_extraction(session)
        else:
            return "Extraction complete"
    
    def _run_extraction(self, session: SessionState) -> str:
        """Run the extraction process"""
        logger.info("Starting extraction process...")
        
        # Load sources if needed
        if not self.sources:
            logger.info("Loading source files...")
            self.sources = load_source_files("data")
        
        if not self.sources:
            logger.error("No source files found")
            raise ValueError("No source files found in data/ directory")
        
        logger.info(f"Loaded {len(self.sources)} source files")
        
        try:
            # Extract all sections
            logger.info("Calling extract_all_sections...")
            term_sheet, llm_calls = extract_all_sections(
                self.client,
                self.sources,
                self.model
            )
            session.term_sheet = term_sheet
            session.term_sheet.extracted_at = datetime.now()
            self.llm_calls.extend(llm_calls)
            
            # Log token usage
            total_input = sum(c.get("input_tokens", 0) for c in llm_calls)
            total_output = sum(c.get("output_tokens", 0) for c in llm_calls)
            logger.info(f"Extraction completed: {len(llm_calls)} LLM calls, {total_input} input tokens, {total_output} output tokens")
            
            # Save extracted data
            try:
                save_extracted_data(session)
                save_conflicts(session)
                save_term_sheet(session)
                logger.info("Saved outputs to out/")
            except Exception as e:
                logger.warning(f"Failed to save outputs: {e}")
            
            # Move to reviewing state
            session.agent_state = AgentState.REVIEWING
            
            return "Extraction complete"
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise
    
    def get_llm_calls(self) -> list[dict]:
        """Get list of LLM calls with token usage"""
        return self.llm_calls
    
    def update_field(
        self, 
        session: SessionState, 
        section: str, 
        field: str, 
        value: str,
        reason: Optional[str] = None
    ) -> bool:
        """Update a specific field value - sets confidence to 1.0"""
        try:
            section_obj = getattr(session.term_sheet, section)
            field_obj: ExtractedField = getattr(section_obj, field)
            
            old_value = field_obj.value
            field_obj.value = value
            field_obj.user_edited = True
            field_obj.confidence = 1.0  # User edits are always 100% confident
            field_obj.source = SourceReference(file="user_input", location="manual edit")
            field_obj.conflicts = []  # Clear conflicts after user decision
            
            # Log the decision
            session.log_decision(UserDecision(
                decision_type="field_edit",
                section=section,
                field=field,
                old_value=old_value,
                new_value=value,
                reason=reason
            ))
            
            logger.info(f"Updated {section}.{field}: '{old_value}' -> '{value}'")
            return True
            
        except AttributeError as e:
            logger.error(f"Failed to update field: {e}")
            return False
