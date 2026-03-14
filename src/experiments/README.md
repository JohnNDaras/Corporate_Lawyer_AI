# Experimental Evaluation Framework

This directory contains the **experimental evaluation scripts** used to benchmark the hybrid contract analysis system.

The experiments evaluate how different architectural components contribute to contract analysis performance.

The goal is to measure the impact of:

- deterministic rule-based analysis  
- retrieval-augmented generation (RAG)  
- large language model reasoning  

The results produced by these experiments were used in the **research paper evaluation section**.

---

# Experiment Pipeline

The experiment workflow follows the pipeline below:

```
Contracts Dataset
        │
        ▼
Contract Loader (PDF / HTML / TXT)
        │
        ▼
Contract Analysis Pipeline
        │
        ├── Clause Segmentation
        ├── Clause Classification
        ├── Rule-Based Risk Detection
        ├── Retrieval-Augmented Generation
        └── LLM Clause Analysis
        ▼
Clause-Level Results
        │
        ▼
Metric Aggregation
        │
        ▼
Experiment Outputs (JSON + CSV)
```

Each contract is processed multiple times using different **system configurations**.

---

# Experiment Script

The experiments are executed using:

```
run_experiments.py
```

This script performs the following steps:

1. Loads contracts from the dataset directory  
2. Converts PDF and HTML files into plain text  
3. Runs multiple system configurations  
4. Saves clause-level results  
5. Aggregates experiment metrics  
6. Exports a summary CSV file  

---

# Dataset Loading

Contracts are loaded from:

```
data/contracts/
```

The loader supports multiple formats:

| Format | Description |
|--------|-------------|
| `.txt` | Plain text contracts |
| `.pdf` | Extracted using pdfminer |
| `.html` / `.htm` | Parsed using BeautifulSoup |

SEC filing HTML documents often contain metadata headers.  
The loader automatically removes these headers to avoid polluting the contract text.

Example cleaning step:

```
Snapshot-Content-Location
MIME-Version
Content-Type
```

These artifacts are removed before analysis.

---

# Contract Validation

Before running experiments, each contract is validated.

A contract is considered valid if:

```
length(text) > 500 characters
```

Short or malformed files are automatically skipped.

Example output:

```
✓ Valid contract: nda_contract_01.pdf
⚠ Skipping invalid contract: corrupted_file.htm
```

---

# Experiment Configurations

The experiments compare four system configurations.

---

## 1. Baseline

```
use_llm_classification = False
use_rag = False
use_rules = False
use_llm_analysis = False
```

### Features:

- clause segmentation  
- keyword-based clause classification  

This configuration represents the **minimal system**.

---

## 2. Rules Only

```
use_llm_classification = False
use_rag = False
use_rules = True
use_llm_analysis = False
```

### Features:

- deterministic rule-based risk detection  
- keyword classification  

This configuration evaluates **traditional rule-based contract analysis**.

---

## 3. RAG + Rules

```
use_llm_classification = False
use_rag = True
use_rules = True
use_llm_analysis = False
```

### Features:

- semantic retrieval using FAISS  
- rule-based detection  

This configuration tests **retrieval grounding without LLM reasoning**.

---

## 4. Full Hybrid System

```
use_llm_classification = True
use_rag = True
use_rules = True
use_llm_analysis = True
```

### Features:

- LLM classification  
- retrieval augmented generation  
- rule-based checks  
- LLM clause reasoning  

This represents the **complete system architecture** proposed in the paper.

---

# Metrics Collected

The experiments collect clause-level metrics for each configuration.

The following fields are recorded:

| Metric | Description |
|--------|-------------|
| contract | contract filename |
| experiment | configuration name |
| clause_id | clause identifier |
| clause_type | classified clause category |
| risk_score | numeric risk score |
| severity | risk severity level |
| deviation | deviation from normative clause patterns |
| confidence | LLM uncertainty estimate |

---

# Output Files

Each experiment run produces two types of outputs.

---

## Clause-Level JSON

Example:

```
results/nda_contract_01_full_system.json
```

This file contains the complete analysis output for the contract.

Structure:

```json
{
  "clauses": [...],
  "contract_risk": {...},
  "missing_clauses": [...]
}
```

---

## Experiment Summary CSV

Example:

```
results/experiment_summary.csv
```

This file aggregates clause-level metrics across all experiments.

Example row:

```
contract,experiment,clause_id,clause_type,risk_score,severity,deviation,confidence
nda_01.pdf,full_system,c003,Confidentiality,85,High,True,0.81
```

This file is used to generate the **plots and tables reported in the paper**.

---

# Progress Tracking

Experiments can take several minutes because LLM analysis is performed for each clause.

The script uses `tqdm` to show progress:

```
Total progress:  25%|██████
```

For each experiment run the script prints:

```
Running full_system on contract_01.pdf
Finished in 9.45 seconds
```

---

# Runtime Statistics

At the end of execution the script prints:

```
Experiments finished
Total runtime: 3.4 minutes
Results saved to: results/
```

This allows tracking experiment cost and performance.

---

# Reproducing the Experiments

To reproduce the experimental evaluation:

```
python src/experiments/run_experiments.py
```

Required directories:

```
data/contracts/
indices/
```

Output will automatically be written to:

```
results/
```

---

# Research Relevance

These experiments were designed to evaluate the **effectiveness of hybrid AI architectures for contract analysis**.

Specifically, they measure the impact of combining:

- deterministic legal rules  
- semantic retrieval from clause corpora  
- large language model reasoning  

The results demonstrate that the **hybrid architecture significantly improves risk detection and clause analysis confidence compared to rule-based systems alone**.
