from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, conlist, confloat

ClauseType = Literal[
    "Confidentiality",
    "Definition of Confidential Info",
    "Exceptions",
    "Term & Survival",
    "Permitted Disclosures",
    "Return/Destruction",
    "Remedies / Injunctive Relief",
    "Governing Law",
    "Dispute Resolution",
    "Limitation of Liability",
    "IP Ownership / Assignment",
    "Work Made for Hire",
    "Termination",
    "Miscellaneous",
]

Severity = Literal["Low", "Medium", "High"]

@dataclass
class Clause:
    id: str
    raw_text: str
    start_char: int
    end_char: int

@dataclass
class Passage:
    source_id: str
    title: str
    clause_type: str
    text: str

@dataclass
class Flag:
    name: str
    severity: Literal["Low", "Med", "High"]
    evidence_snippet: str
    explanation: str

class ClauseClassification(BaseModel):
    label: ClauseType
    confidence: confloat(ge=0.0, le=1.0)
    rationale_short: str = Field(..., max_length=240)

class AnalysisJSON(BaseModel):
    clause_id: str
    clause_type: ClauseType
    plain_english_summary: str

    business_risk: Dict[str, Any]  # {"severity": "Low|Medium|High", "why": [...]}

    norm_deviation: Dict[str, Any]  # {"deviates": bool, "comparison": [...], "suggested_revision": str}

    uncertainty: Dict[str, Any]     # {"confidence": 0..1, "reasons": [...]}

    citations: List[Dict[str, str]] # [{"source_id": "...", "quote": "..."}]
