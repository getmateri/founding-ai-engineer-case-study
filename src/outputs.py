"""
Output Generation

Generates the required output files for the case study:
- extracted_data.json
- conflicts.json
- user_decisions.json
- term_sheet.md
- execution_log.json
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from .schema import SessionState, TermSheetData
from .rendering import render_term_sheet


def ensure_output_dir(output_dir: str = "out") -> Path:
    """Ensure output directory exists"""
    path = Path(output_dir)
    path.mkdir(exist_ok=True)
    return path


def save_extracted_data(session: SessionState, output_dir: str = "out") -> str:
    """Save extracted_data.json"""
    path = ensure_output_dir(output_dir) / "extracted_data.json"
    
    data = {
        "document_type": session.term_sheet.document_type,
        "extracted_at": session.term_sheet.extracted_at.isoformat(),
        "sections": {}
    }
    
    for section_name in ["parties", "deal_economics", "liquidation_terms", 
                         "governance", "founder_terms", "transaction_terms", "signatures"]:
        section = getattr(session.term_sheet, section_name)
        section_data = {}
        
        for field_name, field in section:
            section_data[field_name] = {
                "value": field.value,
                "source": field.source.model_dump() if field.source else None,
                "confidence": field.confidence,
                "conflicts": [c.model_dump() for c in field.conflicts],
                "found": field.found,
                "derived_from_policy": field.derived_from_policy,
                "user_edited": field.user_edited,
                "reasoning": field.reasoning
            }
        
        data["sections"][section_name] = section_data
    
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    
    return str(path)


def save_conflicts(session: SessionState, output_dir: str = "out") -> str:
    """Save conflicts.json"""
    path = ensure_output_dir(output_dir) / "conflicts.json"
    
    conflicts_list = []
    
    for section_name in ["parties", "deal_economics", "liquidation_terms", 
                         "governance", "founder_terms", "transaction_terms", "signatures"]:
        section = getattr(session.term_sheet, section_name)
        
        for field_name, field in section:
            if field.conflicts:
                conflict_entry = {
                    "field": f"{section_name}.{field_name}",
                    "values": [
                        {"value": field.value, "source": field.source.model_dump() if field.source else "extracted"}
                    ] + [
                        {"value": c.value, "source": c.source.model_dump()}
                        for c in field.conflicts
                    ],
                    "resolution": "user_selected" if field.user_edited else "agent_selected",
                    "resolved_value": field.value,
                    "resolved_at": datetime.now().isoformat() if field.user_edited else None
                }
                conflicts_list.append(conflict_entry)
    
    data = {"conflicts": conflicts_list}
    
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    
    return str(path)


def save_user_decisions(session: SessionState, output_dir: str = "out") -> str:
    """Save user_decisions.json"""
    path = ensure_output_dir(output_dir) / "user_decisions.json"
    
    data = {
        "decisions": [
            {
                "timestamp": d.timestamp.isoformat(),
                "type": d.decision_type,
                "section": d.section,
                "field": d.field,
                "old_value": d.old_value,
                "new_value": d.new_value,
                "reason": d.reason
            }
            for d in session.user_decisions
        ]
    }
    
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    
    return str(path)


def save_term_sheet(session: SessionState, output_dir: str = "out") -> str:
    """Save term_sheet.md"""
    path = ensure_output_dir(output_dir) / "term_sheet.md"
    
    markdown = render_term_sheet(session.term_sheet)
    
    with open(path, "w") as f:
        f.write(markdown)
    
    return str(path)


def save_execution_log(
    session: SessionState, 
    llm_calls: list[dict],
    output_dir: str = "out"
) -> str:
    """Save execution_log.json"""
    path = ensure_output_dir(output_dir) / "execution_log.json"
    
    # Calculate token totals
    input_tokens = sum(c.get("input_tokens", 0) for c in llm_calls)
    output_tokens = sum(c.get("output_tokens", 0) for c in llm_calls)
    
    # GPT-4o pricing: $2.50/1M input, $10/1M output
    estimated_cost = (input_tokens * 0.0000025) + (output_tokens * 0.00001)
    
    data = {
        "session_id": session.session_id,
        "started_at": session.created_at.isoformat(),
        "completed_at": datetime.now().isoformat(),
        "final_state": session.agent_state.value,
        "llm_calls": len(llm_calls),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": round(estimated_cost, 4),
        "user_decisions": len(session.user_decisions),
        "conflicts_resolved": len([d for d in session.user_decisions if d.decision_type == "conflict_resolution"]),
    }
    
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    
    return str(path)


def save_all_outputs(
    session: SessionState,
    llm_calls: Optional[list[dict]] = None,
    output_dir: str = "out"
) -> dict[str, str]:
    """Save all required output files"""
    
    llm_calls = llm_calls or []
    
    outputs = {
        "extracted_data": save_extracted_data(session, output_dir),
        "conflicts": save_conflicts(session, output_dir),
        "user_decisions": save_user_decisions(session, output_dir),
        "term_sheet": save_term_sheet(session, output_dir),
        "execution_log": save_execution_log(session, llm_calls, output_dir),
    }
    
    return outputs

