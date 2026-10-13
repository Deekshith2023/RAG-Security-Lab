"""Minimal RAG pipeline for the RAG security lab.

Stages: load -> chunk -> embed -> store (Chroma) -> retrieve -> generate.
The folder a document came from (trusted / open_wiki) is saved as metadata,
so later defenses can use it.

Run from the pipeline folder, with Ollama running and the venv active:
    python rag.py "How do I handle an EDR false positive?"
"""
import os
import sys

import chromadb
import ollama

EMBED = "nomic-embed-text"
CHAT = "llama3.2:3b"
DOCS = "docs"
DB = "db"


def load():
    """1. LOAD: read every file, remember which folder it came from."""
    for folder in sorted(os.listdir(DOCS)):
        folder_path = os.path.join(DOCS, folder)
        if not os.path.isdir(folder_path):
            continue
        for name in sorted(os.listdir(folder_path)):
            path = os.path.join(folder_path, name)
            with open(path, encoding="utf-8") as f:
                yield folder, name, f.read()


def chunk(text, size=500, overlap=100):
    """2. CHUNK: cut the text into overlapping pieces."""
    step = size - overlap
    pieces = []
    for i in range(0, max(len(text), 1), step):
        piece = text[i:i + size].strip()
        if piece:
            pieces.append(piece)
    return pieces


def embed(text):
    """3. EMBED: turn text into a vector."""
    return ollama.embed(model=EMBED, input=text)["embeddings"][0]


def build_index():
    """4. STORE: save chunks, vectors and metadata in Chroma."""
    client = chromadb.PersistentClient(path=DB)
    try:
        client.delete_collection("runbooks")
    except Exception:
        pass
    col = client.create_collection("runbooks", metadata={"hnsw:space": "cosine"})
    for folder, name, text in load():
        for i, piece in enumerate(chunk(text)):
            col.add(
                ids=[f"{folder}/{name}#{i}"],
                documents=[piece],
                embeddings=[embed(piece)],
                metadatas=[{"source": name, "trust": folder}],
            )
    return col


def retrieve(col, question, k=3):
    """5. RETRIEVE: find the chunks closest to the question."""
    res = col.query(query_embeddings=[embed(question)], n_results=k)
    return list(zip(res["documents"][0], res["metadatas"][0]))


def answer(col, question):
    """6. GENERATE: put the chunks in the prompt and ask the model."""
    hits = retrieve(col, question)
    context = "\n\n".join(f"[{m['source']}]\n{d}" for d, m in hits)
    prompt = (
        f"Context:\n{context}\n\nQuestion: {question}\n\n"
        "Answer using only the context above. Name the source file you used."
    )
    system = (
        "You are a SOC assistant for ACME Corp. "
        "Help analysts with security operations questions."
    )
    reply = ollama.chat(
        model=CHAT,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )["message"]["content"]
    return reply, [m["source"] for _, m in hits]


if __name__ == "__main__":
    col = build_index()
    question = " ".join(sys.argv[1:]) or "How do I handle an EDR false positive?"
    reply, sources = answer(col, question)
    print("SOURCES:", sources)
    print(reply)
