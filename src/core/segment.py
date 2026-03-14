from __future__ import annotations
import re
from typing import List
from .types import Clause

_NUM_HEADING = re.compile(r"(?m)^(?P<num>\d+(\.\d+){0,3})[)\.]?\s+")
_ALLCAPS_HEADING = re.compile(r"(?m)^[A-Z][A-Z0-9 \-_/]{5,}$")

def _split_positions(text: str) -> List[int]:
    positions = {0}
    for m in _NUM_HEADING.finditer(text):
        positions.add(m.start())
    for m in _ALLCAPS_HEADING.finditer(text):
        positions.add(m.start())
    # fallback split on blank lines if no headings found
    if len(positions) == 1:
        for m in re.finditer(r"\n\s*\n", text):
            positions.add(m.end())
    return sorted(p for p in positions if 0 <= p < len(text))

def segment_clauses(text: str) -> List[Clause]:
    splits = _split_positions(text)
    clauses: List[Clause] = []
    for i, start in enumerate(splits):
        end = splits[i + 1] if i + 1 < len(splits) else len(text)
        chunk = text[start:end].strip()
        if len(chunk) < 25:
            continue
        clause_id = f"c{i+1:03d}"
        clauses.append(Clause(id=clause_id, raw_text=chunk, start_char=start, end_char=end))
    return clauses
