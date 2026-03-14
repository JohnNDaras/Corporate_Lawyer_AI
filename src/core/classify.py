from __future__ import annotations
import json
from typing import Dict, Tuple
from pydantic import ValidationError

from .types import ClauseClassification, ClauseType
from ..llm.base import LLMClient


# Keyword taxonomy

KEYWORDS: Dict[ClauseType, Tuple[str, ...]] = {

    "Confidentiality": (
        "confidential",
        "non disclosure",
        "nondisclosure",
        "shall not disclose",
        "keep in confidence",
        "maintain confidentiality",
        "protect confidential",
    ),

    "Definition of Confidential Info": (
        "confidential information means",
        "confidential information shall mean",
        "\"confidential information\"",
        "defined as",
        "means any information",
    ),

    "Exceptions": (
        "does not include",
        "exceptions",
        "public domain",
        "already known",
        "independently developed",
        "rightfully received",
        "publicly available",
    ),

    "Term & Survival": (
        "term",
        "survive",
        "survival",
        "duration",
        "shall remain in effect",
        "years following termination",
    ),

    "Permitted Disclosures": (
        "permitted",
        "representatives",
        "need to know",
        "employees",
        "advisors",
        "professional advisors",
    ),

    "Return/Destruction": (
        "return",
        "destroy",
        "destruction",
        "upon request",
        "return or destroy",
        "certify destruction",
    ),

    "Remedies / Injunctive Relief": (
        "injunctive",
        "equitable relief",
        "irreparable harm",
        "injunction",
        "without posting bond",
        "no bond",
    ),

    "Governing Law": (
        "governing law",
        "laws of",
        "state of",
        "jurisdiction",
    ),

    "Dispute Resolution": (
        "arbitration",
        "venue",
        "court",
        "dispute",
        "binding arbitration",
        "exclusive jurisdiction",
    ),

    "Limitation of Liability": (
        "limitation of liability",
        "limit liability",
        "liability",
        "unlimited",
        "without limitation",
        "in no event",
        "consequential damages",
        "indirect damages",
        "cap on liability",
    ),

    "IP Ownership / Assignment": (
        "intellectual property",
        "assignment",
        "assigns",
        "ownership",
        "hereby assigns",
        "right title and interest",
    ),

    "Work Made for Hire": (
        "work made for hire",
        "work for hire",
        "copyright",
    ),

    "Termination": (
        "terminate",
        "termination",
        "upon notice",
        "may terminate",
        "for convenience",
        "for cause",
    ),

    "Miscellaneous": (
        "entire agreement",
        "severability",
        "counterparts",
        "amendment",
        "assignment",
        "notices",
        "waiver",
    ),
}


# Baseline classifier

def baseline_classify(clause_text: str) -> ClauseClassification:

    t = clause_text.lower()

    scores = {}

    for label, kws in KEYWORDS.items():

        # token-aware keyword matching
        scores[label] = sum(
            1 for kw in kws
            if all(token in t for token in kw.split())
        )

    best = max(scores, key=scores.get)
    raw = scores[best]

    confidence = min(0.95, 0.42 + 0.10 * raw)

    if raw == 0:
        best = "Miscellaneous"
        confidence = 0.35

    return ClauseClassification(
        label=best,
        confidence=confidence,
        rationale_short="keyword baseline"
    )


# LLM classifier

_LLM_SYSTEM = (
    "You classify contract clauses into a fixed taxonomy for contract review decision support. "
    "Return JSON only. Not legal advice."
)


def llm_classify(clause_text: str, llm: LLMClient) -> ClauseClassification:

    labels = list(KEYWORDS.keys())

    user = {
        "task": "Choose exactly one label from the taxonomy for the clause.",
        "taxonomy": labels,
        "clause_text": clause_text[:2500],
        "output_json_schema": {
            "label": "one taxonomy label",
            "confidence": "number 0..1",
            "rationale_short": "<= 20 words",
        },
        "rules": [
            "Return JSON only.",
            "No markdown.",
            "No extra keys.",
            "label must match taxonomy exactly.",
        ],
    }

    resp = llm.complete(
        system=_LLM_SYSTEM,
        user=json.dumps(user),
        temperature=0.1
    ).text

    try:

        data = json.loads(resp)

        out = ClauseClassification(**data)

        if out.label not in labels:
            return baseline_classify(clause_text)

        return out

    except (json.JSONDecodeError, ValidationError):

        return baseline_classify(clause_text)
