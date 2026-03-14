# Utility Scripts

This directory contains **standalone utility scripts** used for preparing resources and evaluating components of the contract analysis system.

These scripts are **not required for running the main pipeline**, but they support important tasks such as:

- building the retrieval corpus index  
- evaluating classification performance  
- testing rule-based detection  
- running ablation studies  

These utilities were used during **system development and experimental evaluation**.

---

# Directory Structure

```
src/scripts/
│
├── __init__.py
├── build_corpus_index.py
└── evaluate.py
```

---

# Script Overview

## `build_corpus_index.py`

This script builds the **semantic retrieval index** used by the RAG component.

The index allows the system to retrieve **similar legal clauses** from a corpus when analyzing contracts.

---

## Workflow

```
Raw Clause Corpus
        │
        ▼
Normalize Text
        │
        ▼
SentenceTransformer Embeddings
        │
        ▼
FAISS Vector Index
        │
        ▼
Saved Retrieval Index
```

The resulting index is used by the system to provide **contextual grounding for clause analysis**.

---

# Corpus Format

The script expects clause examples in:

```
data/corpus_raw/
```

Each file should follow the naming format:

```
<clause_type>__<title>__<source_id>.txt
```

### Example

```
Confidentiality__Mutual_NDA__example001.txt
```

This structure encodes metadata used during retrieval.

| Field       | Description                     |
|------------|---------------------------------|
| clause_type | clause taxonomy category        |
| title       | descriptive title               |
| source_id   | unique identifier               |

---

# Passage Construction

Each file is converted into a **Passage object**:

```python
Passage(
    source_id="example001",
    title="Mutual_NDA",
    clause_type="Confidentiality",
    text="Clause text..."
)
```

These passages form the **retrieval corpus**.

---

# Building the Index

To generate the FAISS index:

```bash
python src/scripts/build_corpus_index.py
```

The script performs:

1. Load clause examples  
2. Normalize text  
3. Generate embeddings  
4. Build FAISS index  
5. Save metadata  

### Output Files

```
indices/faiss.index
indices/faiss_meta.pkl
```

These files are required for **retrieval-augmented generation (RAG)**.

---

# `evaluate.py`

This script evaluates **individual components of the contract analysis system**.

It supports three evaluation tasks:

1. Clause classification  
2. Rule-based detection  
3. System ablation experiments  

The evaluation uses a labeled dataset stored in:

```
data/eval/eval_set.jsonl
```

---

# Evaluation Dataset Format

Each entry in the dataset should follow this structure:

```json
{
  "clause_text": "...",
  "true_label": "Confidentiality",
  "expected_flags": ["non_compete"]
}
```

### Fields

| Field         | Description                          |
|--------------|--------------------------------------|
| clause_text   | clause content                       |
| true_label    | ground truth classification          |
| expected_flags| expected rule triggers               |

---

# Classification Evaluation

The script measures classification performance using:

- **Accuracy**  
- **Macro F1 score**  

Evaluation compares predicted labels against the ground truth.

### Example Output

```
== Classification ==
{'accuracy': 0.84, 'macro_f1': 0.81}
```

---

# Rule Evaluation

Rule-based detection is evaluated using:

- Precision  
- Recall  
- F1-score  

The script computes both:

- **per-rule metrics**  
- **micro-averaged metrics**  

### Example Output

```
== Rules ==
{
  "per_rule": {
    "non_compete": {"precision": 0.90, "recall": 0.75, "f1": 0.82}
  },
  "micro": {"precision": 0.88, "recall": 0.80, "f1": 0.84}
}
```

---

# Ablation Experiments

The evaluation script also supports **system ablation analysis**.

Ablation studies measure how different system components affect performance.

The following configurations are compared:

| Mode       | Description                              |
|------------|------------------------------------------|
| LLM Only   | LLM reasoning without retrieval          |
| RAG Only   | Retrieval grounding without LLM analysis |
| Hybrid     | Full hybrid architecture                 |

These experiments provide insight into the **contribution of each component**.

### Example Output

```
== Ablation ==
{
  "llm_only": 0.78,
  "rag_only": 0.65,
  "hybrid": 0.91
}
```

---

# Running the Evaluation

To run the evaluation script:

```bash
python src/scripts/evaluate.py
```

The script prints evaluation metrics directly to the console.

---

# Role in the Research Project

The scripts in this directory were used during the development and validation of the hybrid contract analysis system.

Specifically they supported:

- building the retrieval corpus  
- validating classification performance  
- testing rule detection  
- performing experimental ablation analysis  

These experiments informed the design choices presented in the **research paper**.

---

# Notes

These scripts are designed for **research and experimentation**, not production deployment.

For real-time contract analysis, the system uses the **pipeline module in `src/core`**.
