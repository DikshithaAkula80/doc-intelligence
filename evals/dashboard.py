import streamlit as st
import json
import glob
import pandas as pd

st.set_page_config(page_title="Eval Dashboard", page_icon="📊", layout="wide")
st.title("📊 Evaluation Dashboard")

files = sorted(glob.glob("evals/results_*.json"), reverse=True)

if not files:
    st.warning("No eval results yet. Run `python evals/run_eval.py` first.")
    st.stop()

selected = st.selectbox("Select eval run", files)

with open(selected) as f:
    results = json.load(f)

df = pd.DataFrame(results)

col1, col2, col3 = st.columns(3)
col1.metric("Avg Keyword Score", f"{df['keyword_score'].mean():.2f}")
col2.metric("Avg Citation Score", f"{df['citation_score'].mean():.2f}")
col3.metric("Avg Judge Score", f"{df['judge_score'].mean():.2f}")

st.subheader("Per-question breakdown")
st.dataframe(df[["question", "keyword_score", "citation_score", "judge_score"]], use_container_width=True)

st.subheader("Score distribution")
st.bar_chart(df[["keyword_score", "citation_score", "judge_score"]])
