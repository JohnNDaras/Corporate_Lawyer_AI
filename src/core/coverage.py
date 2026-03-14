from typing import List

REQUIRED_CLAUSES = [
    "Confidentiality",
    "Definition of Confidential Info",
    "Exceptions",
    "Term & Survival",
    "Return/Destruction",
    "Remedies / Injunctive Relief",
]


def detect_missing_clauses(found_labels: List[str]) -> List[str]:

    missing = []

    for c in REQUIRED_CLAUSES:
        if c not in found_labels:
            missing.append(c)

    return missing