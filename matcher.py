from endee import Endee, Precision
from sentence_transformers import SentenceTransformer, util
import torch
import os

# ── constants ──────────────────────────────────────────────
INDEX_NAME = "resume_index"
MODEL_NAME = "all-MiniLM-L6-v2"
RESUME_FOLDER = "resumes"

# ── singletons (loaded once) ────────────────────────────────
_client = None
_model = None
_index = None


def get_client():
    global _client
    if _client is None:
        _client = Endee(token="l3uo1dzs:CQ2xTA7sKCMX9n6X6A7Ey1BOR37zaaUC:as1")
    return _client


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def get_index():
    global _index
    if _index is None:
        _index = get_client().get_index(INDEX_NAME)
    return _index


# ── setup ───────────────────────────────────────────────────
def setup_index():
    """Delete old index (if any) and create a fresh one."""
    client = get_client()
    try:
        client.delete_index(INDEX_NAME)
    except Exception:
        pass
    client.create_index(
        name=INDEX_NAME,
        dimension=384,
        space_type="cosine",
        precision=Precision.INT8,
    )
    global _index
    _index = client.get_index(INDEX_NAME)
    return _index


# ── ingestion ───────────────────────────────────────────────
def ingest_resumes(pdf_paths: list[str]) -> int:
    """Embed and upsert a list of PDF file paths into Endee."""
    from pdf_loader import extract_text

    model = get_model()
    index = get_index()
    count = 0

    for path in pdf_paths:
        filename = os.path.basename(path)
        text = extract_text(path)
        if not text.strip():
            continue
        vector = model.encode(text).tolist()
        index.upsert([{
            "id": filename,
            "vector": vector,
            "meta": {"resume": text, "filename": filename},
        }])
        count += 1

    return count


# ── matching ────────────────────────────────────────────────
def match_resumes(job_description: str, top_k: int = 3) -> list[dict]:
    """Return top-k resumes ranked by cosine similarity to job_description."""
    model = get_model()
    index = get_index()

    query_vector = model.encode(job_description).tolist()
    results = index.query(vector=query_vector, top_k=top_k)

    output = []
    for rank, match in enumerate(results, start=1):
        resume_text = match["meta"]["resume"]
        resume_vector = model.encode(resume_text)
        score = util.cos_sim(
            torch.tensor(query_vector),
            torch.tensor(resume_vector),
        ).item()
        output.append({
            "rank": rank,
            "filename": match["meta"].get("filename", match["id"]),
            "score": round(score, 4),
            "preview": resume_text[:300],
            "full_text": resume_text,
        })

    output.sort(key=lambda x: x["score"], reverse=True)
    return output