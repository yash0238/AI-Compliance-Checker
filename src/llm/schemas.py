# src/llm/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

# =====================================================
# CLAUSE EXTRACTION SCHEMAS
# =====================================================

class Clause(BaseModel):
    clause_id: str = Field(description="Unique identifier for the clause")
    clause_heading: Optional[str] = Field(description="The heading or title of the clause, if present")
    clause_text: str = Field(description="The full text content of the clause")
    clause_type: str = Field(description="Categorize into: Confidentiality, Termination, Indemnity, Liability, Payment, Data Protection, IP, SLA, Assignment, Governing Law, Dispute Resolution, Other")
    rationale: str = Field(description="1 sentence why this classification is correct")

class ClauseExtractionBox(BaseModel):
    """Schema to contain heavily extracted data securely."""
    data: List[Clause] = Field(description="A list of the extracted clauses.")


# =====================================================
# RISK ASSESSMENT SCHEMAS
# =====================================================

class RiskAssessment(BaseModel):
    risk_level: str = Field(description="'low', 'medium', or 'high'")
    risk_score: int = Field(description="numeric score 0-100")
    risk_factors: List[str] = Field(description="List of key risk concerns. MUST be a JSON array. Return [] if none.")
    missing_controls: List[str] = Field(description="List of missing legal protections. MUST be a JSON array. Return [] if none.")
    regulation_violations: List[str] = Field(description="List of violated or implicated Indian regulations. MUST be a JSON array. Return [] if none.")
    explanation: str = Field(description="short summary citing specific articles/sections if available")

