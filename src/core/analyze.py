from __future__ import annotations
import json
import re
from typing import List, Optional
from pydantic import ValidationError
from .types import AnalysisJSON, Clause, Passage, Flag, ClauseType
from ..llm.base import LLMClient
from .disclaimers import DISCLAIMER_BANNER


_ANALYZE_SYSTEM = (
    "You are an AI assistant for contract review decision support. "
    "Not legal advice. Provide grounded clause-level analysis with uncertainty. "
    "Return JSON only. Do not wrap in markdown."
)

# JSON extraction helpers

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)

def _extract_json_object(text: str) -> Optional[str]:
    """
    Try to extract the first JSON object from a messy LLM response.
    Handles extra text before/after JSON and code fences.
    """
    if not text:
        return None

    t = text.strip()

    # Strip common markdown fences
    if "```" in t:
        t = t.replace("```json", "").replace("```JSON", "").replace("```", "").strip()

    # Fast path: already valid JSON
    if t.startswith("{") and t.endswith("}"):
        return t

    # Try to find a JSON-looking block
    m = _JSON_BLOCK_RE.search(t)
    if not m:
        return None

    candidate = m.group(0).strip()

    # Sometimes models output multiple JSON objects; take the first balanced one
    # We'll do a lightweight brace-balance scan from first '{'
    start = t.find("{")
    if start == -1:
        return candidate

    depth = 0
    for i in range(start, len(t)):
        if t[i] == "{":
            depth += 1
        elif t[i] == "}":
            depth -= 1
            if depth == 0:
                return t[start:i+1].strip()

    return candidate


def _format_context(passages: List[Passage]) -> List[dict]:
    return [
        {
            "source_id": p.source_id,
            "title": p.title,
            "clause_type": p.clause_type,
            "text": p.text[:700],  # keep small
        }
        for p in passages
    ]


def _max_flag_severity(flags: List[Flag]) -> str:
    if not flags:
        return "Low"
    order = {"Low": 1, "Med": 2, "High": 3}
    return max(flags, key=lambda f: order.get(f.severity, 1)).severity


def _upgrade_severity(llm_sev: str, flags: List[Flag]) -> str:
    """
    Ensure business_risk severity reflects deterministic rule severity.
    """
    llm_rank = {"Low": 1, "Medium": 2, "High": 3}.get(llm_sev, 2)
    flag = _max_flag_severity(flags)
    if flag == "High":
        return "High"
    if flag == "Med" and llm_rank < 2:
        return "Medium"
    return llm_sev


def analyze_clause(
    clause: Clause,
    label: ClauseType,
    retrieved_passages: List[Passage],
    flags: List[Flag],
    llm: LLMClient,
    max_retries: int = 3,
) -> AnalysisJSON:

    payload = {
        "disclaimer": DISCLAIMER_BANNER,
        "clause_id": clause.id,
        "clause_type": label,
        "clause_text": clause.raw_text[:3500],
        "retrieved_context": _format_context(retrieved_passages),
        "rule_flags": [f.__dict__ for f in flags],
        "required_json_schema": {
            "clause_id": "string",
            "clause_type": "one taxonomy label",
            "plain_english_summary": "string",
            "business_risk": {"severity": "Low|Medium|High", "why": ["..."]},
            "norm_deviation": {
                "deviates": "boolean",
                "comparison": ["..."],
                "suggested_revision": "string",
            },
            "uncertainty": {"confidence": "number 0..1", "reasons": ["..."]},
            "citations": [{"source_id": "...", "quote": "..."}],
        },
        "rules": [
            "Return JSON only.",
            "No markdown, no commentary, no preface.",
            "No extra keys beyond required_json_schema.",
            "uncertainty.confidence must be a NUMBER from 0.0 to 1.0.",
            "If retrieved_context is empty, citations must be [].",
            "Citations quotes must be short and copied from retrieved_context only.",
            "Do not provide legal advice.",
        ],
    }

    last_err = None

    for attempt in range(max_retries):
        resp_text = llm.complete(
            system=_ANALYZE_SYSTEM,
            user=json.dumps(payload),
            temperature=0.2,
        ).text

        candidate = _extract_json_object(resp_text)

        if not candidate:
            last_err = "Could not find JSON object in model output."
        else:
            try:
                data = json.loads(candidate)

                # If no RAG context, enforce empty citations (avoid hallucinated cites)
                if not retrieved_passages:
                    data["citations"] = []

                out = AnalysisJSON(**data)

                # Upgrade severity based on flags
                sev = out.business_risk.get("severity", "Medium")
                out.business_risk["severity"] = _upgrade_severity(sev, flags)

                # If model gives ultra-low confidence, require reasons; otherwise lift slightly
                conf = float(out.uncertainty.get("confidence", 0.5))
                reasons = out.uncertainty.get("reasons", [])
                if conf <= 0.15 and (not reasons or len(reasons) == 0):
                    out.uncertainty["confidence"] = 0.35
                    out.uncertainty["reasons"] = ["Confidence adjusted: model gave very low confidence without reasons."]

                return out

            except (json.JSONDecodeError, ValidationError) as e:
                last_err = str(e)

        # Repair prompt for next attempt: show model a JSON skeleton
        payload["rules"].append(
            f"Previous output was invalid. Fix it. Error: {str(last_err)[:200]}"
        )
        payload["example_valid_output"] = {
            "clause_id": clause.id,
            "clause_type": label,
            "plain_english_summary": "Example: This clause requires X and prohibits Y.",
            "business_risk": {"severity": "Medium", "why": ["Example reason 1", "Example reason 2"]},
            "norm_deviation": {"deviates": False, "comparison": [], "suggested_revision": ""},
            "uncertainty": {"confidence": 0.6, "reasons": ["Example: missing definitions / context."]},
            "citations": [],
        }

    # Final fallback
    return AnalysisJSON(
        clause_id=clause.id,
        clause_type=label,
        plain_english_summary="Parsing failed.",
        business_risk={"severity": "Medium", "why": ["LLM JSON parsing failure."]},
        norm_deviation={"deviates": False, "comparison": [], "suggested_revision": ""},
        uncertainty={"confidence": 0.1, "reasons": [f"Repeated JSON failures. Last error: {str(last_err)[:120]}"]},
        citations=[],
    )
