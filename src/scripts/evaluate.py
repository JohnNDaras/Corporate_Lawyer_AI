from __future__ import annotations
import json
from typing import Dict, List, Any, Tuple
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support

from src.core.classify import baseline_classify, llm_classify
from src.core.rules import run_rules
from src.core.rag import RAGConfig, retrieve_context
from src.core.analyze import analyze_clause
from src.core.types import Clause
from src.llm.base import LLMClient

def load_jsonl(path: str) -> List[dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def eval_classification(rows: List[dict], llm: LLMClient | None) -> Dict[str, Any]:
    y_true, y_pred = [], []
    for r in rows:
        text = r["clause_text"]
        true = r["true_label"]
        if llm:
            pred = llm_classify(text, llm).label
        else:
            pred = baseline_classify(text).label
        y_true.append(true)
        y_pred.append(pred)
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
    }

def eval_rules(rows: List[dict]) -> Dict[str, Any]:
    # expected_flags: list[str]
    all_rules = set()
    for r in rows:
        for name in r.get("expected_flags", []):
            all_rules.add(name)
    all_rules = sorted(all_rules)

    y_true_by_rule = {rn: [] for rn in all_rules}
    y_pred_by_rule = {rn: [] for rn in all_rules}

    for r in rows:
        text = r["clause_text"]
        label = r["true_label"]
        expected = set(r.get("expected_flags", []))
        found = set(f.name for f in run_rules(text, label))

        for rn in all_rules:
            y_true_by_rule[rn].append(1 if rn in expected else 0)
            y_pred_by_rule[rn].append(1 if rn in found else 0)

    per_rule = {}
    for rn in all_rules:
        p, rc, f1, _ = precision_recall_fscore_support(
            y_true_by_rule[rn], y_pred_by_rule[rn], average="binary", zero_division=0
        )
        per_rule[rn] = {"precision": float(p), "recall": float(rc), "f1": float(f1)}

    # micro (flatten)
    y_true_flat = [x for rn in all_rules for x in y_true_by_rule[rn]]
    y_pred_flat = [x for rn in all_rules for x in y_pred_by_rule[rn]]
    p, rc, f1, _ = precision_recall_fscore_support(y_true_flat, y_pred_flat, average="binary", zero_division=0)

    return {"per_rule": per_rule, "micro": {"precision": float(p), "recall": float(rc), "f1": float(f1)}}

def run_ablation(rows: List[dict], llm: LLMClient | None, rag_cfg: RAGConfig) -> Dict[str, Any]:
    # For ablation: we focus on downstream severity stability or output completeness.
    # Minimal proxy: "did the analyzer produce valid JSON with severity field"
    def run_mode(mode: str):
        ok = 0
        for i, r in enumerate(rows):
            clause = Clause(id=f"e{i:03d}", raw_text=r["clause_text"], start_char=0, end_char=len(r["clause_text"]))
            label = r["true_label"]

            passages = retrieve_context(clause.raw_text, label, rag_cfg, k=4) if ("rag" in mode) else []
            flags = run_rules(clause.raw_text, label) if ("rules" in mode) else []

            if llm and ("llm" in mode):
                analysis = analyze_clause(clause, label, passages, flags, llm)
                if analysis.business_risk.get("severity") in ("Low", "Medium", "High"):
                    ok += 1
            else:
                # no-llm mode
                ok += 1
        return ok / max(1, len(rows))

    return {
        "llm_only": run_mode("llm"),
        "rag_only": run_mode("rag"),     # proxy only (no analyzer)
        "hybrid": run_mode("llm+rag+rules"),
    }

def main():
    rows = load_jsonl("data/eval/eval_set.jsonl")
    rag_cfg = RAGConfig(persist_dir="indices/chroma")

    llm = None  # plug in our client

    print("== Classification ==")
    print(eval_classification(rows, llm))

    print("\n== Rules ==")
    print(eval_rules(rows))

    print("\n== Ablation (proxy completeness) ==")
    print(run_ablation(rows[:20], llm, rag_cfg))

if __name__ == "__main__":
    main()
