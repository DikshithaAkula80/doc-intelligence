import streamlit as st
import requests
import json

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Document Intelligence", page_icon="📄", layout="wide")
st.title("📄 Document Intelligence")
st.caption("Upload a PDF or Word doc, then ask questions about it.")

with st.sidebar:
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])
    if uploaded_file and st.button("Ingest Document", type="primary"):
        with st.spinner("Processing document..."):
            response = requests.post(
                f"{API_URL}/ingest",
                files={"file": (uploaded_file.name, uploaded_file.getvalue())}
            )
            if response.status_code == 200:
                data = response.json()
                st.success(f"✓ Ingested {data['total_chunks']} chunks")
                st.json(data["breakdown"])
                st.session_state["doc_ready"] = True
            else:
                st.error(response.json().get("detail", "Ingestion failed"))

st.header("Ask a Question")
question = st.text_input("Type your question here", placeholder="What is this document about?")

if st.button("Get Answer", type="primary") and question:
    with st.spinner("Searching and generating answer..."):
        response = requests.post(
            f"{API_URL}/query",
            json={"question": question}
        )
        if response.status_code == 200:
            data = response.json()
            st.subheader("Answer")
            st.write(data["answer"])
            st.subheader("Sources")
            for i, cite in enumerate(data["citations"], 1):
                st.caption(f"{i}. {cite['source_file']} — page {cite['page']} {('· ' + cite['section']) if cite['section'] else ''}")
        else:
            st.error("Query failed. Make sure a document is ingested first.")
