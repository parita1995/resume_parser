#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# app.py
import io, json, tempfile
from pathlib import Path

import streamlit as st

# ===== import your free-only parser =====
# Save your earlier free parser as resume_parser.py (the one that calls Ollama only)
from resume_parser import parse_resume_llm, ResumeOut  # type: ignore



# In[ ]:


import os, sys, importlib, inspect
sys.path.insert(0, os.getcwd())   # ensure current dir on path

import resume_parser as rp         # import the module object
importlib.reload(rp)               # pick up edits

st.caption(f"Welcome LLM Based resume parser application")
st.caption(f"All parsing runs locally")


# In[ ]:


# ===== optional: list local Ollama models to help users pick =====
def list_ollama_models() -> list[str]:
    try:
        import ollama
        tags = ollama.list().get("models", [])
        return [m.get("model") for m in tags if m.get("model")]
    except Exception:
        return []

st.set_page_config(page_title="Resume Parser", page_icon="📄", layout="centered")
st.title("📄 Resume Parser — Local LLM")



# In[ ]:


with st.sidebar:
    st.header("Settings")
    try:
        rp.ensure_ollama()
        st.success("Ollama is reachable.")
    except Exception as e:
        st.error(str(e))
        
    local_models = list_ollama_models()
    default_model = "llama3.1:8b"
    model = st.selectbox(
        "Ollama model",
        options=([default_model] + [m for m in local_models if m != default_model]) or [default_model],
        help="Use an Ollama model you have pulled locally.",
    )
    st.caption("Tip: `ollama pull llama3.1:8b` or `phi3:mini`")

st.markdown("Upload one or many resumes. Accepted: PDF, DOCX.")

uploaded = st.file_uploader(
    "Drag and drop files or browse",
    type=["pdf", "docx"],
    accept_multiple_files=True,
)

results: list[dict] = []
if uploaded:
    btn = st.button("Parse resumes", type="primary")
    if btn:
        prog = st.progress(0, text="Parsing...")
        for i, up in enumerate(uploaded, start=1):
            suffix = ".pdf" if up.type == "application/pdf" or up.name.lower().endswith(".pdf") else ".docx"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(up.read())
                tmp_path = Path(tmp.name)

            with st.spinner(f"Parsing {up.name}"):
                import time
                t0 = time.time()
                out = rp.parse_resume_llm(tmp_path, model=model)  # <— pass selected model
                latency = round(time.time() - t0, 2)

                rec = out.model_dump()
                rec["file"] = up.name
                rec["latency_s"] = latency     # <— show latency
                results.append(rec)
            prog.progress(i / len(uploaded), text=f"Parsed {i}/{len(uploaded)}")

        prog.empty()

        st.subheader("Results")
        for rec in results:
            with st.container(border=True):
                st.markdown(f"**File:** {rec.get('file','')}")
                if "error" in rec:
                    st.error(rec["error"])
                    continue
                st.markdown(f"**Name:** {rec.get('name','')}")
                st.markdown(f"**Email:** {rec.get('email','')}")
                skills = rec.get("skills") or []
                if skills:
                    st.markdown(f"**Latency:** {rec.get('latency_s', '?')} s")
                with st.expander("Raw JSON"):
                    st.json(rec)

        if results:
            # JSONL download
            buf = io.StringIO()
            for r in results:
                buf.write(json.dumps(r, ensure_ascii=False) + "\n")
            st.download_button(
                "Download JSONL",
                buf.getvalue().encode("utf-8"),
                file_name="resume_parses.jsonl",
                mime="application/json",
            )


# In[ ]:





# In[ ]:




