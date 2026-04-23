## Semantic Resume Matcher

> An AI-powered recruitment assistant that semantically matches resumes to job descriptions using **Endee Vector Database**, sentence embeddings, and a RAG pipeline — going far beyond traditional keyword matching.

---

## Problem Statement

Traditional ATS (Applicant Tracking Systems) rely on keyword matching, which causes qualified candidates to get filtered out simply because they used different words. This project solves that by understanding the **contextual meaning** between resumes and job descriptions using vector embeddings.


## Features

 Upload multiple PDF resumes
Semantic similarity matching using Sentence Transformers
Vector storage and search powered by **Endee Vector DB**
Match score with visual progress bars
Color-coded ranking (High / Medium / Low match)
Clean Streamlit UI — no technical knowledge needed to use

---

## System Architecture

```
PDF Resumes
    │
    ▼
Text Extraction (pdf_loader.py)
    │
    ▼
Embedding Generation (SentenceTransformers: all-MiniLM-L6-v2)
    │
    ▼
Endee Vector DB (Index + Upsert)
    │
    ▼
Semantic Search (Cosine Similarity Query)
    │
    ▼
Match Score + Ranking (matcher.py)
    │
    ▼
Streamlit Dashboard (streamlit_app.py)
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Embedding Model | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Vector Database | **Endee Vector DB** |
| PDF Parsing | PyPDF2 |
| Similarity Scoring | PyTorch + Sentence Transformers |
| Language | Python 3.10+ |

---

##Project Structure

```
semantic-resume-matcher/
├── resumes/                  # Place PDF resumes here
│   ├── resume1.pdf
│   ├── resume2.pdf
│   └── resume3.pdf
├── pdf_loader.py             # PDF text extraction
├── matcher.py                # Core logic: Endee client, embeddings, matching
├── streamlit_app.py          # Streamlit UI
├── requirements.txt          # Python dependencies
└── README.md
```

---

##Setup & Running

### Prerequisites
- Python 3.8+
- Docker Desktop

### Step 1 — Start Endee Vector DB

```bash
docker run -d \
  -p 8080:8080 \
  -v ./endee-data:/data \
  --name endee-server \
  endeeio/endee-server:latest
```

Verify at: `http://localhost:8080`

### Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Run the App

```bash
streamlit run streamlit_app.py
```

Open `http://localhost:8501` in your browser.

---

## How to Use

1. **Upload Resumes** — Use the sidebar to upload one or more PDF resumes
2. **Click "Index Resumes"** — Resumes are embedded and stored in Endee
3. **Enter Job Description** — Paste any job description in the main area
4. **Click "Find Matches"** — Get ranked results with match scores instantly

---

## 🔗 Endee Vector DB Integration

This project uses Endee as its core vector database:

- Creates a **cosine similarity index** with 384 dimensions (matching `all-MiniLM-L6-v2` output)
- **Upserts** resume embeddings with metadata (filename, full text)
- Executes **semantic search queries** to retrieve the most relevant candidates
- Uses `INT8` precision for fast and memory-efficient search

```python
client.create_index(
    name="resume_index",
    dimension=384,
    space_type="cosine",
    precision=Precision.INT8,
)
```

---

## Sample Output

```
#1  resume2.pdf  —  Score: 0.71  🟢 High Match
#2  resume1.pdf  —  Score: 0.43  🟡 Medium Match  
#3  resume3.pdf  —  Score: 0.28  🔴 Low Match
```

---

## requirements.txt

```
endee
streamlit
sentence-transformers
PyPDF2
torch
python-dotenv
```

---

## Acknowledgements

- [Endee Vector Database](https://github.com/endee-io/endee) — high-performance open source vector DB
- [Sentence Transformers](https://www.sbert.net/) — state-of-the-art sentence embeddings
- [Streamlit](https://streamlit.io/) — rapid UI development for ML apps
