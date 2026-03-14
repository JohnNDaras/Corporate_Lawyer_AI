# Corporate Lawyer AI Assistant
### Hybrid AI System for Contract Risk Analysis and Compliance

This project presents a **hybrid AI system for automated contract analysis**, combining deterministic legal rules, retrieval-augmented generation (RAG), and large language model reasoning.

The system analyzes legal agreements (such as NDAs and confidentiality agreements) and produces **clause-level insights**, including:

- clause classification  
- risk scoring  
- deviation detection  
- plain-English summaries  
- uncertainty estimates  

The system is designed as a **decision-support tool** to assist legal professionals in reviewing contracts.

> ⚠️ Not legal advice. Educational decision support only.

---

# System Architecture

The architecture integrates symbolic reasoning with modern language models.

<img src="https://github.com/user-attachments/assets/007f1cea-dcb9-4bc7-a471-2c9667d50484" width="500">

The pipeline operates as follows:

1. **Contract Normalization**  
   - cleans and standardizes raw contract text.

2. **Clause Segmentation**  
   - splits the contract into individual clauses.

3. **Clause Classification**  
   - assigns each clause a legal category.

4. **Rule Engine**  
   - deterministic legal heuristics detect risky language.

5. **Retrieval System (RAG)**  
   - similar clauses are retrieved from a corpus using FAISS.

6. **LLM Analysis**  
   - the language model produces structured clause analysis.

7. **Outputs**  
   - risk scores  
   - deviation detection  
   - summaries  
   - confidence estimates  

This hybrid design improves both **interpretability and reliability** compared to purely generative approaches.

---

# Example System Output

For each clause the system generates structured analysis:

Clause: Confidentiality  
Risk: Medium  
Deviation: True  
Confidence: 0.76  

The final output includes:

- clause-level analysis  
- document-level warnings  
- global contract risk score  
- missing recommended clauses  

Results can be exported as **structured JSON**.

---

# Experimental Results

The system was evaluated through an **ablation study comparing multiple architectures**.

<img src="experiment_results_panel.png" width="1000">

Experiments compare four configurations:

| System | Description |
|--------|-------------|
| Baseline | segmentation + heuristic classification |
| Rules Only | deterministic rule checks |
| RAG + Rules | retrieval-augmented rule system |
| Hybrid (Full System) | rules + RAG + LLM reasoning |

Key findings:

- Hybrid architecture detects **significantly more clause deviations**  
- Risk assessments become **more nuanced**  
- Confidence estimates improve through contextual grounding  

These results demonstrate the advantages of combining:

- symbolic rules  
- semantic retrieval  
- language model reasoning  

---

# Features

## Clause Classification

Classifies contract clauses into a legal taxonomy:

- Confidentiality  
- Exceptions  
- Term & Survival  
- Governing Law  
- Dispute Resolution  
- Limitation of Liability  
- IP Ownership  
- Termination  
- Miscellaneous  

## Rule-Based Risk Detection

The rule engine detects patterns such as:

- unlimited liability  
- non-compete clauses  
- overbroad confidentiality definitions  
- missing governing law  

Rules provide **transparent and explainable signals**.

## Retrieval-Augmented Analysis

The system retrieves similar clauses from a corpus using **vector similarity search**.

Technology:

- SentenceTransformers  
- FAISS vector index  

Retrieved clauses provide **contextual grounding** for the LLM.

## LLM Reasoning

A language model performs clause analysis and produces:

- plain-English explanations  
- risk reasoning  
- deviation detection  
- uncertainty estimation  

The model returns **structured JSON outputs**.

---

# Interactive Demo

The project includes a **Streamlit web application** for interactive analysis.

Run the demo:

```
streamlit run src/app/streamlit_app.py
```

The interface allows users to:

- paste contract text  
- enable/disable system components  
- inspect clause analysis  
- download results as JSON  

---

# Installation

Clone the repository:

```
git clone https://github.com/JohnNDaras/Corporate_Lawyer_AI.git
cd corporate-lawyer-ai-assistant
```

Install dependencies:

```
pip install -r requirements.txt
```

Set the OpenRouter API key:

```
export OPENROUTER_API_KEY=your_api_key
```

---

# Running the System

## Run the Streamlit Application

```
streamlit run src/app/streamlit_app.py
```

---

## Run Experiments

```
python src/experiments/run_experiments.py
```

This script:

- processes contracts  
- runs multiple system configurations  
- saves results in JSON  
- generates experiment summary CSV  

---

## Build Retrieval Corpus Index

```
python src/scripts/build_corpus_index.py
```

This builds the FAISS index used by the RAG system.

---

# Repository Structure

```
project/
│
├── src/
│   ├── core/
│   │   Contract analysis pipeline
│   │   segmentation, rules, RAG, analysis
│   │
│   ├── llm/
│   │   LLM client adapters
│   │
│   ├── experiments/
│   │   experimental evaluation scripts
│   │
│   ├── scripts/
│   │   utilities for corpus building and evaluation
│   │
│   └── app/
│       Streamlit interactive interface
│
├── data/
│   contracts and clause corpus
│
├── indices/
│   FAISS retrieval index
│
├── results/
│   experiment outputs
│
└── README.md
```

Detailed documentation for each component is provided in the respective directories:

- `src/core/README.md`  
- `src/llm/README.md`  
- `src/scripts/README.md`  
- `src/experiments/README.md`  
- `src/app/README.md`  

---

# Research Context

This project explores **hybrid AI architectures for legal document analysis**.

Traditional rule-based systems struggle with linguistic variability, while purely generative models may hallucinate or lack grounding.

The proposed architecture integrates:

- deterministic legal rules  
- retrieval-augmented grounding  
- language model reasoning  

This combination improves both **accuracy and interpretability**.

---

# Limitations

The system currently focuses on:

- confidentiality agreements  
- non-disclosure agreements  

Future work may extend the system to:

- vendor contracts  
- employment agreements  
- corporate governance documents  

---

# Future Work

Potential extensions include:

- larger legal corpora  
- more advanced retrieval techniques  
- fine-tuned legal language models  
- multi-document contract comparison  

---

# Disclaimer

This system is intended for **educational and research purposes only**.

It does **not provide legal advice** and should not replace professional legal review.

---

# License

MIT License
