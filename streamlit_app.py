import streamlit as st
import tempfile
import os
from matcher import setup_index, ingest_resumes, match_resumes

# ── page config ─────────────────────────────────────────────
st.set_page_config(
    page_title="Semantic Resume Matcher",
    page_icon="🔍",
    layout="centered",
)

# ── minimal custom CSS ──────────────────────────────────────
st.markdown("""
<style>
    .main { max-width: 760px; }
    .score-pill {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .high   { background: #d1fae5; color: #065f46; }
    .medium { background: #fef3c7; color: #92400e; }
    .low    { background: #fee2e2; color: #991b1b; }
</style>
""", unsafe_allow_html=True)

# ── header ───────────────────────────────────────────────────
st.title("🔍 Semantic Resume Matcher")
st.caption("Upload resumes, paste a job description — get ranked matches instantly.")
st.divider()

# ── session state ────────────────────────────────────────────
if "indexed" not in st.session_state:
    st.session_state.indexed = False
if "resume_names" not in st.session_state:
    st.session_state.resume_names = []

# ── sidebar: upload resumes ──────────────────────────────────
with st.sidebar:
    st.header("📄 Step 1 — Upload Resumes")
    uploaded_files = st.file_uploader(
        "Upload PDF resumes",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        if st.button("⚡ Index Resumes", use_container_width=True, type="primary"):
            with st.spinner("Setting up Endee index..."):
                setup_index()

            pdf_paths = []
            with tempfile.TemporaryDirectory() as tmpdir:
                for f in uploaded_files:
                    path = os.path.join(tmpdir, f.name)
                    with open(path, "wb") as out:
                        out.write(f.read())
                    pdf_paths.append(path)

                with st.spinner(f"Embedding {len(pdf_paths)} resume(s)..."):
                    count = ingest_resumes(pdf_paths)

            st.session_state.indexed = True
            st.session_state.resume_names = [f.name for f in uploaded_files]
            st.success(f"✅ {count} resume(s) indexed!")

    if st.session_state.indexed:
        st.markdown("**Indexed resumes:**")
        for name in st.session_state.resume_names:
            st.markdown(f"- 📄 {name}")

# ── main area: job description + results ─────────────────────
st.subheader("📝 Step 2 — Enter Job Description")
job_desc = st.text_area(
    label="Job description",
    placeholder="e.g. Looking for an AI Engineer with NLP, Python, and vector database experience...",
    height=160,
    label_visibility="collapsed",
)

top_k = st.slider("Number of top matches to show", min_value=1, max_value=5, value=3)

run_btn = st.button("🚀 Find Matches", type="primary", use_container_width=True)

st.divider()

# ── results ──────────────────────────────────────────────────
if run_btn:
    if not st.session_state.indexed:
        st.warning("⚠️ Please upload and index resumes first (sidebar).")
    elif not job_desc.strip():
        st.warning("⚠️ Please enter a job description.")
    else:
        with st.spinner("Searching..."):
            matches = match_resumes(job_desc, top_k=top_k)

        st.subheader(f"🏆 Top {len(matches)} Matches")

        for m in matches:
            score = m["score"]
            if score >= 0.5:
                pill_class = "high"
                emoji = "🟢"
            elif score >= 0.35:
                pill_class = "medium"
                emoji = "🟡"
            else:
                pill_class = "low"
                emoji = "🔴"

            with st.expander(
                f"{emoji}  #{m['rank']}  {m['filename']}  —  score: {score}",
                expanded=(m["rank"] == 1),
            ):
                score_pct = int(score * 100)
                st.progress(score_pct, text=f"Match score: {score_pct}%")

                st.markdown("**Resume preview:**")
                st.markdown(
                    f"<div style='background:#f8fafc;padding:12px;border-radius:8px;"
                    f"font-size:0.88rem;color:#334155;line-height:1.6'>{m['preview']}...</div>",
                    unsafe_allow_html=True,
                )

                with st.expander("Show full resume text"):
                    st.text(m["full_text"])