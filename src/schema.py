"""
Term Sheet Schema and Types

Defines the structure for extracted fields, sources, and the complete term sheet.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum
from datetime import datetime


# =============================================================================
# ENUMS
# =============================================================================

class AgentState(str, Enum):
    INIT = "init"
    INGESTING = "ingesting"
    EXTRACTING = "extracting"
    REVIEWING = "reviewing"
    RENDERING = "rendering"
    COMPLETE = "complete"


class ReviewPriority(str, Enum):
    AUTO = "auto"           # High confidence, low stakes → just use it
    CONFIRM = "confirm"     # Medium confidence → show user, default accept
    DECIDE = "decide"       # Low confidence or conflict → user must choose
    MISSING = "missing"     # Not found → user must provide


class SecurityType(str, Enum):
    SERIES_SEED = "Series Seed Preferred Stock"
    SERIES_A = "Series A Preferred Stock"
    SERIES_B = "Series B Preferred Stock"
    SAFE = "SAFE"
    CONVERTIBLE_NOTE = "Convertible Note"


class ParticipationType(str, Enum):
    NON_PARTICIPATING = "non-participating"
    PARTICIPATING = "participating"
    CAPPED_PARTICIPATING = "capped participating"


class AntiDilutionType(str, Enum):
    BROAD_BASED = "broad-based weighted average"
    NARROW_BASED = "narrow-based weighted average"
    FULL_RATCHET = "full ratchet"
    NONE = "none"


class DividendType(str, Enum):
    NON_CUMULATIVE = "non-cumulative"
    CUMULATIVE = "cumulative"
    NONE = "none"


class VestingFrequency(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"


class AccelerationType(str, Enum):
    NONE = "none"
    SINGLE_TRIGGER = "single-trigger"
    DOUBLE_TRIGGER = "double-trigger"


class OptionPoolTiming(str, Enum):
    PRE_MONEY = "pre-money"
    POST_MONEY = "post-money"


# =============================================================================
# SOURCE & PROVENANCE
# =============================================================================

class SourceReference(BaseModel):
    """Where a value came from"""
    file: str                          # "deal_model.xlsx", "firm_policy.md", etc.
    location: str                      # "Sheet1!C5", "Section 2.4", "line 23"


class ConflictingValue(BaseModel):
    """When multiple sources disagree"""
    value: str
    source: SourceReference


class ExtractedField(BaseModel):
    """A single extracted field with provenance metadata"""
    value: Optional[str] = None
    source: Optional[SourceReference] = None
    confidence: float = Field(ge=0, le=1, default=0.0)
    conflicts: list[ConflictingValue] = Field(default_factory=list)
    found: bool = True
    derived_from_policy: bool = False
    user_edited: bool = False
    reasoning: Optional[str] = None

    def get_review_priority(self, is_high_stakes: bool = False) -> ReviewPriority:
        """Determine how this field should be handled in the UI
        
        With binary confidence (0.0 or 1.0):
        - confidence=1.0: AI is 100% certain, can auto-approve (unless high stakes)
        - confidence=0.0: AI is uncertain, human must review
        """
        if not self.found or self.value is None:
            return ReviewPriority.MISSING
        if self.conflicts:
            return ReviewPriority.DECIDE
        if self.confidence < 1.0:
            # Not 100% confident - human must review
            return ReviewPriority.DECIDE
        # confidence == 1.0
        if is_high_stakes:
            return ReviewPriority.CONFIRM
        return ReviewPriority.AUTO


# =============================================================================
# TERM SHEET SECTIONS
# =============================================================================

class PartiesSection(BaseModel):
    """Parties section of the term sheet"""
    company_name: ExtractedField = Field(default_factory=ExtractedField)
    company_jurisdiction: ExtractedField = Field(default_factory=ExtractedField)
    founders: ExtractedField = Field(default_factory=ExtractedField)
    lead_investor: ExtractedField = Field(default_factory=ExtractedField)


class DealEconomicsSection(BaseModel):
    """Deal economics section of the term sheet"""
    round_type: ExtractedField = Field(default_factory=ExtractedField)
    investment_amount: ExtractedField = Field(default_factory=ExtractedField)
    pre_money_valuation: ExtractedField = Field(default_factory=ExtractedField)
    security_type: ExtractedField = Field(default_factory=ExtractedField)
    price_per_share: ExtractedField = Field(default_factory=ExtractedField)
    target_ownership_pct: ExtractedField = Field(default_factory=ExtractedField)
    option_pool_pct: ExtractedField = Field(default_factory=ExtractedField)
    option_pool_timing: ExtractedField = Field(default_factory=ExtractedField)


class LiquidationTermsSection(BaseModel):
    """Liquidation and economic rights section"""
    liquidation_preference_multiple: ExtractedField = Field(default_factory=ExtractedField)
    participation_type: ExtractedField = Field(default_factory=ExtractedField)
    dividend_type: ExtractedField = Field(default_factory=ExtractedField)
    dividend_rate_pct: ExtractedField = Field(default_factory=ExtractedField)
    anti_dilution_type: ExtractedField = Field(default_factory=ExtractedField)


class GovernanceSection(BaseModel):
    """Control and governance section"""
    board_seats_total: ExtractedField = Field(default_factory=ExtractedField)
    board_seats_investor: ExtractedField = Field(default_factory=ExtractedField)
    board_seats_founder: ExtractedField = Field(default_factory=ExtractedField)
    board_seats_independent: ExtractedField = Field(default_factory=ExtractedField)
    board_observer_rights: ExtractedField = Field(default_factory=ExtractedField)
    investor_consent_for_quorum: ExtractedField = Field(default_factory=ExtractedField)
    drag_along_threshold_pct: ExtractedField = Field(default_factory=ExtractedField)
    pro_rata_rights: ExtractedField = Field(default_factory=ExtractedField)


class FounderTermsSection(BaseModel):
    """Founder terms section"""
    vesting_period_months: ExtractedField = Field(default_factory=ExtractedField)
    vesting_cliff_months: ExtractedField = Field(default_factory=ExtractedField)
    vesting_frequency: ExtractedField = Field(default_factory=ExtractedField)
    acceleration_type: ExtractedField = Field(default_factory=ExtractedField)
    non_compete_months: ExtractedField = Field(default_factory=ExtractedField)
    non_solicit_months: ExtractedField = Field(default_factory=ExtractedField)


class TransactionTermsSection(BaseModel):
    """Transaction terms section"""
    exclusivity_days: ExtractedField = Field(default_factory=ExtractedField)
    legal_fee_cap: ExtractedField = Field(default_factory=ExtractedField)
    expected_closing_days: ExtractedField = Field(default_factory=ExtractedField)
    governing_law: ExtractedField = Field(default_factory=ExtractedField)


class SignaturesSection(BaseModel):
    """Signatures and execution section"""
    effective_date: ExtractedField = Field(default_factory=ExtractedField)
    company_signatory_name: ExtractedField = Field(default_factory=ExtractedField)
    company_signatory_title: ExtractedField = Field(default_factory=ExtractedField)
    investor_signatory_name: ExtractedField = Field(default_factory=ExtractedField)
    investor_signatory_title: ExtractedField = Field(default_factory=ExtractedField)
    binding_status: ExtractedField = Field(default_factory=lambda: ExtractedField(
        value="non-binding",
        confidence=1.0,
        found=True,
        reasoning="Term sheets are typically non-binding except for exclusivity and confidentiality"
    ))


# =============================================================================
# COMPLETE TERM SHEET
# =============================================================================

class TermSheetData(BaseModel):
    """Complete extracted term sheet data"""
    document_type: Literal["term_sheet"] = "term_sheet"
    extracted_at: datetime = Field(default_factory=datetime.now)
    
    parties: PartiesSection = Field(default_factory=PartiesSection)
    deal_economics: DealEconomicsSection = Field(default_factory=DealEconomicsSection)
    liquidation_terms: LiquidationTermsSection = Field(default_factory=LiquidationTermsSection)
    governance: GovernanceSection = Field(default_factory=GovernanceSection)
    founder_terms: FounderTermsSection = Field(default_factory=FounderTermsSection)
    transaction_terms: TransactionTermsSection = Field(default_factory=TransactionTermsSection)
    signatures: SignaturesSection = Field(default_factory=SignaturesSection)

    def get_all_conflicts(self) -> list[dict]:
        """Get all fields with conflicts"""
        conflicts = []
        for section_name in ["parties", "deal_economics", "liquidation_terms", 
                            "governance", "founder_terms", "transaction_terms", "signatures"]:
            section = getattr(self, section_name)
            for field_name, field in section:
                if isinstance(field, ExtractedField) and field.conflicts:
                    conflicts.append({
                        "section": section_name,
                        "field": field_name,
                        "current_value": field.value,
                        "conflicts": [c.model_dump() for c in field.conflicts]
                    })
        return conflicts

    def get_missing_required_fields(self) -> list[dict]:
        """Get all required fields that are missing"""
        required_fields = [
            ("parties", "company_name"),
            ("deal_economics", "investment_amount"),
            ("deal_economics", "pre_money_valuation"),
            ("deal_economics", "security_type"),
            ("liquidation_terms", "liquidation_preference_multiple"),
        ]
        missing = []
        for section_name, field_name in required_fields:
            section = getattr(self, section_name)
            field = getattr(section, field_name)
            if not field.found or field.value is None:
                missing.append({"section": section_name, "field": field_name})
        return missing


# =============================================================================
# SESSION STATE
# =============================================================================

class UserDecision(BaseModel):
    """Log of a user decision"""
    timestamp: datetime = Field(default_factory=datetime.now)
    decision_type: str  # "conflict_resolution", "field_edit", "approval"
    section: str
    field: str
    old_value: Optional[str] = None
    new_value: str
    reason: Optional[str] = None


class SessionState(BaseModel):
    """Complete session state"""
    session_id: str
    agent_state: AgentState = AgentState.INIT
    document_type: str = "term_sheet"
    
    term_sheet: TermSheetData = Field(default_factory=TermSheetData)
    user_decisions: list[UserDecision] = Field(default_factory=list)
    chat_history: list[dict] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def add_chat_message(self, role: str, content: str):
        """Add a message to chat history"""
        self.chat_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now()

    def log_decision(self, decision: UserDecision):
        """Log a user decision"""
        self.user_decisions.append(decision)
        self.updated_at = datetime.now()

