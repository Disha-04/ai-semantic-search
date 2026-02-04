import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

INDEX_PATH = "artifacts/faiss.index"
DOCS_PATH = "artifacts/docs.json"
MODEL_NAME = "all-MiniLM-L6-v2"

def main():
    print("🔍 Semantic Search Ready")
    print("Type a query and press Enter (type 'exit' to quit)\n")

    index = faiss.read_index(INDEX_PATH)

    with open(DOCS_PATH, "r", encoding="utf-8") as f:
        docs = json.load(f)

    model = SentenceTransformer(MODEL_NAME)

    while True:
        query = input("Query: ").strip()
        if query.lower() in {"exit", "quit"}:
            print("👋 Exiting search")
            break

        q_emb = model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)
        scores, ids = index.search(q_emb, 3)

        print("\nTop results:")
        for rank, idx in enumerate(ids[0], start=1):
            preview = docs[idx][:160] + ("..." if len(docs[idx]) > 160 else "")
            print(f"{rank}. {preview}")
        print()

if __name__ == "__main__":
    main()