import json
import numpy as np
import faiss
import streamlit as st
from sentence_transformers import SentenceTransformer

OUT_DIR = "artifacts"
MODEL_NAME = "all-MiniLM-L6-v2"

st.set_page_config(page_title="AI Semantic Search", page_icon="🔎", layout="wide")

@st.cache_resource
def load_model():
    return SentenceTransformer(MODEL_NAME)

@st.cache_resource
def load_data():
    index = faiss.read_index(f"{OUT_DIR}/faiss.index")
    docs = json.load(open(f"{OUT_DIR}/docs.json", "r", encoding="utf-8"))
    meta = json.load(open(f"{OUT_DIR}/meta.json", "r", encoding="utf-8"))
    return index, docs, meta

def snippet(text, n=280):
    t = " ".join(text.strip().split())
    return t if len(t) <= n else t[:n] + "…"

st.title("🔎 AI Semantic Search Engine")
st.caption("Search documents by meaning using embeddings + FAISS.")

query = st.text_input("", placeholder="Ask anything… e.g. 'ETL automation and dashboards'")
top_k = st.slider("Top results", 1, 10, 5)

model = load_model()
index, docs, meta = load_data()

if query:
    q_emb = model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)
    scores, ids = index.search(q_emb, top_k)

    st.subheader("Results")
    for rank, (score, idx) in enumerate(zip(scores[0], ids[0]), 1):
        st.markdown(f"**{rank}. {meta[idx]['source']}** — score `{score:.3f}`")
        st.write(snippet(docs[idx]))
        st.divider()
else:
    st.info("Type a query to search your documents.")