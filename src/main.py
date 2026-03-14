import argparse, json
from src.core.pipeline import analyze_contract
from src.core.rag import RAGConfig

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to contract text file")
    ap.add_argument("--out", required=True, help="Output JSON path")
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    llm = None  # plug in your LLM client
    rag_cfg = RAGConfig(persist_dir="indices/chroma")

    result = analyze_contract(text, llm=llm, rag_cfg=rag_cfg)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    # minimal terminal table
    print("Clause\tType\tSeverity\tDeviation\tConfidence")
    for item in result["clauses"]:
        a = item["analysis"]
        print(
            f"{item['clause']['id']}\t{a.get('clause_type')}\t"
            f"{a.get('business_risk',{}).get('severity')}\t"
            f"{a.get('norm_deviation',{}).get('deviates')}\t"
            f"{a.get('uncertainty',{}).get('confidence')}"
        )

if __name__ == "__main__":
    main()
