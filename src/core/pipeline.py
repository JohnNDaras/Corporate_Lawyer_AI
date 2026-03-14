from __future__ import annotations
from typing import Any, Dict, Optional

from .text import normalize_text
from .segment import segment_clauses
from .classify import baseline_classify, llm_classify
from .rules import run_rules, run_document_rules
from .rag import RAGConfig, FAISSRetriever
from .analyze import analyze_clause
from .coverage import detect_missing_clauses
from ..llm.base import LLMClient
from .disclaimers import DISCLAIMER_BANNER


# Helper: severity -> numeric risk score

def severity_to_score(severity: str) -> int:
    mapping = {
        "Low": 30,
        "Med": 60,
        "Medium": 60,
        "High": 85,
        "Critical": 95,
    }
    return mapping.get(severity, 50)


# Helper: normalize boolean outputs

def normalize_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return False


def analyze_contract(
    raw_text: str,
    llm: Optional[LLMClient],
    rag_cfg: RAGConfig,
    use_llm_classification: bool = True,
    use_rag: bool = True,
    use_rules: bool = True,
    use_llm_analysis: bool = True,
) -> Dict[str, Any]:

    text = normalize_text(raw_text)

    clauses = segment_clauses(text)

    doc_flags = run_document_rules(text) if use_rules else []

    retriever = FAISSRetriever(rag_cfg) if use_rag else None

    results = []

    # Risk aggregation
    severity_values = []

    for c in clauses:

        # Classification
        if llm and use_llm_classification:
            cls = llm_classify(c.raw_text, llm)
        else:
            cls = baseline_classify(c.raw_text)

        # Retrieval
        if retriever:
            try:
                passages = retriever.retrieve(
                    query=c.raw_text,
                    clause_label=cls.label,
                    k=3,
                )
            except Exception:
                passages = []
        else:
            passages = []

        # Rules
        flags = run_rules(c.raw_text, cls.label) if use_rules else []

        # LLM Analysis
        if llm and use_llm_analysis:

            analysis = analyze_clause(
                clause=c,
                label=cls.label,
                retrieved_passages=passages,
                flags=flags,
                llm=llm,
            )

            analysis_dict = analysis.model_dump()

        else:

            analysis_dict = {
                "clause_id": c.id,
                "clause_type": cls.label,
                "plain_english_summary": "(LLM analysis disabled)",
                "business_risk": {"severity": "Low", "why": []},
                "norm_deviation": {
                    "deviates": False,
                    "comparison": [],
                    "suggested_revision": "",
                },
                "uncertainty": {
                    "confidence": cls.confidence,
                    "reasons": ["LLM analysis disabled"],
                },
                "citations": [],
            }

        # Fix boolean outputs
        if "norm_deviation" in analysis_dict:
            analysis_dict["norm_deviation"]["deviates"] = normalize_bool(
                analysis_dict["norm_deviation"].get("deviates", False)
            )

        # Risk score
        severity = analysis_dict["business_risk"]["severity"]
        analysis_dict["risk_score"] = severity_to_score(severity)

        severity_values.append(severity)

        # Hybrid confidence adjustment
        if flags and severity == "Low":
            analysis_dict["uncertainty"]["confidence"] = max(
                0.0, analysis_dict["uncertainty"]["confidence"] * 0.8
            )

        # Attach rule evidence
        if flags:

            analysis_dict.setdefault("citations", [])

            for f in flags:
                analysis_dict["citations"].append(
                    {"rule": f.name, "evidence": f.evidence_snippet}
                )

        results.append(
            {
                "clause": {
                    "id": c.id,
                    "text": c.raw_text,
                    "start_char": c.start_char,
                    "end_char": c.end_char,
                },
                "classification": cls.model_dump(),
                "flags": [f.__dict__ for f in flags],
                "analysis": analysis_dict,
            }
        )

    # Global Contract Risk Score

    weights = {"Low": 1, "Med": 2, "Medium": 2, "High": 3}

    risk_sum = sum(weights.get(s, 1) for s in severity_values)

    if severity_values:
        contract_score = round((risk_sum / len(severity_values)) * 33)
    else:
        contract_score = 0

    contract_risk = {
        "score": min(100, contract_score),
        "level": "High" if contract_score > 70 else "Medium" if contract_score > 40 else "Low",
    }

    # Missing clause detection

    labels = [r["classification"]["label"] for r in results]

    missing_clauses = detect_missing_clauses(labels)

    return {
        "disclaimer": DISCLAIMER_BANNER,
        "doc_flags": [f.__dict__ for f in doc_flags],
        "clauses": results,
        "contract_risk": contract_risk,
        "missing_clauses": missing_clauses,
        "settings": {
            "use_llm_classification": use_llm_classification,
            "use_rag": use_rag,
            "use_rules": use_rules,
            "use_llm_analysis": use_llm_analysis,
        },
    }
