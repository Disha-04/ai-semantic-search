import os
import glob
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

DATA_DIR = "data"
OUT_DIR = "artifacts"
MODEL_NAME = "all-MiniLM-L6-v2"

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    paths = sorted(glob.glob(os.path.join(DATA_DIR, "*.txt")))
    print(f"📄 Found {len(paths)} documents")

    if not paths:
        raise SystemExit("❌ No .txt files found in ./data")

    docs = []
    meta = []

    for p in paths:
        with open(p, "r", encoding="utf-8") as f:
            text = f.read().strip()
            if text:
                docs.append(text)
                meta.append({"source": os.path.basename(p)})

    if not docs:
        raise SystemExit("❌ Documents are empty")

    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(
        docs,
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype(np.float32)

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, os.path.join(OUT_DIR, "faiss.index"))

    with open(os.path.join(OUT_DIR, "docs.json"), "w") as f:
        json.dump(docs, f, indent=2)

    with open(os.path.join(OUT_DIR, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print("✅ Index built successfully")
    print("📁 Files saved in /artifacts")

if __name__ == "__main__":
    main()