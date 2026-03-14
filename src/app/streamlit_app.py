import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

import json
import streamlit as st

from src.core.pipeline import analyze_contract
from src.core.rag import RAGConfig
from src.core.disclaimers import DISCLAIMER_BANNER
from src.llm.openrouter_client import OpenRouterClient


@st.cache_resource
def load_llm():
    return OpenRouterClient()


st.set_page_config(page_title="Corporate Lawyer AI Assistant", layout="wide")

st.title("Corporate Lawyer AI Assistant")
st.caption(DISCLAIMER_BANNER)

st.info("Decision support only. Verify with qualified counsel before acting.")

with st.spinner("Connecting to LLM..."):
    llm_client = load_llm()

st.success("LLM ready")

st.divider()


contract_text = st.text_area("Paste contract text", height=300)

colA, colB, colC, colD = st.columns(4)

use_llm_classification = colA.checkbox("LLM classification", value=True)
use_rag = colB.checkbox("RAG retrieval", value=True)
use_rules = colC.checkbox("Rule checks", value=True)
use_llm_analysis = colD.checkbox("LLM analysis", value=True)

analyze_btn = st.button("Analyze", type="primary")

rag_cfg = RAGConfig(
    index_path="indices/faiss.index",
    metadata_path="indices/faiss_meta.pkl"
)


if analyze_btn:

    if not contract_text.strip():
        st.warning("Paste contract text first.")
        st.stop()

    with st.spinner("Analyzing contract..."):

        result = analyze_contract(
            raw_text=contract_text,
            llm=llm_client if use_llm_analysis else None,
            rag_cfg=rag_cfg,
            use_llm_classification=use_llm_classification,
            use_rag=use_rag,
            use_rules=use_rules,
            use_llm_analysis=use_llm_analysis
        )

    st.success("Analysis complete")

    # Contract Risk Score

    st.subheader("Overall Contract Risk")

    st.metric(
        "Risk Score",
        f"{result['contract_risk']['score']} / 100",
        result["contract_risk"]["level"]
    )

    # Missing clauses

    if result["missing_clauses"]:

        st.warning("Missing Recommended Clauses")

        for c in result["missing_clauses"]:
            st.write("-", c)

    # Document flags

    if result.get("doc_flags"):
        st.subheader("Document-level flags")

        for f in result["doc_flags"]:
            st.warning(f"{f['name']} ({f['severity']}): {f['explanation']}")

    # Clause table

    st.subheader("Clause summary")

    rows = []

    for item in result["clauses"]:

        analysis = item["analysis"]

        rows.append({
            "Clause": item["clause"]["id"],
            "Type": analysis.get("clause_type"),
            "Severity": analysis.get("business_risk", {}).get("severity"),
            "Deviation": analysis.get("norm_deviation", {}).get("deviates"),
            "Confidence": analysis.get("uncertainty", {}).get("confidence")
        })

    st.dataframe(rows, use_container_width=True)

    # Clause details

    for item in result["clauses"]:

        with st.expander(f"Details: {item['clause']['id']}"):

            st.markdown("### Clause Text")
            st.write(item["clause"]["text"])

            if item.get("flags"):

                st.markdown("### Rule flags")

                for f in item["flags"]:

                    st.write(
                        f"{f['name']} ({f['severity']}): {f['explanation']}"
                    )

                    st.caption(f"Evidence: {f['evidence_snippet']}")

            st.markdown("### Analysis JSON")

            st.code(
                json.dumps(item["analysis"], indent=2),
                language="json"
            )

    st.download_button(
        "Download JSON",
        data=json.dumps(result, indent=2).encode("utf-8"),
        file_name="analysis_results.json",
        mime="application/json"
    )
