from __future__ import annotations
import re
from typing import List
from .types import Flag, ClauseType

def _snippet(text: str, m: re.Match, radius: int = 80) -> str:
    s, e = m.start(), m.end()
    return text[max(0, s - radius): min(len(text), e + radius)].strip()

# More robust patterns
UNLIMITED_LIABILITY_RE = re.compile(
    r"\bunlimited\b.*\bliabilit(y|ies)\b|\bliabilit(y|ies)\b.*\bunlimited\b|\bwithout limitation\b",
    re.IGNORECASE | re.DOTALL,
)

NO_BOND_RE = re.compile(r"\bno bond\b|\bwithout (posting )?bond\b", re.IGNORECASE)
NONCOMPETE_RE = re.compile(r"\bnon-?compete\b|\bnot compete\b", re.IGNORECASE)

def run_rules(clause_text: str, clause_label: ClauseType) -> List[Flag]:
    t = clause_text
    tl = clause_text.lower()
    flags: List[Flag] = []

    # Unlimited liability / no cap - now catches broader phrasing
    m = UNLIMITED_LIABILITY_RE.search(t)
    if m:
        flags.append(Flag(
            name="unlimited_liability_language",
            severity="High",
            evidence_snippet=_snippet(t, m),
            explanation="Language suggests liability may be uncapped or broadly expanded."
        ))

    # One-way confidentiality (still heuristic)
    if clause_label in ("Confidentiality", "Definition of Confidential Info"):
        if ("disclosing party" in tl and "receiving party" in tl) and ("each party" not in tl and "both parties" not in tl):
            flags.append(Flag(
                name="potential_one_way_confidentiality",
                severity="Med",
                evidence_snippet=t[:220],
                explanation="Clause may bind only one side; verify mutuality if intended."
            ))

    # Overbroad confidentiality definition
    if clause_label == "Definition of Confidential Info":
        m = re.search(r"\ball information\b.*\bwhether or not\b.*\bmarked\b", tl, re.DOTALL)
        if m:
            flags.append(Flag(
                name="overbroad_confidential_definition",
                severity="Med",
                evidence_snippet=_snippet(t, m),
                explanation="Definition appears very broad; may increase compliance burden and disputes."
            ))

    # Injunctive relief + no bond
    if clause_label == "Remedies / Injunctive Relief":
        m = NO_BOND_RE.search(t)
        if m:
            flags.append(Flag(
                name="injunction_no_bond",
                severity="Med",
                evidence_snippet=_snippet(t, m),
                explanation="Injunctive relief without bond can strengthen remedies against the recipient."
            ))

    # Non-compete (anywhere)
    m = NONCOMPETE_RE.search(t)
    if m:
        flags.append(Flag(
            name="non_compete",
            severity="High",
            evidence_snippet=_snippet(t, m),
            explanation="Non-compete restrictions can be high-risk and jurisdiction-dependent."
        ))

    # IP assignment without carve-outs (light heuristic)
    if clause_label == "IP Ownership / Assignment":
        if "hereby assigns" in tl and ("pre-existing" not in tl and "background" not in tl):
            flags.append(Flag(
                name="ip_assignment_missing_background_carveout",
                severity="Med",
                evidence_snippet=t[:260],
                explanation="IP assignment may be missing a carve-out for pre-existing/background IP."
            ))

    return flags

def run_document_rules(all_clauses_text: str) -> List[Flag]:
    tl = all_clauses_text.lower()
    flags: List[Flag] = []

    if "governing law" not in tl and "laws of" not in tl:
        flags.append(Flag(
            name="missing_governing_law",
            severity="Med",
            evidence_snippet="(document-level)",
            explanation="No governing law detected; may increase uncertainty and dispute costs."
        ))

    return flags

