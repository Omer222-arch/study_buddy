import os
from typing import Any

import requests
import streamlit as st

API_URL = os.getenv("STUDY_BUDDY_API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="CRAG Study Buddy", layout="centered")
st.title("CRAG Study Buddy")
st.markdown(
    "Upload PDF sources, ingest content into the local Chroma store, and ask questions over your document corpus."
)

with st.expander("API endpoint"):
    st.write(API_URL)

uploaded_file = st.file_uploader("Choose a PDF to ingest", type=["pdf"])
if uploaded_file is not None:
    if st.button("Ingest PDF"):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        try:
            response = requests.post(f"{API_URL}/ingest", files=files, timeout=120)
            response.raise_for_status()
            data = response.json()
            st.success(f"Ingested {data['ingested_chunks']} chunks from {data['file_name']}")
            st.json(data)
        except requests.RequestException as exc:
            st.error(f"Ingestion failed: {exc}")

st.markdown("---")

query = st.text_input("Ask a question about the ingested content")
top_k = st.slider("Retrieve top chunks", 1, 10, 4)
if st.button("Get Answer"):
    if not query:
        st.warning("Enter a query before asking.")
    else:
        payload = {"query": query, "top_k": top_k}
        try:
            response = requests.post(f"{API_URL}/chat", json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            st.subheader("Answer")
            st.write(data.get("answer", "No answer returned."))
            if data.get("retrieved_documents"):
                st.subheader("Retrieved Documents")
                for idx, doc in enumerate(data["retrieved_documents"], start=1):
                    st.markdown(f"**Chunk {idx}:**")
                    st.write(doc)
            if data.get("steps_taken"):
                st.subheader("Steps Taken")
                st.write(data["steps_taken"])
        except requests.RequestException as exc:
            st.error(f"Chat request failed: {exc}")
