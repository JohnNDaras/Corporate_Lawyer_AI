# Streamlit Application

This directory contains the **interactive web application** used to demonstrate the contract analysis system.

The application provides a user-friendly interface that allows users to:

- paste contract text  
- run automated contract analysis  
- inspect clause-level results  
- view detected risks  
- download structured JSON outputs  

The interface is implemented using **Streamlit** and serves as a **demonstration layer on top of the core analysis pipeline**.

---

# Application Overview

The Streamlit app connects the user interface to the hybrid contract analysis pipeline.

```
User Interface (Streamlit)
        │
        ▼
Contract Input
        │
        ▼
Analysis Pipeline (src/core)
        │
        ├── Clause Classification
        ├── Rule Checks
        ├── RAG Retrieval
        └── LLM Reasoning
        ▼
Structured Contract Analysis
        │
        ▼
Interactive Results Display
```

This allows users to explore the behavior of the system in real time.

---

# File Structure

```
src/app/
│
└── streamlit_app.py
```

The entire application is implemented in a single Streamlit script.

---

# Running the Application

To start the interface:

```bash
streamlit run src/app/streamlit_app.py
```

The application will open in the browser, typically at:

```
http://localhost:8501
```

---

# Interface Components

The application provides several interactive components.

---

## Contract Input

Users can paste contract text into the main input area.

Example input:

```
Paste contract text here...
```

The system supports:

- NDAs  
- confidentiality agreements  
- vendor contracts  
- general legal agreements  

---

## Analysis Controls

Users can enable or disable system components to experiment with the architecture.

| Option              | Description                                   |
|---------------------|-----------------------------------------------|
| LLM classification  | Uses an LLM to classify clauses               |
| RAG retrieval       | Retrieves similar clauses from the corpus     |
| Rule checks         | Applies deterministic legal rules             |
| LLM analysis        | Generates detailed clause reasoning           |

This allows users to **simulate ablation experiments interactively**.

---

# Example Configuration

## Full Hybrid System

```
LLM classification ✔
RAG retrieval ✔
Rule checks ✔
LLM analysis ✔
```

## Minimal Baseline

```
LLM classification ✖
RAG retrieval ✖
Rule checks ✖
LLM analysis ✖
```

---

# Contract Analysis Output

After clicking **Analyze**, the system processes the contract and returns structured results.

The application displays:

1. **Overall contract risk score**  
2. **Missing recommended clauses**  
3. **Document-level rule warnings**  
4. **Clause-level analysis**  

---

# Contract Risk Score

The system computes a global contract risk score:

```
Risk Score: 48 / 100
Risk Level: Medium
```

This score is derived from aggregated clause risk assessments.

---

# Missing Clauses

The system detects whether recommended clauses are absent.

Example:

```
Missing Recommended Clauses

- Return / Destruction
- Remedies / Injunctive Relief
```

---

# Document-Level Flags

Certain risks are detected at the **document level**.

Example:

```
missing_governing_law (Medium):
No governing law detected; may increase dispute uncertainty.
```

---

# Clause Summary Table

The interface displays a summary table showing clause-level metrics.

Example:

| Clause | Type              | Severity | Deviation | Confidence |
|--------|-------------------|----------|-----------|------------|
| c001   | Confidentiality   | Low      | False     | 0.72       |
| c002   | Exceptions        | Medium   | True      | 0.63       |

This table provides a quick overview of contract risks.

---

# Clause-Level Details

Each clause can be expanded to view detailed analysis.

The interface displays:

- the clause text  
- rule-based flags  
- supporting evidence  
- full analysis JSON  

Example:

```
Clause ID: c003
Type: Confidentiality
Severity: Medium
Deviation: True
```

The full structured output is also displayed.

---

# JSON Export

Users can download the analysis results as a JSON file.

Example output file:

```
analysis_results.json
```

This file contains:

```json
{
  "contract_risk": {...},
  "missing_clauses": [...],
  "clauses": [...]
}
```

This makes the system suitable for integration into other applications.

---

# LLM Initialization

The application connects to the language model during startup.

```
Connecting to LLM...
LLM ready
```

The system currently uses:

```
OpenRouterClient
```

Default model:

```
meta-llama/llama-3-8b-instruct
```

---

# Disclaimer

The application prominently displays the disclaimer:

```
Not legal advice.
Educational decision support only.
No attorney-client relationship is formed.
```

This ensures responsible use of AI-generated legal analysis.

---

# Purpose of the Application

The Streamlit interface was designed to:

- demonstrate the capabilities of the hybrid contract analysis system  
- allow interactive exploration of clause-level outputs  
- support presentations and research demonstrations  
- provide a prototype interface for legal AI tools  

The application is intended for **research and demonstration purposes only**.

---

# Integration with the Research Paper

The application demonstrates the architecture described in the research paper.

Specifically, it showcases the integration of:

- deterministic legal rules  
- retrieval-augmented generation  
- large language model reasoning  

Together these components form the **hybrid contract analysis system evaluated in the experiments**.
