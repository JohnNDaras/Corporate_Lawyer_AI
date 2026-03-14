# Core Contract Analysis Engine

This directory contains the **core analytical components** of the contract analysis system.

It implements the full pipeline responsible for transforming raw contract text into structured clause-level risk analysis.

The modules in this folder perform the following main tasks:

1. **Text normalization**
2. **Clause segmentation**
3. **Clause classification**
4. **Rule-based risk detection**
5. **Retrieval-Augmented Generation (RAG)**
6. **LLM-based clause analysis**
7. **Document-level coverage checks**
8. **Risk scoring and aggregation**

These components together form the **hybrid contract analysis architecture** used in the research project.

---

# Architecture Overview

The processing pipeline implemented in this module follows the workflow below:

```
Raw Contract Text
        │
        ▼
Text Normalization
        │
        ▼
Clause Segmentation
        │
        ▼
Clause Classification
        │
        ├── Rule-Based Risk Detection
        ├── Retrieval of Similar Clauses (RAG)
        ▼
LLM Clause Analysis
        │
        ▼
Risk Scoring + Aggregation
        │
        ▼
Final Structured Contract Report
```

Each stage is implemented as a dedicated module in this directory.

---

# File Structure

```
src/core/
│
├── analyze.py
├── classify.py
├── coverage.py
├── disclaimers.py
├── pipeline.py
├── rag.py
├── rules.py
├── segment.py
├── text.py
└── types.py
```

Each module is explained below.

---

# `pipeline.py`

**Central orchestration module of the entire system.**

This file implements the `analyze_contract()` function which coordinates all analysis steps.

### Main responsibilities:

- normalize raw contract text
- segment the document into clauses
- classify clauses
- apply rule-based checks
- retrieve similar clauses using FAISS
- generate LLM-based clause analysis
- compute clause-level risk scores
- compute overall contract risk
- detect missing critical clauses

The pipeline produces the final structured output used by the UI and experiments.

### Key function

```python
analyze_contract(...)
```

This function returns a structured JSON-like object containing:

```json
{
  "clauses": [...],
  "contract_risk": {...},
  "missing_clauses": [...],
  "doc_flags": [...]
}
```

---

# `segment.py`

This module performs **clause segmentation**.

Contracts often contain structured headings such as:

```
1. Confidentiality

2. Term

3. Governing Law
```

The segmentation algorithm detects clause boundaries using:

1. numbered headings  
2. ALL CAPS section titles  
3. blank line heuristics  

Example:

```
1.
Confidentiality
The receiving party shall keep information confidential.

2.
Term
This agreement remains valid for five years.
```

This becomes:

```
Clause c001
Clause c002
```

The output structure is defined using the `Clause` dataclass.

---

# `classify.py`

This module classifies clauses into a predefined **contract clause taxonomy**.

Two classification approaches are supported:

## 1. Baseline keyword classifier

A deterministic classifier based on keyword matching.

Example keywords:

```
Confidentiality
Exceptions
Term & Survival
Return / Destruction
Remedies / Injunctive Relief
Governing Law
Limitation of Liability
```

### Advantages:

- fast
- deterministic
- no external dependencies

### Limitations:

- lower semantic accuracy

---

## 2. LLM-based classifier

The system can optionally use a **large language model** to classify clauses.

The LLM receives:

- clause text  
- taxonomy labels  
- structured output requirements  

The model returns structured JSON:

```json
{
  "label": "Confidentiality",
  "confidence": 0.83,
  "rationale_short": "Clause restricts disclosure of confidential information."
}
```

If LLM output is invalid, the system automatically falls back to the baseline classifier.

---

# `rules.py`

This module implements **deterministic legal risk checks**.

Rules detect potentially problematic contract language.

## Example Rules

### Unlimited liability

Detects language suggesting uncapped liability:

```
"unlimited liability"
"without limitation"
```

### One-way confidentiality

Detects clauses where confidentiality obligations apply to only one party.

### Non-compete restrictions

Detects non-compete language that may create legal risk.

### Overbroad confidentiality definitions

Detects clauses defining confidential information too broadly.

### Injunctive relief without bond

Detects clauses allowing injunctions without bond posting.

---

Each rule returns a **Flag object** containing:

```python
Flag(
  name="unlimited_liability_language",
  severity="High",
  evidence_snippet="...",
  explanation="Language suggests uncapped liability."
)
```

---

# `rag.py`

This module implements **Retrieval-Augmented Generation (RAG)**.

The goal is to provide the LLM with examples of **similar clauses from a corpus**.

The system uses:

```
SentenceTransformers
FAISS vector index
```

### Workflow:

1. Embed clause text using a transformer model  
2. Query FAISS index  
3. Retrieve the most similar clauses  
4. Provide them as contextual evidence for the LLM  

Example retrieved passage:

```
source_id: nda_102
clause_type: Confidentiality
text: "Each party agrees not to disclose confidential information..."
```

This helps ground LLM reasoning and reduces hallucinations.

---

# `analyze.py`

This module performs **LLM-based clause analysis**.

The LLM receives:

- clause text  
- clause classification  
- retrieved examples  
- rule flags  

The model must return **strictly structured JSON** containing:

```json
{
  "plain_english_summary": "...",
  "business_risk": {...},
  "norm_deviation": {...},
  "uncertainty": {...},
  "citations": [...]
}
```

## Safety Mechanisms

### JSON extraction

LLM responses may contain extra text or formatting.  
The system extracts the valid JSON object automatically.

### Schema validation

The output is validated using **Pydantic models**.

### Automatic retries

If JSON parsing fails, the system retries with a repair prompt.

### Severity correction

Rule-based flags can upgrade LLM risk severity to ensure consistency.

---

# `coverage.py`

This module checks whether the contract contains **essential clauses**.

Required NDA clauses include:

```
Confidentiality
Definition of Confidential Information
Exceptions
Term & Survival
Return / Destruction
Remedies / Injunctive Relief
```

Missing clauses are detected and reported.

Example output:

```python
missing_clauses = [
  "Exceptions",
  "Remedies / Injunctive Relief"
]
```

---

# `text.py`

Utility module for **text normalization**.

Functions include:

- newline normalization  
- whitespace cleanup  
- removal of formatting artifacts  

This step ensures consistent input for segmentation and classification.

---

# `types.py`

Defines the core **data structures and schemas** used across the system.

## Clause

Represents a segmented clause.

```python
Clause(
  id="c001",
  raw_text="The receiving party shall...",
  start_char=120,
  end_char=360
)
```

---

## Passage

Represents a retrieved clause from the RAG corpus.

---

## Flag

Represents a rule-based risk detection result.

---

## ClauseClassification

Pydantic model for clause classification output.

---

## AnalysisJSON

Pydantic schema for the LLM clause analysis response.

---

# Risk Scoring

Clause risk severity is mapped to numeric scores:

```
Low      → 30
Medium   → 60
High     → 85
Critical → 95
```

The final **contract risk score** is computed as the weighted average of clause severities.

---

# Safety Features

The system includes several safeguards to improve reliability:

- strict JSON schema validation  
- rule-based severity upgrades  
- hallucination prevention for citations  
- fallback classification methods  
- uncertainty scoring  

These mechanisms ensure robust behavior when interacting with LLMs.

---

# Summary

The `core` module implements the **entire hybrid contract analysis engine** used in this research project.

By combining:

- deterministic rule analysis  
- semantic retrieval  
- large language model reasoning  

the system provides structured clause-level insights for contract review.
