from __future__ import annotations
import os
import json
import csv
import time
from pathlib import Path

from tqdm import tqdm
import pdfminer.high_level
from bs4 import BeautifulSoup

from src.core.pipeline import analyze_contract
from src.core.rag import RAGConfig
from src.llm.openrouter_client import OpenRouterClient


# Contract loader (PDF / HTML / TXT)

def load_contract(file_path: Path) -> str:

    suffix = file_path.suffix.lower()

    try:

        # TXT
        if suffix == ".txt":
            return file_path.read_text(errors="ignore")

        # PDF
        if suffix == ".pdf":
            return pdfminer.high_level.extract_text(file_path)

        # HTML / HTM
        if suffix in [".html", ".htm"]:

            html = file_path.read_text(errors="ignore")

            soup = BeautifulSoup(html, "lxml")

            # remove scripts/styles
            for tag in soup(["script", "style"]):
                tag.extract()

            text = soup.get_text(separator="\n")

            # remove SEC snapshot header
            if "Snapshot-Content-Location" in text:
                parts = text.split("\n\n", 1)
                if len(parts) > 1:
                    text = parts[1]

            return text

    except Exception as e:
        print(f"Error reading {file_path.name}: {e}")

    return ""


# Paths

CONTRACT_DIR = "data/contracts"
OUTPUT_DIR = "results"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# RAG configuration

rag_cfg = RAGConfig(
    index_path="indices/faiss.index",
    metadata_path="indices/faiss_meta.pkl",
)


# LLM

print("Initializing OpenRouter LLM...")
llm = OpenRouterClient()


# Experiment configurations

experiments = {

    "baseline": dict(
        use_llm_classification=False,
        use_rag=False,
        use_rules=False,
        use_llm_analysis=False
    ),

    "rules_only": dict(
        use_llm_classification=False,
        use_rag=False,
        use_rules=True,
        use_llm_analysis=False
    ),

    "rag_rules": dict(
        use_llm_classification=False,
        use_rag=True,
        use_rules=True,
        use_llm_analysis=False
    ),

    "full_system": dict(
        use_llm_classification=True,
        use_rag=True,
        use_rules=True,
        use_llm_analysis=True
    ),
}


# Prepare contract list (filter invalid ones)

contract_files = []

print("\nScanning contracts...\n")

for f in Path(CONTRACT_DIR).iterdir():

    text = load_contract(f)

    if len(text.strip()) > 500:
        contract_files.append(f)
        print(f"✓ Valid contract: {f.name}")
    else:
        print(f"⚠ Skipping invalid contract: {f.name}")

print()

total_jobs = len(contract_files) * len(experiments)

print(f"Valid contracts: {len(contract_files)}")
print(f"Experiments per contract: {len(experiments)}")
print(f"Total experiment runs: {total_jobs}\n")


summary_rows = []

global_progress = tqdm(total=total_jobs, desc="Total progress")

start_time = time.time()


# Run experiments

for contract_file in contract_files:

    contract_text = load_contract(contract_file)

    for exp_name, settings in experiments.items():

        job_start = time.time()

        print(f"\nRunning {exp_name} on {contract_file.name}")

        try:

            result = analyze_contract(
                raw_text=contract_text,
                llm=llm,
                rag_cfg=rag_cfg,
                **settings
            )

        except Exception as e:
            print(f"Experiment failed for {contract_file.name}: {e}")
            global_progress.update(1)
            continue


        output_path = os.path.join(
            OUTPUT_DIR,
            f"{contract_file.stem}_{exp_name}.json"
        )

        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)


        for clause in result["clauses"]:

            analysis = clause["analysis"]

            summary_rows.append({

                "contract": contract_file.name,
                "experiment": exp_name,
                "clause_id": clause["clause"]["id"],
                "clause_type": analysis.get("clause_type"),
                "risk_score": analysis.get("risk_score"),
                "severity": analysis.get("business_risk", {}).get("severity"),
                "deviation": analysis.get("norm_deviation", {}).get("deviates"),
                "confidence": analysis.get("uncertainty", {}).get("confidence"),

            })


        job_time = time.time() - job_start

        print(f"Finished in {job_time:.2f} seconds")

        global_progress.update(1)


global_progress.close()


# Save CSV summary

csv_path = os.path.join(OUTPUT_DIR, "experiment_summary.csv")

if summary_rows:

    with open(csv_path, "w", newline="") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=summary_rows[0].keys()
        )

        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"\nCSV summary saved to: {csv_path}")

else:
    print("\nNo results generated.")


# Final runtime report

total_time = time.time() - start_time

print("\nExperiments finished")
print(f"Total runtime: {total_time/60:.2f} minutes")
print(f"Results saved to: {OUTPUT_DIR}")
